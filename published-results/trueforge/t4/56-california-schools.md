The five schools with the lowest average Reading scores among those that opened in 2000–2004 and have active district status (StatusType = 1) are:

| School | Phone | Avg Reading Score |
|---|---|---|
| Alternatives in Action | (510) 748-4314 | 352 |
| Latino College Preparatory Academy | (408) 729-2281 | 367 |
| Crenshaw Arts-Technology Charter High | (323) 293-3917 | 375 |
| LIFE Academy | (510) 534-0282 | 378 |
| Crawford High | (619) 362-3700 | 380 |

Your answers set the definitions: StatusType 1 means active, "most important subject for humanities degrees" means Reading, and "early 2000s" means OpenDate from 2000-01-01 through 2004-12-31. The StatusType codes come from the column description and your confirmation, not from a code list in the database.

```sql
SELECT s.School, s.Phone, sat.AvgScrRead AS AvgReadingScore
FROM schools s
JOIN satscores sat ON s.CDSCode = sat.cds
WHERE s.StatusType = 1
  AND s.OpenDate BETWEEN '2000-01-01' AND '2004-12-31'
  AND sat.rtype = 'S'
  AND sat.AvgScrRead IS NOT NULL
ORDER BY sat.AvgScrRead ASC
LIMIT 5;
```