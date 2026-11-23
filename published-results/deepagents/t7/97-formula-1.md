Five drivers meet the criteria. Their last names in ascending order, with their main page (`wikiUrl`):

| surname | wikiUrl |
|---|---|
| Behelmererer | http://FrancisBehelmererer.com |
| Hamilton | http://en.wikipedia.org/wiki/Lewis_Hamilton |
| Melher | http://JonathanMelher.com |
| Ricciardo | http://en.wikipedia.org/wiki/Daniel_Ricciardo |
| Rosberg | http://en.wikipedia.org/wiki/Nico_Rosberg |

No driver actually scored more than 30 points in one race in 2016. The highest single-race total is 25. Following your clarification, I used 25 points (a race win) as the threshold. A veteran is a driver with results in 5 or more distinct seasons across the whole table, not just 2016.

```sql
SELECT DISTINCT d.surname, d.wikiUrl
FROM results res
JOIN races r ON r.raceId = res.raceId
JOIN drivers d ON d.driverId = res.driverId
WHERE r.year = 2016
  AND res.points = 25
  AND d.driverId IN (
      SELECT r2.driverId
      FROM results r2
      JOIN races ra ON ra.raceId = r2.raceId
      GROUP BY r2.driverId
      HAVING COUNT(DISTINCT ra.year) >= 5
  )
ORDER BY d.surname;
```