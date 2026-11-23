The five schools are below. Each is active (StatusType 1), opened 2000–2004, and has the lowest average Reading score among those schools.

| School | Phone | Avg Reading | Opened |
|---|---|---|---|
| Alternatives in Action | (510) 748-4314 | 352 | 2001-09-04 |
| Latino College Preparatory Academy | (408) 729-2281 | 367 | 2001-08-28 |
| Crenshaw Arts-Technology Charter High | (323) 293-3917 | 375 | 2003-09-02 |
| LIFE Academy | (510) 534-0282 | 378 | 2001-09-04 |
| Crawford High | (619) 362-3700 | 380 | 2004-09-07 |

I had to confirm three things with you because the schema and business notes didn't define them: StatusType 1 is active, "most important subject for humanities" means Reading, and "early 2000s" means 2000 through 2004.

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