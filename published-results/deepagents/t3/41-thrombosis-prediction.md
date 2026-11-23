Using your definitions, 107 patients match. Their IDs and sexes are in the query below.

Assumptions behind the query:
- **LDH beyond normal:** any laboratory LDH value above 500.
- **Hospital visit:** `Patient.Date3`, which the notes describe as the date the patient first went to the hospital. I did not also require `Admission = '+'`.
- **Early 1990s:** Date3 from 1990-01-01 through 1997-12-31.
- **Duplicates:** `DISTINCT` returns each patient once, even with several high LDH results.

```sql
SELECT DISTINCT p.ID, p.SEX
FROM Patient p
JOIN Laboratory l ON l.ID = p.ID
WHERE l.LDH > 500
  AND p.Date3 BETWEEN '1990-01-01' AND '1997-12-31'
ORDER BY p.ID;
```