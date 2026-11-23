One user matches: **DankMasterDan**.

I applied these filters, based on your answers:
- **City:** Location contains "Los Angeles" (you said the next Super Bowl is in Los Angeles). This is a substring match, so it also catches "Los Angeles, CA" and similar variants.
- **Language:** `favorite_language = 'E'`, which you confirmed means French.
- **Age:** under 28 and not NULL. The minimum recorded age is 13, so this gives the same result as the 13-to-27 range. About 32,000 users have no age recorded and are excluded.

```sql
SELECT DisplayName
FROM users
WHERE Location LIKE '%Los Angeles%'
  AND favorite_language = 'E'
  AND Age IS NOT NULL
  AND Age < 28
ORDER BY DisplayName;
```