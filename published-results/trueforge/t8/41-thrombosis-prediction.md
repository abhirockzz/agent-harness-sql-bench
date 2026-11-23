The query returned 80+ patients (the full list was truncated in the output). The filter is: `Date3` (the first hospital visit date) between 1990-01-01 and 1997-12-31, and an LDH value above 500 in the Laboratory table. Dates are stored as `YYYY-MM-DD` text, so the BETWEEN comparison works.

The query uses `DISTINCT` because a patient can have several LDH readings.

```sql
SELECT DISTINCT p.ID, p.SEX
FROM Patient p
JOIN Laboratory l ON l.ID = p.ID
WHERE p.Date3 BETWEEN '1990-01-01' AND '1997-12-31'
  AND l.LDH > 500
ORDER BY p.ID;
```