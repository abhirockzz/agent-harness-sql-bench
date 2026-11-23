Five drivers qualify. Two of them, Behelmererer and Melher, have placeholder-looking URLs (francisbehelmererer.com, jonathanmelher.com) rather than Wikipedia pages, so you may want to check those records.

| Last name | Main page (wikiUrl) | Seasons raced |
|---|---|---|
| Behelmererer | http://FrancisBehelmererer.com | 6 |
| Hamilton | http://en.wikipedia.org/wiki/Lewis_Hamilton | 11 |
| Melher | http://JonathanMelher.com | 5 |
| Ricciardo | http://en.wikipedia.org/wiki/Daniel_Ricciardo | 7 |
| Rosberg | http://en.wikipedia.org/wiki/Nico_Rosberg | 11 |

How I got there:
- **Points threshold:** No 2016 result exceeds 30 points. The highest single-race haul in 2016 was 25 points, so I applied the threshold you chose: 25 points or more in a 2016 race, which is a race win. The only results above 30 points are from 2014.
- **Veteran:** Competed in 5 or more different seasons, across all years in the database.
- **Main page:** The `wikiUrl` column, as you specified.

```sql
WITH hi AS (
  SELECT DISTINCT r.driverId
  FROM results r JOIN races ra ON r.raceId = ra.raceId
  WHERE ra.year = 2016 AND r.points >= 25
),
seasons AS (
  SELECT r.driverId, COUNT(DISTINCT ra.year) AS n_seasons
  FROM results r JOIN races ra ON r.raceId = ra.raceId
  GROUP BY r.driverId
)
SELECT d.surname AS last_name, d.wikiUrl AS main_page, s.n_seasons
FROM hi
JOIN seasons s ON s.driverId = hi.driverId
JOIN drivers d ON d.driverId = hi.driverId
WHERE s.n_seasons >= 5
ORDER BY d.surname ASC;
```