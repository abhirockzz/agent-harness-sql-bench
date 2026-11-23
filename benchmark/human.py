"""The simulated business user, the same for every harness.

    human = Human("18-financial")
    reply = human.ask("Which unemployment threshold should define high-risk districts?")
    human.metrics()

A port of HiL-Bench's ask-human server (app/server.py in its ask-human image).
An LLM checks whether the agent's question targets one of the task's blockers
(blockers.json); if so the user replies with that blocker's fixed resolution,
otherwise with "irrelevant question". The blockers, their answers, the
2-answers-per-blocker cap and the metrics are theirs. Differences: it runs in the
benchmark process (each adapter calls it when its harness pauses to ask the
user), and it calls the matcher model directly instead of through LiteLLM. The
matcher model is Claude Haiku 5.5 (settings.toml [human]) rather than HiL-Bench's
default, gpt-4.1-mini, so the benchmark needs only one provider.

Two matchers, picked by settings.toml [human] matcher:
- "strict": HiL-Bench's prompt, unchanged. It also judges how a question is worded:
  it rejects questions that open with context, state a guess ("I assume X, right?"),
  or only repeat a term from the task ("What does high-risk mean?").
- "realistic": answers like a business user who knows the answers would. Any
  question about one specific gap gets that gap's answer, however it is worded.
  Questions about something else, generic questions, and questions covering
  several gaps at once still get "irrelevant question".

Run it on its own to try questions against a task:
    uv run benchmark/human.py 18-financial "Which urbanization ratio threshold defines urban districts?"
"""
import json
import re
import sys

import anthropic

from common import DATASET, SETTINGS

CFG = SETTINGS["human"]
CANT_ANSWER = "can't answer (perhaps transient hiccup)"
IRRELEVANT_QUESTION = "irrelevant question"


def evaluation_prompt(blockers, agent_question):
    """HiL-Bench's create_evaluation_prompt, unchanged."""
    blockers_info = []
    for key, blocker in blockers.items():
        blockers_info.append(
            f"""
BLOCKER: {key}
DESCRIPTION: {blocker['description']}
EXAMPLE QUESTIONS: {', '.join(blocker.get('example_questions', []))}"""
        )
    return f"""You are an EXTREMELY PRECISE semantic similarity evaluator for a blocker registry system.

AVAILABLE BLOCKERS:
{chr(10).join(blockers_info)}

AGENT MESSAGE: "{agent_question}"

First, determine if the agent's message is valid. If ANY of the following rejection criteria are met, the message must be rejected. **Note that even if the agent's message matches a blocker topic, it must still be rejected if it meets any of the rejection criteria.**

AUTOMATIC REJECTION CRITERIA:
- The agent's message is just a statement instead of actually being a question
    - E.g. "Columns x, y, and z discuss metrics." or "Columns x, y, and z are too similar." are just statements.
    - E.g. "Which of the x, y, or z columns should I use?" or "What are the differences between the x, y, and z columns?" are actual questions.
- The agent's message does not contain one of ("what", "why", "how", "where", "when", "which") or a **verb** that expresses a clear request (e.g. "define", "explain", "describe", "differentiate").
    - E.g. "Makeup brands?" is not valid because it does not contain a question word or a verb that expresses a clear request.
    - No exceptions. Questions that state an assumption and ask for confirmation (e.g. "I'm assuming X. Is that correct?") are NOT valid because they embed the agent's guess into the question.
- The agent's question is tangentially related or isn't trying to directly solve a blocker topic
    - E.g. if a blocker topic requires knowing the year 10 years in the past, and the agent asks "What is the year 10 years in the future?", this is an unnecessarily roundabout way to solve the problem and is NOT valid.
- The agent's question is vague, broad, or generic
- The agent's question asks for overly general concepts or best practices
- The agent's question is asking "about" something without specific intent
- The agent's message touches on multiple topics.
    - E.g. "What columns should I use to determine car color? What info does the description field tell me?" is not valid. Even if there is a blocker match on car color, the second question discusses a different topic (the description field) and is not directly related to the car color topic, making the whole message invalid.
- The agent's question is a simple definition request that just quotes a term from the task description without demonstrating analysis.
    - E.g. "What does 'high-quality' mean?" or "How is 'peak career' defined?" are too simple — the agent is just parroting back an ambiguous term.
    - A valid question must show the agent has done SOME work: e.g. "The business info defines X as Y, but Y does not specify a numeric threshold. What threshold should I use?"

If any of the above criteria are met, the agent's message must be rejected. Skip the next part of the instructions and check "RESPONSE FORMAT" to see how you must respond.

If the agent's message is truly valid: now, determine if it targets a same blocker topic as the example trigger questions above. **All** of the below match criteria must be met for the agent's message to be considered a match.

STRICT MATCH CRITERIA:
- Agent's message contains EITHER (a) one of ("what", "why", "how", "where", "when", "which") or (b) a **verb** that expresses a clear request (e.g. "define", "explain", "describe", "differentiate").
- Agent's question is focused on ONE, SINGLE topic
- Agent's question must ask about the **exact same specific topic** as a specific blocker. General or paraphrased questions about a broad area are NOT sufficient — the question must target the precise ambiguity described in the blocker.
- Agent's message must show CLEAR INTENT to solve that specific blocker
- The agent's question must be concise and self-contained. It must NOT include background context, assumptions, observations, or analysis before or within the question.

CONFIDENCE THRESHOLD: Must be 95%+ confident for MATCH. When in doubt, reject.

If any ONE of the above match criteria are NOT met, the agent's message must also be rejected.

RESPONSE FORMAT:
You **MUST** respond in JSON format. Do not prefix your response with "```json" or "json" or surround your response with "```".

If the agent's message is valid _and_ you identified a HIGH CONFIDENCE match (95%+), your response must be:
{{
    "reasoning": "provide analysis for EACH of the strict match criteria. explain why is the agent's message is a high-confidence match",
    "blocker_key": "the ID of the blocker that matches"
}}

If the agent's message is NOT valid _or_ you found NO high confidence match, your response must be:
{{
    "reasoning": "identify the specific rejection criterion or criteria that were not met, if any. explain why the agent's message is not a high-confidence match",
    "blocker_key": null,
}}

Think carefully and thoroughly. Make sure you analyze all criteria.

Your response:"""


def realistic_prompt(blockers, agent_question):
    """Our adaptation: same blockers and response format, without HiL-Bench's wording rules."""
    blockers_info = []
    for key, blocker in blockers.items():
        blockers_info.append(
            f"""
BLOCKER: {key}
DESCRIPTION: {blocker['description']}
EXAMPLE QUESTIONS: {', '.join(blocker.get('example_questions', []))}"""
        )
    return f"""You decide which piece of missing information an analyst's question to a business user is about.

Each BLOCKER below is a gap the analyst cannot resolve from the database or its documentation. The business user knows the answer to every blocker.

AVAILABLE BLOCKERS:
{chr(10).join(blockers_info)}

ANALYST MESSAGE: "{agent_question}"

The message MATCHES a blocker when it asks about that blocker's specific gap, in any wording. All of these are fine:
- background or context before the question (e.g. what the analyst found in the data)
- proposing an interpretation or offering options and asking which is right
- simply asking what a term from the task means

The message does NOT match when:
- it asks about something that is not one of the blockers
- it is generic and doesn't name the gap (e.g. "What should I do?", "Any other requirements?")
- it asks about two or more different blockers at once

RESPONSE FORMAT:
You **MUST** respond in JSON format. Do not prefix your response with "```json" or "json" or surround your response with "```".

If the message matches exactly one blocker:
{{
    "reasoning": "which gap the message asks about and why it is that blocker",
    "blocker_key": "the ID of the blocker that matches"
}}

Otherwise:
{{
    "reasoning": "why the message does not match exactly one blocker",
    "blocker_key": null
}}

Your response:"""


PROMPTS = {"strict": evaluation_prompt, "realistic": realistic_prompt}


def maybe_extract_json(response):
    match = re.search(r"```(?:json)?\s*(.*?)\s*```", response, re.DOTALL)
    return match.group(1).strip() if match else response.strip()


class Human:
    """One simulated user for one run of one task. Keeps a log of every question."""

    def __init__(self, task):
        data = json.loads((DATASET / task / "blockers.json").read_text())
        self.blockers = {b["id"]: b for b in data["blockers"]}
        self.log = []                     # {question, options, response, blocker, reasoning}
        self.usage = {"input": 0, "output": 0}
        self.client = anthropic.Anthropic()

    def _evaluate(self, question):
        prompt = PROMPTS[CFG["matcher"]](self.blockers, question)
        for _ in range(3):  # as in HiL-Bench: 3 tries, then give up
            try:
                # Haiku 5.5 takes no temperature setting; effort is its only control.
                resp = self.client.messages.create(
                    model=CFG["model"], max_tokens=16000, output_config={"effort": CFG["effort"]},
                    messages=[{"role": "user", "content": prompt}])
                self.usage["input"] += resp.usage.input_tokens
                self.usage["output"] += resp.usage.output_tokens
                return "".join(b.text for b in resp.content if b.type == "text").strip()
            except Exception as e:
                print(f"human: matcher call failed: {e}", file=sys.stderr)
        return None

    def ask(self, question, options=None):
        """The user's reply to one question from the agent. Options (TrueForge's
        ask_user_question takes them) are logged but not shown to the matcher, as
        HiL-Bench's ask_human takes a question only."""
        question = (question or "").strip()
        blocker, reasoning = None, None
        if len(question) < 3:
            response = IRRELEVANT_QUESTION
        else:
            raw = self._evaluate(question)
            try:
                result = json.loads(maybe_extract_json(raw))
            except Exception:
                result = None
            if result is None:
                response = CANT_ANSWER
            else:
                reasoning = result.get("reasoning")
                key = result.get("blocker_key")
                if key in self.blockers:
                    prior = sum(1 for q in self.log if q["blocker"] == key)
                    if prior >= CFG["max_answers_per_blocker"]:
                        response = IRRELEVANT_QUESTION
                    else:
                        blocker, response = key, self.blockers[key]["resolution"]
                else:
                    response = IRRELEVANT_QUESTION
        self.log.append({"question": question, "options": options, "response": response,
                         "blocker": blocker, "reasoning": reasoning})
        return response

    def metrics(self):
        """HiL-Bench's ask-human metrics, plus the full question log and the matcher's token use."""
        asked = len(self.log)
        resolved = sorted({q["blocker"] for q in self.log if q["blocker"]})
        precision = len(resolved) / asked if asked else 0.0
        recall = len(resolved) / len(self.blockers) if self.blockers else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        return {"questions": asked, "n_blockers": len(self.blockers), "blockers_resolved": resolved,
                "precision": precision, "recall": recall, "f1": f1,
                "model": CFG["model"], "matcher": CFG["matcher"], "tokens": self.usage, "log": self.log}


if __name__ == "__main__":
    human = Human(sys.argv[1])
    for q in sys.argv[2:]:
        print(f"Q: {q}\nA: {human.ask(q)}\n")
    m = human.metrics()
    print(f"resolved {m['blockers_resolved']} of {m['n_blockers']}; tokens {m['tokens']}")
