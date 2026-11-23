Five schools meet your criteria. They are listed below from lowest to highest average Reading score, with no ties at the cutoff.

| School | Phone | Avg Reading score |
|---|---|---|
| Alternatives in Action | (510) 748-4314 | 352 |
| Latino College Preparatory Academy | (408) 729-2281 | 367 |
| Crenshaw Arts-Technology Charter High | (323) 293-3917 | 375 |
| LIFE Academy | (510) 534-0282 | 378 |
| Crawford High | (619) 362-3700 | 380 |

I used these interpretations of your terms, based on your answers:
- **Active district status:** `StatusType = 1`.
- **Most important humanities subject:** Reading (`AvgScrRead`).
- **Opened in the early 2000s:** `OpenDate` from 2000-01-01 through 2004-12-31.

Only schools with a Reading score in the SAT data are included.

```sql
SELECT s.School, s.Phone, sa.AvgScrRead, s.OpenDate, s.StatusType
FROM schools s
JOIN satscores sa ON sa.cds = s.CDSCode
WHERE s.StatusType = 1
  AND s.OpenDate BETWEEN '2000-01-01' AND '2004-12-31'
  AND sa.AvgScrRead IS NOT NULL
ORDER BY sa.AvgScrRead ASC
LIMIT 5;
```