The query returned 80 patients with LDH above 500 whose first hospital visit (Date3) fell between 1990-01-01 and 1997-12-31. Their IDs and sex are in the query output below.

I did not filter on the `Admission` flag. Date3 is the hospital-visit date you confirmed, and it applies to every patient. If you want only patients recorded as admitted (`Admission = '+'`), add `AND p.Admission = '+'` to the query.

Assumptions:
- "Beyond normal range" means LDH > 500, as you specified.
- "The many first years of the 1990s" means 1990 through 1997 inclusive, as you specified.
- LDH values are numeric integers. Non-numeric entries are stored as NULL, so they are excluded automatically.
- A patient with several qualifying lab rows appears once.

```sql
SELECT DISTINCT p.ID, p.SEX
FROM Patient p
JOIN Laboratory l ON l.ID = p.ID
WHERE l.LDH > 500
  AND p.Date3 BETWEEN '1990-01-01' AND '1997-12-31'
ORDER BY p.ID;
```