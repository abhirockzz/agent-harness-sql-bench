Fifty-one patients match. Each is an admitted patient (Admission = '+') whose hospital date (Date3) falls between 1990-01-01 and 1997-12-31, and who has at least one LDH value above 500.

Some of the results are not in the reply because the list is long. Among the first rows: 27654 (F), 57266 (M), 912147 (F), 4007151 (M).

Assumptions behind the query:
- "Went to the hospital" means Admission = '+', and the visit date is Date3, as you confirmed.
- "Beyond normal range" means LDH > 500, as you confirmed.
- "Many first years of the 1990s" means 1990 through 1997, as you confirmed.
- A patient is included if any of their LDH readings in that range is above 500. The query does not use the daily maximum or the non-numeric LDH notes.

```sql
SELECT DISTINCT p.ID, p.SEX
FROM Patient p
JOIN Laboratory l ON l.ID = p.ID
WHERE p.Admission = '+'
  AND p.Date3 BETWEEN '1990-01-01' AND '1997-12-31'
  AND l.LDH > 500;
```