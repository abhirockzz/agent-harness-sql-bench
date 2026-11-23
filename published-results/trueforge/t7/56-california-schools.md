The five schools with the lowest average Reading scores among active-status schools opened 2000–2004 are below. Alternatives in Action has the lowest score, at 352.

| School | Phone | Open date | Avg Reading |
|---|---|---|---|
| Alternatives in Action | (510) 748-4314 | 2001-09-04 | 352 |
| Latino College Preparatory Academy | (408) 729-2281 | 2001-08-28 | 367 |
| Crenshaw Arts-Technology Charter High | (323) 293-3917 | 2003-09-02 | 375 |
| LIFE Academy | (510) 534-0282 | 2001-09-04 | 378 |
| Crawford High | (619) 362-3700 | 2004-09-07 | 380 |

I took your terms as follows:
- **Active district status:** `StatusType = 1`, as you confirmed.
- **Most important humanities subject:** Reading (`AvgScrRead`), as you confirmed.
- **Early 2000s:** `OpenDate` from 2000-01-01 to 2004-12-31, as you confirmed.

I joined on `CDSCode = cds` and kept only school-level rows (`rtype = 'S'`), excluding schools with no Reading score.

```sql
SELECT s.School, s.Phone, s.OpenDate, t.AvgScrRead
FROM schools s
JOIN satscores t ON s.CDSCode = t.cds
WHERE s.StatusType = 1
  AND s.OpenDate BETWEEN '2000-01-01' AND '2004-12-31'
  AND t.AvgScrRead IS NOT NULL
  AND t.rtype = 'S'
ORDER BY t.AvgScrRead ASC
LIMIT 5;
```