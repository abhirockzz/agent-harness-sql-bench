Among schools opened from 2000 through 2004 with active status, these five have the lowest average SAT Reading scores:

| School | Phone | Avg SAT Reading |
|---|---|---|
| Alternatives in Action | (510) 748-4314 | 352 |
| Latino College Preparatory Academy | (408) 729-2281 | 367 |
| Crenshaw Arts-Technology Charter High | (323) 293-3917 | 375 |
| LIFE Academy | (510) 534-0282 | 378 |
| Crawford High | (619) 362-3700 | 380 |

I used these interpretations:
- **Subject:** SAT Reading, as you confirmed.
- **Opened in the early 2000s:** OpenDate from 2000-01-01 through 2004-12-31, as you confirmed.
- **Active district status:** `StatusType = 1`. The column description only lists the codes 1–4 and doesn't name them. I took 1 to mean Active, which is the usual convention for this field, but I didn't confirm that with you.

The query returns 203 matching schools before the top-five cut. Each school has one SAT row, so the average is that school's own score.

```sql
SELECT s.School, s.Phone, sat.AvgScrRead
FROM schools s
JOIN satscores sat ON s.CDSCode = sat.cds
WHERE s.OpenDate BETWEEN '2000-01-01' AND '2004-12-31'
  AND s.StatusType = 1
  AND sat.AvgScrRead IS NOT NULL
ORDER BY sat.AvgScrRead ASC
LIMIT 5;
```