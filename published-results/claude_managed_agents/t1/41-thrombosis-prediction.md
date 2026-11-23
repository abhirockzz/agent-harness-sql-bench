I found 81 patients with an LDH value above 500 whose first hospital date (Patient.Date3) falls between 1990 and 1997.

Filters used, from your answers:
- **LDH beyond normal range:** LDH > 500 in the Laboratory table.
- **"Went to the hospital":** Patient.Date3, which the business notes describe as the first hospital visit date.
- **"The many first years of the 1990s":** 1990-01-01 through 1997-12-31.

```sql
SELECT DISTINCT p.ID, p.SEX
FROM Patient p
JOIN Laboratory l ON l.ID = p.ID
WHERE l.LDH > 500
  AND p.Date3 BETWEEN '1990-01-01' AND '1997-12-31'
ORDER BY p.ID;
```