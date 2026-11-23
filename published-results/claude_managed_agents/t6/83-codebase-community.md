One user matches all three criteria: **DankMasterDan**.

I used your answers as given:
- **Host city:** Los Angeles, matched by `Location LIKE '%Los Angeles%'`. Locations are self-reported, so users who write something like "SoCal" would not be included.
- **Age:** under 28, matched by `Age < 28`.
- **French:** favorite_language `'E'`.

```sql
SELECT DisplayName
FROM users
WHERE Location LIKE '%Los Angeles%'
  AND favorite_language = 'E'
  AND Age < 28;
```