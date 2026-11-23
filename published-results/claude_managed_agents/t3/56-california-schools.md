The five active schools that opened in 2000–2004 with the lowest average SAT Reading scores are:

| School | Phone | Opened | Avg Reading |
|---|---|---|---|
| Alternatives in Action | (510) 748-4314 | 2001-09-04 | 352 |
| Latino College Preparatory Academy | (408) 729-2281 | 2001-08-28 | 367 |
| Crenshaw Arts-Technology Charter High | (323) 293-3917 | 2003-09-02 | 375 |
| LIFE Academy | (510) 534-0282 | 2001-09-04 | 378 |
| Crawford High | (619) 362-3700 | 2004-09-07 | 380 |

I made three interpretive choices, confirmed with you:
- **Active district status:** `StatusType = 1`. The other codes are 2, 3 and 4.
- **Most important humanities subject:** Reading (`AvgScrRead`).
- **Early 2000s:** opened between 2000-01-01 and 2004-12-31.

Schools without a Reading score are excluded.

```sql
SELECT s.School, s.Phone, s.OpenDate, sat.AvgScrRead
FROM schools s
JOIN satscores sat ON sat.cds = s.CDSCode
WHERE s.StatusType = 1
  AND s.OpenDate BETWEEN '2000-01-01' AND '2004-12-31'
  AND sat.AvgScrRead IS NOT NULL
ORDER BY sat.AvgScrRead ASC
LIMIT 5;
```