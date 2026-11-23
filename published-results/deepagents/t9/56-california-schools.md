The five schools with the lowest average Reading scores among those that opened 2000–2004 and have StatusType = 1 are:

| School | Phone | Avg Reading |
|---|---|---|
| Alternatives in Action | (510) 748-4314 | 352 |
| Latino College Preparatory Academy | (408) 729-2281 | 367 |
| Crenshaw Arts-Technology Charter High | (323) 293-3917 | 375 |
| LIFE Academy | (510) 534-0282 | 378 |
| Crawford High | (619) 362-3700 | 380 |

The filters were: Reading as the humanities subject, OpenDate between 2000-01-01 and 2004-12-31, and StatusType = 1. The schema does not label the StatusType codes, so the mapping of 1 to "active" came from your answer.

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