I found 81 patients who had at least one LDH value above 500 and a hospital first-visit date (Date3) between 1990-01-01 and 1997-12-31. Each is listed once, with ID and sex.

The results start with 27654 (F), 57266 (M), 540520 (F), 912147 (F), and so on through 5452747 (F). The full list is what the query below returns.

Assumptions behind the query:
- **Hospital visit:** Date3, as you confirmed. I did not also require Admission = '+'.
- **LDH cutoff:** strictly greater than 500.
- **Period:** 1990 through 1997 inclusive.

```sql
SELECT DISTINCT p.ID, p.SEX
FROM Patient p
JOIN Laboratory l ON l.ID = p.ID
WHERE l.LDH > 500
  AND p.Date3 BETWEEN '1990-01-01' AND '1997-12-31'
ORDER BY p.ID;
```