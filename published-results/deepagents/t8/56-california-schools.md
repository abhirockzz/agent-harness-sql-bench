The five schools with the lowest average Reading scores, among active schools (StatusType 1) that opened from 2000 through 2004, are:

| School | Phone | Avg Reading | Opened |
|---|---|---|---|
| Alternatives in Action | (510) 748-4314 | 352 | 2001-09-04 |
| Latino College Preparatory Academy | (408) 729-2281 | 367 | 2001-08-28 |
| Crenshaw Arts-Technology Charter High | (323) 293-3917 | 375 | 2003-09-02 |
| LIFE Academy | (510) 534-0282 | 378 | 2001-09-04 |
| Crawford High | (619) 362-3700 | 380 | 2004-09-07 |

I used the Reading average as the "most important subject", and treated StatusType = 1 as Active and 2000–2004 as "early 2000s", all as you confirmed. The query only includes schools that have a Reading score in the SAT data.

```sql
SELECT s.School, s.Phone, AVG(sat.AvgScrRead) AS avg_read, s.OpenDate, s.StatusType
FROM schools s
JOIN satscores sat ON sat.cds = s.CDSCode
WHERE s.StatusType = 1
  AND s.OpenDate BETWEEN '2000-01-01' AND '2004-12-31'
  AND sat.AvgScrRead IS NOT NULL
GROUP BY s.CDSCode, s.School, s.Phone, s.OpenDate, s.StatusType
ORDER BY avg_read ASC
LIMIT 5;
```