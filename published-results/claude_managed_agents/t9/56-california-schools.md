The five lowest-scoring schools are below. I used Reading as the humanities subject, StatusType = 1 for "active", and OpenDate from 2000-01-01 to 2004-12-31 for "early 2000s".

| School | District | Phone | Opened | Avg Reading |
|---|---|---|---|---|
| Alternatives in Action | Alameda Unified | (510) 748-4314 | 2001-09-04 | 352 |
| Latino College Preparatory Academy | East Side Union High | (408) 729-2281 | 2001-08-28 | 367 |
| Crenshaw Arts-Technology Charter High | Los Angeles Unified | (323) 293-3917 | 2003-09-02 | 375 |
| LIFE Academy | Oakland Unified | (510) 534-0282 | 2001-09-04 | 378 |
| Crawford High | San Diego Unified | (619) 362-3700 | 2004-09-07 | 380 |

The schema does not label the StatusType codes. I took 1 to mean active, as you confirmed. That filter applies to the school's own status, not to a separate district status field, since none exists in the schema.

```sql
SELECT s.School, s.District, s.Phone, s.OpenDate, t.AvgScrRead
FROM schools s
JOIN satscores t ON t.cds = s.CDSCode
WHERE s.StatusType = 1
  AND s.OpenDate BETWEEN '2000-01-01' AND '2004-12-31'
  AND t.AvgScrRead IS NOT NULL
ORDER BY t.AvgScrRead ASC
LIMIT 5;
```