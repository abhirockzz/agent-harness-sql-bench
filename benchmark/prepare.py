"""Get the task databases, pinned to the exact data the benchmark was run on.

    uv run benchmark/prepare.py

Needs Docker running. The tasks themselves (question, gaps and their answers,
answer key) are committed in benchmark/dataset/<task>/. Each task's database and
business notes live in that task's HiL-Bench Docker image under /data, and
task.json pins the image by its digest (hil-bench@sha256:...). A digest is a hash
of the image's contents, so pulling by digest always gives the same bytes. This
copies /data out of each image into data/<database>/ (git-ignored). Databases
already there are skipped.

Maintainers only: how the task folders were made, from a Harbor download
(harbor 0.27.0, `scale-ai/hil-bench-sql-ask-human`):

    uvx --from harbor==0.27.0 harbor download scale-ai/hil-bench-sql-ask-human -o <download-dir>
    uv run benchmark/prepare.py --import <download-dir>/hil-bench-sql-ask-human 18 41 56 83 97

--import copies each task's files unchanged and records its image digest in task.json.
"""
import argparse
import json
import pathlib
import shutil
import subprocess
import tomllib

from common import DATA, DATASET, task_info, tasks


def question(instruction):
    """The question, without Harbor's terminal-command boilerplate."""
    return instruction.split("Answer the following question:")[1].split("# Available Commands")[0].strip()


def import_task(download, n):
    src = pathlib.Path(download) / f"hil-bench-sql_{n}-ask_human"
    meta = tomllib.loads((src / "task.toml").read_text())
    db = meta["metadata"]["database_name"]
    out = DATASET / f"{n:02d}-{db.replace('_', '-')}"
    out.mkdir(parents=True, exist_ok=True)
    # Same opening line HiL-Bench gives the agent, then the question.
    q = question((src / "instruction.md").read_text())
    (out / "prompt.txt").write_text(f"You are working in the `{db}` database.\n\n{q}\n")
    (out / "task.json").write_text(json.dumps(
        {"hil_bench_task": n, "database": db, "docker_image": meta["environment"]["docker_image"]}, indent=2) + "\n")
    shutil.copy(src / "environment" / "ask-human-data" / "blocker_registry.json", out / "blockers.json")
    shutil.copy(src / "tests" / "ground_truth.sql", out / "ground_truth.sql")
    shutil.copy(src / "tests" / "golden_output.csv", out / "golden_output.csv")
    print(f"imported {out.name}")


def copy_data(image, dest):
    """docker pull by digest, then docker cp /data out of a stopped container."""
    if (dest / "database.sqlite").exists():
        return
    # The images are linux/amd64 only; this pulls them on any host (Docker can copy files without running them).
    subprocess.run(["docker", "pull", "--platform", "linux/amd64", "-q", image], check=True)
    container = subprocess.run(["docker", "create", "--platform", "linux/amd64", image],
                               check=True, capture_output=True, text=True).stdout.strip()
    try:
        tmp = dest.with_name(dest.name + ".tmp")
        shutil.rmtree(tmp, ignore_errors=True)
        subprocess.run(["docker", "cp", f"{container}:/data", str(tmp)], check=True)
        tmp.rename(dest)
    finally:
        subprocess.run(["docker", "rm", container], check=True, capture_output=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--import", dest="download", metavar="DOWNLOAD_DIR",
                        help="maintainers: (re)create task folders from a Harbor download")
    parser.add_argument("numbers", nargs="*", type=int, help="HiL-Bench task numbers, with --import")
    args = parser.parse_args()

    if args.download:
        for n in args.numbers:
            import_task(args.download, n)
        return

    DATA.mkdir(exist_ok=True)
    for task in tasks():
        info = task_info(task)
        copy_data(info["docker_image"], DATA / info["database"])
        size = (DATA / info["database"] / "database.sqlite").stat().st_size / 1e6
        print(f"{task}: {info['database']} ({size:.0f} MB)")


if __name__ == "__main__":
    main()
