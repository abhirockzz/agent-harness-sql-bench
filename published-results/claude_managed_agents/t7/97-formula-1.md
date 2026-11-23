In 2016 there was no race with more than 30 points, since the highest any driver scored was 25. Following your clarification, I used the maximum of 25 points (a race win) as the threshold. Using the definitions you gave, a veteran is a driver with results in 5 or more distinct seasons, and the main page is `wikiUrl`.

Five drivers qualify:

| Surname | Main page (wikiUrl) |
|---|---|
| Behelmererer | http://FrancisBehelmererer.com |
| Hamilton | http://en.wikipedia.org/wiki/Lewis_Hamilton |
| Melher | http://JonathanMelher.com |
| Ricciardo | http://en.wikipedia.org/wiki/Daniel_Ricciardo |
| Rosberg | http://en.wikipedia.org/wiki/Nico_Rosberg |

Two of the main-page values (Behelmererer and Melher) are not Wikipedia links, so they may be worth checking against the source data.

```sql
SELECT d.surname, d.wikiUrl
FROM drivers d
JOIN results r ON r.driverId = d.driverId
JOIN races ra ON ra.raceId = r.raceId
WHERE ra.year = 2016 AND r.points >= 25
  AND d.driverId IN (
    SELECT r2.driverId FROM results r2 JOIN races ra2 ON ra2.raceId = r2.raceId
    GROUP BY r2.driverId HAVING COUNT(DISTINCT ra2.year) >= 5)
GROUP BY d.driverId, d.surname, d.wikiUrl
ORDER BY d.surname ASC;
```