The query returns the patients who have at least one LDH value above 500 and a Date3 (first hospital visit) between 1990-01-01 and 1997-12-31. The result has about 80 patients, which I did not count precisely. Each ID appears once.

Your answers set the filters:
- **Hospital visit:** Date3, which the column notes describe as the date a patient first went to the hospital.
- **Period:** 1990 through 1997 inclusive, as you defined "the many first years of the 1990s."
- **LDH beyond normal range:** LDH > 500.

```sql
SELECT DISTINCT p.ID, p.SEX
FROM Patient p
JOIN Laboratory l ON l.ID = p.ID
WHERE p.Date3 BETWEEN '1990-01-01' AND '1997-12-31'
  AND l.LDH > 500;
```