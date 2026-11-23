Here are the patients with LDH above 500 whose first hospital date (Date3) falls between 1990-01-01 and 1997-12-31. The query returned 81 patients, listed by ID and sex in the query output above.

Three interpretations were confirmed with you:
- **Hospital visit:** Date3, which you said is the date the patient first went to the hospital.
- **"Many first years of the 1990s":** 1990 through 1997 inclusive.
- **"Beyond normal range":** LDH > 500.

```sql
SELECT DISTINCT p.ID, p.SEX
FROM Patient p
JOIN Laboratory l ON l.ID = p.ID
WHERE l.LDH > 500
  AND p.Date3 BETWEEN '1990-01-01' AND '1997-12-31'
ORDER BY p.ID;
```