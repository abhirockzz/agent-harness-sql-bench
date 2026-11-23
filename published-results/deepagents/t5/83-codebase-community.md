Only one user matches: **DankMasterDan** (Location "Los Angeles, CA", age 25, favorite_language E).

Here is how I applied your criteria:
- **Location:** contains "Los Angeles", as you specified for the next Super Bowl host city.
- **Language:** `favorite_language = 'E'`, which you confirmed means French.
- **Age:** under 28, as you specified. I excluded users with no recorded age, since about 32,000 users have a NULL age and I can't confirm they meet the requirement.

```sql
SELECT DisplayName
FROM users
WHERE Location LIKE '%Los Angeles%'
  AND favorite_language = 'E'
  AND Age IS NOT NULL
  AND Age < 28;
```