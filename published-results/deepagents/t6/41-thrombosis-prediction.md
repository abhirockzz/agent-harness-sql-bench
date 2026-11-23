There are 48 matching patients. Each has at least one LDH value above 500 U/L, dated 1990 to 1997, and was admitted to the hospital (Admission = '+').

I made three interpretation choices, and you confirmed two of them:
- **LDH "beyond normal range":** the schema has no reference range, so I used LDH > 500 (your choice).
- **"First years of the 1990s":** I used 1990-01-01 to 1997-12-31 (your choice).
- **"Went to the hospital":** I used the Patient table's Admission flag = '+', which the column notes define as admitted to the hospital (as opposed to outpatient '-'). I did not ask you to confirm this one.

Patients with LDH values beyond 500 U/L between 1990 and 1997 who were admitted:

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

```sql
SELECT DISTINCT p.ID, p.SEX
FROM Patient p
JOIN Laboratory l ON l.ID = p.ID
WHERE l.LDH > 500
  AND l.Date BETWEEN '1990-01-01' AND '1997-12-31'
  AND p.Admission = '+'
ORDER BY p.ID;
```