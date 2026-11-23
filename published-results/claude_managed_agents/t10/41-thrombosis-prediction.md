I found 45 patients who were admitted to hospital, had an LDH value above 500 and a first hospital visit (Date3) between 1990 and 1997. The results are the ID and sex of each:

| ID | SEX |
|---|---|
| 27654 | F |
| 57266 | M |
| 912147 | F |
| 944797 | F |
| 1078741 | F |
| 1138737 | F |
| 1673252 | F |
| 2265184 | F |
| 2395148 | F |
| 3178036 | F |
| 4007151 | M |
| 4424808 | F |
| 4466420 | F |
| 4472142 | F |
| 4618443 | M |
| 4632548 | F |
| 4634342 | F |
| 4643816 | F |
| 4649885 | F |
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

Assumptions I used, all confirmed by you except where noted:
- **LDH beyond normal range** means LDH > 500 (your answer).
- **Hospital visit** means `Admission = '+'` (admitted). I left out the 3 records coded `'+('`, which is not defined in the schema. Say if you want them included.
- **Date** is `Patient.Date3`, which you identified as the first hospital visit date.
- **"Many first years of the 1990s"** means 1990-01-01 through 1997-12-31 (your answer).

```sql
SELECT DISTINCT p.ID, p.SEX
FROM Patient p
JOIN Laboratory l ON l.ID = p.ID
WHERE p.Admission = '+'
  AND p.Date3 BETWEEN '1990-01-01' AND '1997-12-31'
  AND l.LDH > 500
ORDER BY p.ID;
```