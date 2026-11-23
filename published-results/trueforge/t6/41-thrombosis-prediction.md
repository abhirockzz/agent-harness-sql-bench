This returns 45 patients (ID and sex) who had an LDH value above 500 and a first hospital visit date between 1990-01-01 and 1997-12-31.

How I read the request:
- **"Went to the hospital"**: `Patient.Admission = '+'` (admitted, as opposed to outpatient `-`), with the first hospital visit date taken from `Patient.Date3`, as you confirmed.
- **"Many first years of the 1990s"**: 1990 through 1997 inclusive, as you specified.
- **"LDH beyond normal range"**: `Laboratory.LDH > 500`, as you specified. A patient counts if any of their LDH results exceeds 500.
- The query uses `DISTINCT` so each patient appears once.

```sql
SELECT DISTINCT p.ID, p.SEX
FROM Patient p
JOIN Laboratory l ON l.ID = p.ID
WHERE p.Admission = '+'
  AND p.Date3 BETWEEN '1990-01-01' AND '1997-12-31'
  AND l.LDH > 500
ORDER BY p.ID;
```