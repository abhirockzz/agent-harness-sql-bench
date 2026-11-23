One user matches all three criteria: **DankMasterDan**.

I applied these filters:
- **City:** `Location` contains "Los Angeles". The next Super Bowl after today (Nov 2026) is Super Bowl LXI in February 2027, which you told me to match as Los Angeles.
- **Age:** under 28, as you specified. Users with no age recorded are excluded.
- **Language:** `favorite_language = 'E'`, which you confirmed is French.

I did not filter on American Football interest. The database has no field for it, and the business notes only offer loose heuristics (past engagement with football tags, or profile mentions of the NFL), so I left that out. Adding it would narrow the list further.

```sql
SELECT DisplayName
FROM users
WHERE Location LIKE '%Los Angeles%'
  AND favorite_language = 'E'
  AND Age IS NOT NULL
  AND Age < 28;
```