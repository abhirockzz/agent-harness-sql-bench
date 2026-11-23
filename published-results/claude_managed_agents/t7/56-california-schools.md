These are the five schools opened 2000–2004 with active status (StatusType = 1) that have the lowest average SAT Reading scores:

| School | Phone | Opened | Avg Reading |
|---|---|---|---|
| Alternatives in Action | (510) 748-4314 | 2001-09-04 | 352 |
| Latino College Preparatory Academy | (408) 729-2281 | 2001-08-28 | 367 |
| Crenshaw Arts-Technology Charter High | (323) 293-3917 | 2003-09-02 | 375 |
| LIFE Academy | (510) 534-0282 | 2001-09-04 | 378 |
| Crawford High | (619) 362-3700 | 2004-09-07 | 380 |

I used your answers for the three ambiguous points: Reading as the humanities subject, StatusType 1 as "active", and 2000-01-01 to 2004-12-31 as "early 2000s". I also limited the join to school-level SAT rows (`rtype = 'S'`), so district aggregates are not mixed in.

```sql
SELECT s.School, s.Phone, s.OpenDate, sa.AvgScrRead
FROM schools s
JOIN satscores sa ON sa.cds = s.CDSCode AND sa.rtype = 'S'
WHERE s.StatusType = 1
  AND s.OpenDate BETWEEN '2000-01-01' AND '2004-12-31'
  AND sa.AvgScrRead IS NOT NULL
ORDER BY sa.AvgScrRead ASC
LIMIT 5;
```