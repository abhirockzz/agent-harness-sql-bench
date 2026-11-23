Five schools match: Alternatives in Action, Latino College Preparatory Academy, Crenshaw Arts-Technology Charter High, LIFE Academy, and Crawford High. Each has an active status, opened between 2000 and 2004, and has the lowest average Reading scores in the query.

| School | Phone | Opened | Avg Reading |
|---|---|---|---|
| Alternatives in Action | (510) 748-4314 | 2001-09-04 | 352 |
| Latino College Preparatory Academy | (408) 729-2281 | 2001-08-28 | 367 |
| Crenshaw Arts-Technology Charter High | (323) 293-3917 | 2003-09-02 | 375 |
| LIFE Academy | (510) 534-0282 | 2001-09-04 | 378 |
| Crawford High | (619) 362-3700 | 2004-09-07 | 380 |

Your answers set the filters: StatusType = 1 for "active," Reading (AvgScrRead) for the humanities subject, and OpenDate from 2000-01-01 to 2004-12-31 for "early 2000s." The query joins schools to satscores on CDSCode, and excludes schools with no Reading score.

```sql
SELECT s.School, s.Phone, s.OpenDate, s.StatusType, sat.AvgScrRead
FROM schools s
JOIN satscores sat ON s.CDSCode = sat.cds
WHERE s.StatusType = 1
  AND s.OpenDate BETWEEN '2000-01-01' AND '2004-12-31'
  AND sat.AvgScrRead IS NOT NULL
ORDER BY sat.AvgScrRead ASC
LIMIT 5;
```