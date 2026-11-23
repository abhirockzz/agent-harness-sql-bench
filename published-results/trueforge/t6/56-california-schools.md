Five schools match. Alternatives in Action has the lowest average Reading score (352), and Crawford High has the fifth lowest (380).

| School | Phone | Opened | Avg Reading |
|---|---|---|---|
| Alternatives in Action | (510) 748-4314 | 2001-09-04 | 352 |
| Latino College Preparatory Academy | (408) 729-2281 | 2001-08-28 | 367 |
| Crenshaw Arts-Technology Charter High | (323) 293-3917 | 2003-09-02 | 375 |
| LIFE Academy | (510) 534-0282 | 2001-09-04 | 378 |
| Crawford High | (619) 362-3700 | 2004-09-07 | 380 |

I used the assumptions you confirmed: "active" is StatusType = 1, "early 2000s" is OpenDate from 2000-01-01 through 2004-12-31, and the subject is Reading (AvgScrRead). Schools with no Reading score were excluded.

```sql
SELECT s.School, s.Phone, s.OpenDate, s.StatusType, t.AvgScrRead
FROM schools s
JOIN satscores t ON s.CDSCode = t.cds
WHERE s.StatusType = 1
  AND s.OpenDate BETWEEN '2000-01-01' AND '2004-12-31'
  AND t.AvgScrRead IS NOT NULL
ORDER BY t.AvgScrRead ASC
LIMIT 5;
```