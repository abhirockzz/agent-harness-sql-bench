The five schools with the lowest average Reading scores among those opened 2000–2004 with StatusType = 1 (Active) are:

| School | Phone | Avg Reading |
|---|---|---|
| Alternatives in Action | (510) 748-4314 | 352 |
| Latino College Preparatory Academy | (408) 729-2281 | 367 |
| Crenshaw Arts-Technology Charter High | (323) 293-3917 | 375 |
| LIFE Academy | (510) 534-0282 | 378 |
| Crawford High | (619) 362-3700 | 380 |

I took "active district status" to mean StatusType = 1, "most important subject for humanities" to mean Reading, and "early 2000s" to mean OpenDate from 2000-01-01 to 2004-12-31, as you confirmed. The schools table's StatusType is described as district status, so I applied it to each school's own row.

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