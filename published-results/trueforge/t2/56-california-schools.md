The five schools with the lowest average Reading scores among those opened 2000–2004 with StatusType 1 are below. The query ranks by AvgScrRead.

| School | Phone | Avg Reading |
|---|---|---|
| Alternatives in Action | (510) 748-4314 | 352 |
| Latino College Preparatory Academy | (408) 729-2281 | 367 |
| Crenshaw Arts-Technology Charter High | (323) 293-3917 | 375 |
| LIFE Academy | (510) 534-0282 | 378 |
| Crawford High | (619) 362-3700 | 380 |

Your answers set the filters: StatusType = 1 for "active," Reading as the humanities subject, and OpenDate from 2000-01-01 to 2004-12-31 for "early 2000s." The schema has no separate district-status column, so I used the school's StatusType. The business notes did not define the status codes, so the result depends on your answer that code 1 means active.

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