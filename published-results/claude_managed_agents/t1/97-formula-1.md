Five drivers match, but only because I had to change the threshold. No 2016 race had a driver score more than 30 points: the highest single-race total that season was 25.

I asked how to handle that. Your answer was to treat "more than 30" as the maximum possible score, 25 points, which is a race win. I applied that, and "veteran" as five or more distinct seasons in the results data.

| last_name | main_page |
|---|---|
| Behelmererer | http://FrancisBehelmererer.com |
| Hamilton | http://en.wikipedia.org/wiki/Lewis_Hamilton |
| Melher | http://JonathanMelher.com |
| Ricciardo | http://en.wikipedia.org/wiki/Daniel_Ricciardo |
| Rosberg | http://en.wikipedia.org/wiki/Nico_Rosberg |

Two of the surnames (Behelmererer, Melher) and their URLs look unusual compared with the others. I returned them as stored, but they may be data-quality issues worth checking.

```sql
SELECT d.surname AS last_name, d.wikiUrl AS main_page
FROM drivers d
WHERE d.driverId IN (
  SELECT r.driverId FROM results r
  JOIN races ra ON ra.raceId = r.raceId
  WHERE ra.year = 2016 AND r.points >= 25
)
AND (
  SELECT COUNT(DISTINCT ra2.year) FROM results r2
  JOIN races ra2 ON ra2.raceId = r2.raceId
  WHERE r2.driverId = d.driverId
) >= 5
ORDER BY d.surname ASC;
```