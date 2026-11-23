Five schools tie on the criteria you gave. Here they are, from lowest average Reading score upward:

| School | Phone | Opened | Avg Reading |
|---|---|---|---|
| Alternatives in Action | (510) 748-4314 | 2001-09-04 | 352 |
| Latino College Preparatory Academy | (408) 729-2281 | 2001-08-28 | 367 |
| Crenshaw Arts-Technology Charter High | (323) 293-3917 | 2003-09-02 | 375 |
| LIFE Academy | (510) 534-0282 | 2001-09-04 | 378 |
| Crawford High | (619) 362-3700 | 2004-09-07 | 380 |

Your criteria were applied as follows:
- **Active status:** `StatusType = 1`. The schools table has no separate district-status column, so I used this school-level code.
- **Opened early 2000s:** `OpenDate` from 2000-01-01 through 2004-12-31.
- **Humanities subject:** Reading, using `AvgScrRead`.

```sql
SELECT s.School, s.Phone
FROM schools s
JOIN satscores sat ON sat.cds = s.CDSCode
WHERE s.StatusType = 1
  AND s.OpenDate BETWEEN '2000-01-01' AND '2004-12-31'
  AND sat.AvgScrRead IS NOT NULL
ORDER BY sat.AvgScrRead ASC
LIMIT 5;
```