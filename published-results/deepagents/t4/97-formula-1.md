Five drivers meet the criteria. Their last names in ascending order, with their wiki page (the "main page" you specified):

| Surname | Main page (wikiUrl) |
|---|---|
| Behelmererer | http://FrancisBehelmererer.com |
| Hamilton | http://en.wikipedia.org/wiki/Lewis_Hamilton |
| Melher | http://JonathanMelher.com |
| Ricciardo | http://en.wikipedia.org/wiki/Daniel_Ricciardo |
| Rosberg | http://en.wikipedia.org/wiki/Nico_Rosberg |

Two things you should know about these results:

- **The threshold changed.** No driver scored more than 30 points in a single 2016 race. The highest single-race score that year was 25, so I used the 25-point maximum (a race win) as you asked. The query below uses `>= 25`.
- **Veteran definition.** I counted a veteran as a driver with results in 5 or more distinct seasons across the whole results table, not just before 2016.

```sql
WITH veterans AS (
  SELECT res.driverId
  FROM results res
  JOIN races r ON r.raceId = res.raceId
  GROUP BY res.driverId
  HAVING COUNT(DISTINCT r.year) >= 5
),
big_races AS (
  SELECT DISTINCT res.driverId
  FROM results res
  JOIN races r ON r.raceId = res.raceId
  WHERE r.year = 2016 AND res.points >= 25
)
SELECT d.surname, d.wikiUrl
FROM drivers d
WHERE d.driverId IN (SELECT driverId FROM veterans)
  AND d.driverId IN (SELECT driverId FROM big_races)
ORDER BY d.surname ASC;
```