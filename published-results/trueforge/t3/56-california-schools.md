Five schools match: all have StatusType 1 (active), opened 2000–2004, and have the lowest average Reading scores (AvgScrRead).

| School | Phone | Opened | Avg Reading |
|---|---|---|---|
| Alternatives in Action | (510) 748-4314 | 2001-09-04 | 352 |
| Latino College Preparatory Academy | (408) 729-2281 | 2001-08-28 | 367 |
| Crenshaw Arts-Technology Charter High | (323) 293-3917 | 2003-09-02 | 375 |
| LIFE Academy | (510) 534-0282 | 2001-09-04 | 378 |
| Crawford High | (619) 362-3700 | 2004-09-07 | 380 |

The filter for "active district status" uses `StatusType = 1` in the `schools` table, since that column is the only status field and you confirmed code 1 means active.

```sql
SELECT s.School, s.Phone, s.OpenDate, s.StatusType, AVG(sat.AvgScrRead) AS avg_read
FROM schools s
JOIN satscores sat ON sat.cds = s.CDSCode
WHERE s.StatusType = 1
  AND s.OpenDate BETWEEN '2000-01-01' AND '2004-12-31'
  AND sat.AvgScrRead IS NOT NULL
GROUP BY s.CDSCode, s.School, s.Phone, s.OpenDate, s.StatusType
ORDER BY avg_read ASC
LIMIT 5;
```