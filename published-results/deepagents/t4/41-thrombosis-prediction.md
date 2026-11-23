There are 81 patients who match. Their IDs and sex are in the query below.

I made these interpretation choices:
- **LDH beyond normal range:** LDH > 500, the cutoff you gave. Any laboratory record above 500 counts, not only the daily maximum.
- **Went to the hospital:** `Patient.Date3`, which you identified as the first hospital visit date.
- **"The many first years of the 1990s":** 1990-01-01 through 1997-12-31, inclusive.

```sql
SELECT DISTINCT p.ID, p.SEX
FROM Patient p
JOIN Laboratory l ON p.ID = l.ID
WHERE l.LDH > 500
  AND p.Date3 BETWEEN '1990-01-01' AND '1997-12-31'
ORDER BY p.ID;
```