There are 81 patients who meet the criteria. Each ID appears once, and sex is F or M for all of them.

I used these definitions, which you gave me:
- **Hospital visit:** the `Date3` field, which the notes say is the date the patient first went to the hospital.
- **Period:** `Date3` from 1990-01-01 through 1997-12-31.
- **Abnormal LDH:** a numeric LDH value above 500 in the Laboratory table.

```sql
SELECT DISTINCT p.ID, p.SEX
FROM Patient p
JOIN Laboratory l ON l.ID = p.ID
WHERE p.Date3 BETWEEN '1990-01-01' AND '1997-12-31'
  AND l.LDH > 500
ORDER BY p.ID;
```