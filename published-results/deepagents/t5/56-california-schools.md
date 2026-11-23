Five schools match. Lowest average Reading scores among schools opened 2000–2004 with StatusType 1 (Active):

| School | Phone | Avg Reading | Opened |
|---|---|---|---|
| Alternatives in Action | (510) 748-4314 | 352 | 2001-09-04 |
| Latino College Preparatory Academy | (408) 729-2281 | 367 | 2001-08-28 |
| Crenshaw Arts-Technology Charter High | (323) 293-3917 | 375 | 2003-09-02 |
| LIFE Academy | (510) 534-0282 | 378 | 2001-09-04 |
| Crawford High | (619) 362-3700 | 380 | 2004-09-07 |

Your answers set the definitions: StatusType 1 is Active, "most important subject for humanities" is Reading, and early 2000s means opened 2000-01-01 through 2004-12-31. Schools with no Reading score were excluded.

```sql
SELECT s.School, s.Phone, t.AvgScrRead, s.OpenDate, s.StatusType
FROM schools s
JOIN satscores t ON s.CDSCode = t.cds
WHERE s.StatusType = 1
  AND s.OpenDate BETWEEN '2000-01-01' AND '2004-12-31'
  AND t.AvgScrRead IS NOT NULL
ORDER BY t.AvgScrRead ASC
LIMIT 5;
```