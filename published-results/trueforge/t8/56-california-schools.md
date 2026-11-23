The five active schools opened 2000–2004 with the lowest average SAT Reading scores are:

| School | Phone | Avg SAT Reading |
|---|---|---|
| Alternatives in Action | (510) 748-4314 | 352 |
| Latino College Preparatory Academy | (408) 729-2281 | 367 |
| Crenshaw Arts-Technology Charter High | (323) 293-3917 | 375 |
| LIFE Academy | (510) 534-0282 | 378 |
| Crawford High | (619) 362-3700 | 380 |

I used the following filters, based on your answers:
- **Active:** `StatusType = 1`. The schema doesn't label the codes, so this is your confirmation rather than a documented definition.
- **Opened in the early 2000s:** `OpenDate` from 2000-01-01 to 2004-12-31.
- **Humanities subject:** SAT Reading (`AvgScrRead`).

Schools without a Reading score were excluded.

```sql
SELECT s.School, s.Phone, sat.AvgScrRead
FROM schools s
JOIN satscores sat ON s.CDSCode = sat.cds
WHERE s.StatusType = 1
  AND s.OpenDate BETWEEN '2000-01-01' AND '2004-12-31'
  AND sat.AvgScrRead IS NOT NULL
ORDER BY sat.AvgScrRead ASC
LIMIT 5;
```