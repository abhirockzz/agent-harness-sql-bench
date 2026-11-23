Here are the patients with LDH above 500 whose first hospital visit (Date3) falls between 1990-01-01 and 1997-12-31. The query returns 80 patients, listed in the results above.

Assumptions I used:
- **"Beyond normal range"** means LDH > 500, as you specified.
- **"The many first years of the 1990s"** means 1990 through 1997 inclusive.
- **"Went to the hospital"** is judged by Patient.Date3, which you identified as the first hospital visit date.
- **LDH timing:** any LDH reading above 500 counts, whatever its lab date. The lab date is not restricted to the period.

```sql
SELECT DISTINCT p.ID, p.SEX
FROM Patient p
JOIN Laboratory l ON l.ID = p.ID
WHERE l.LDH > 500
  AND p.Date3 BETWEEN '1990-01-01' AND '1997-12-31'
ORDER BY p.ID;
```