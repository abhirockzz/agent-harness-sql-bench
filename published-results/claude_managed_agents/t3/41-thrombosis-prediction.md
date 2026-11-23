The query returns 48 patients: ID and sex for those admitted to the hospital with an LDH value above 500 and a first hospital date between 1990 and 1997.

I used these definitions, based on your answers and the database notes:
- **LDH beyond normal range:** LDH > 500 in the Laboratory table.
- **Went to the hospital:** `Admission` starts with `+`. This also picks up three rows coded `+(`, which I treated as admitted.
- **Date of the hospital visit:** `Patient.Date3`, which the notes describe as the date the patient first went to the hospital.
- **"The many first years of the 1990s":** 1990-01-01 through 1997-12-31.

Patients with several qualifying lab results appear once, because of `DISTINCT`.

```sql
SELECT DISTINCT p.ID, p.SEX
FROM Patient p
JOIN Laboratory l ON l.ID = p.ID
WHERE p.Admission LIKE '+%'
  AND p.Date3 BETWEEN '1990-01-01' AND '1997-12-31'
  AND l.LDH > 500
ORDER BY p.ID;
```