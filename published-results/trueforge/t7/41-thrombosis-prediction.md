Patients with LDH above 500 and a first hospital visit (Date3) between 1990-01-01 and 1997-12-31 are listed below. The query returns 94 distinct patients, and the result is the full set.

I used these definitions from your answers:
- **LDH beyond normal range:** LDH > 500 in the Laboratory table.
- **"First years of the 1990s":** 1990 through 1997 inclusive.
- **Went to the hospital:** Patient.Date3, which the business notes identify as the date the patient first went to the hospital. I did not filter on the Admission column.

```sql
SELECT DISTINCT p.ID, p.SEX
FROM Patient p
JOIN Laboratory l ON p.ID = l.ID
WHERE l.LDH > 500
  AND p.Date3 BETWEEN '1990-01-01' AND '1997-12-31';
```