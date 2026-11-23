The query returns 80 patients (ID and sex) who have at least one LDH value above 500 and a first hospital visit date (Date3) between 1990-01-01 and 1997-12-31.

I used these definitions, which you confirmed:
- **LDH beyond normal range:** LDH > 500 in the Laboratory table.
- **Went to the hospital:** Date3 is the first hospital visit date. I did not also filter on the Admission column.
- **"The many first years of the 1990s":** 1990 through 1997 inclusive.

```sql
SELECT DISTINCT p.ID, p.SEX
FROM Patient p
JOIN Laboratory l ON l.ID = p.ID
WHERE l.LDH > 500
  AND p.Date3 BETWEEN '1990-01-01' AND '1997-12-31'
ORDER BY p.ID;
```