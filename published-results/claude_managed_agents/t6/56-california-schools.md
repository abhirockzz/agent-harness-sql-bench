The five schools with the lowest average Reading scores among those opened in 2000–2004 with active status are:

| School | Phone | Opened | Avg Reading |
|---|---|---|---|
| Alternatives in Action | (510) 748-4314 | 2001-09-04 | 352 |
| Latino College Preparatory Academy | (408) 729-2281 | 2001-08-28 | 367 |
| Crenshaw Arts-Technology Charter High | (323) 293-3917 | 2003-09-02 | 375 |
| LIFE Academy | (510) 534-0282 | 2001-09-04 | 378 |
| Crawford High | (619) 362-3700 | 2004-09-07 | 380 |

I made three interpretation choices, based on your answers and the schema:
- **Active status:** `StatusType = 1`. The schema only lists codes 1–4, and you confirmed 1 means Active.
- **Humanities subject:** Reading (`AvgScrRead`), which you chose as the most important subject.
- **Early 2000s:** `OpenDate` from 2000-01-01 through 2004-12-31, as you specified.

138 schools meet the criteria. The query uses only school-level SAT rows (`rtype = 'S'`), so district aggregate rows are excluded.

```sql
SELECT s.School, s.Phone, s.OpenDate, sat.AvgScrRead
FROM schools s
JOIN satscores sat ON sat.cds = s.CDSCode AND sat.rtype = 'S'
WHERE s.StatusType = 1
  AND s.OpenDate BETWEEN '2000-01-01' AND '2004-12-31'
  AND sat.AvgScrRead IS NOT NULL
ORDER BY sat.AvgScrRead ASC
LIMIT 5;
```