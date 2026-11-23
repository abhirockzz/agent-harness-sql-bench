There are 48 patients who match. The list is below, and the query that produces it is at the end.

- **Hospital visits:** I used `Patient.Admission = '+'`, which the schema defines as admitted to hospital (as opposed to outpatient `-`).
- **Visit date:** I used `Laboratory.Date`, because `Patient.Date1`–`Date4` have almost no 1990s values. The schema doesn't say which date marks a hospital visit, so this is my assumption.
- **LDH threshold:** LDH > 500, as you specified. This is not a standard clinical reference range.
- **1990s window:** 1990-01-01 through 1997-12-31, as you specified.

| ID | SEX |
|---|---|
| 27654 | F |
| 57266 | M |
| 912147 | F |
| 944797 | F |
| 1078741 | F |
| 1137040 | M |
| 1138737 | F |
| 1673252 | F |
| 2265184 | F |
| 2371753 | F |
| 3178036 | F |
| 4007151 | M |
| 4424808 | F |
| 4425292 | F |
| 4466420 | F |
| 4472142 | F |
| 4618443 | M |
| 4632548 | F |
| 4634342 | F |
| 4643816 | F |
| 4649885 | F |
| 4652830 | F |
| 4790235 | F |
| 4843434 | F |
| 4861720 | F |
| 4865142 | M |
| 4878272 | F |
| 4879930 | F |
| 4894243 | F |
| 4927381 | F |
| 5064814 | F |
| 5065022 | F |
| 5093771 | F |
| 5105683 | F |
| 5115307 | F |
| 5119703 | M |
| 5123360 | F |
| 5126587 | F |
| 5164396 | F |
| 5176755 | F |
| 5181621 | M |
| 5184284 | F |
| 5296268 | F |
| 5300381 | F |
| 5302954 | F |
| 5404650 | F |
| 5405581 | F |
| 5452747 | F |

The 3 rows with the non-standard admission code `'+('` do not match the LDH and date criteria, so they don't affect the result.

```sql
SELECT DISTINCT p.ID, p.SEX
FROM Patient p
WHERE p.Admission = '+'
  AND p.ID IN (
    SELECT ID
    FROM Laboratory
    WHERE LDH > 500
      AND Date BETWEEN '1990-01-01' AND '1997-12-31'
  )
ORDER BY p.ID;
```