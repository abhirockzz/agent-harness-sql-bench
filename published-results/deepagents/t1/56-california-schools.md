Among schools that opened from 2000 through 2004 and have active status (StatusType = 1), these five have the lowest average Reading scores:

| School | Phone | Opened | Avg Reading |
|---|---|---|---|
| Alternatives in Action | (510) 748-4314 | 2001-09-04 | 352 |
| Latino College Preparatory Academy | (408) 729-2281 | 2001-08-28 | 367 |
| Crenshaw Arts-Technology Charter High | (323) 293-3917 | 2003-09-02 | 375 |
| LIFE Academy | (510) 534-0282 | 2001-09-04 | 378 |
| Crawford High | (619) 362-3700 | 2004-09-07 | 380 |

I used the definitions you gave: StatusType 1 for active, Reading for the humanities subject, and 2000-01-01 to 2004-12-31 for the early 2000s. Schools with no Reading score were excluded.

```sql
SELECT s.School, s.Phone, s.OpenDate, s.StatusType, sat.AvgScrRead
FROM schools s
JOIN satscores sat ON sat.cds = s.CDSCode
WHERE s.StatusType = 1
  AND s.OpenDate BETWEEN '2000-01-01' AND '2004-12-31'
  AND sat.AvgScrRead IS NOT NULL
ORDER BY sat.AvgScrRead ASC
LIMIT 5;
```