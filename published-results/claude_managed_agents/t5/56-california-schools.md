The five schools with the lowest average Reading scores among active schools opened in 2000–2004 are:

| School | Phone | Avg Reading score |
|---|---|---|
| Alternatives in Action | (510) 748-4314 | 352 |
| Latino College Preparatory Academy | (408) 729-2281 | 367 |
| Crenshaw Arts-Technology Charter High | (323) 293-3917 | 375 |
| LIFE Academy | (510) 534-0282 | 378 |
| Crawford High | (619) 362-3700 | 380 |

I used the definitions you confirmed: StatusType = 1 means active, "early 2000s" means OpenDate from 2000-01-01 through 2004-12-31, and Reading is the humanities subject. Schools without a Reading score are excluded.

```sql
SELECT s.School, s.Phone, AVG(q.AvgScrRead) AS avg_read
FROM schools s
JOIN satscores q ON q.cds = s.CDSCode
WHERE s.StatusType = 1
  AND s.OpenDate BETWEEN '2000-01-01' AND '2004-12-31'
  AND q.AvgScrRead IS NOT NULL
GROUP BY s.CDSCode, s.School, s.Phone
ORDER BY avg_read ASC
LIMIT 5;
```