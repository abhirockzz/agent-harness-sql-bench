The five schools with the lowest average Reading scores among early-2000s openings with active status are below. Alternatives in Action has the lowest average at 352.

| School | Phone | Avg Reading | Opened |
|---|---|---|---|
| Alternatives in Action | (510) 748-4314 | 352 | 2001-09-04 |
| Latino College Preparatory Academy | (408) 729-2281 | 367 | 2001-08-28 |
| Crenshaw Arts-Technology Charter High | (323) 293-3917 | 375 | 2003-09-02 |
| LIFE Academy | (510) 534-0282 | 378 | 2001-09-04 |
| Crawford High | (619) 362-3700 | 380 | 2004-09-07 |

Assumptions I made:
- **Subject:** Reading (AvgScrRead), as you specified.
- **Opening dates:** 2000-01-01 through 2004-12-31, as you specified.
- **Active status:** StatusType = 1. The schema only lists codes 1–4 and doesn't label them, so I took 1 as "Active" based on the usual California convention. I did not confirm this against the business notes.
- **Ties:** I did not check whether a tie at the fifth position was cut off by the limit.

```sql
SELECT s.School, s.Phone, sat.AvgScrRead, s.OpenDate, s.StatusType
FROM schools s
JOIN satscores sat ON sat.cds = s.CDSCode
WHERE s.OpenDate BETWEEN '2000-01-01' AND '2004-12-31'
  AND s.StatusType = 1
  AND sat.AvgScrRead IS NOT NULL
ORDER BY sat.AvgScrRead ASC
LIMIT 5;
```