The five schools with the lowest average Reading scores among those opened in 2000–2004 with active status are:

| School | Phone | Avg Reading |
|---|---|---|
| Alternatives in Action | (510) 748-4314 | 352 |
| Latino College Preparatory Academy | (408) 729-2281 | 367 |
| Crenshaw Arts-Technology Charter High | (323) 293-3917 | 375 |
| LIFE Academy | (510) 534-0282 | 378 |
| Crawford High | (619) 362-3700 | 380 |

I took your terms as follows:
- **Active status:** `StatusType = 1`. The schema lists only the codes 1–4, and you confirmed that 1 means Active.
- **Most important humanities subject:** Reading (`AvgScrRead`), as you confirmed.
- **Opened in the early 2000s:** `OpenDate` from 2000-01-01 through 2004-12-31, as you specified.

```sql
SELECT s.School, s.Phone
FROM schools s
JOIN satscores sat ON sat.cds = s.CDSCode AND sat.rtype = 'S'
WHERE s.StatusType = 1
  AND s.OpenDate BETWEEN '2000-01-01' AND '2004-12-31'
  AND sat.AvgScrRead IS NOT NULL
ORDER BY sat.AvgScrRead ASC
LIMIT 5
```