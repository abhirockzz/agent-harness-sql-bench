Five drivers match: Behelmererer, Hamilton, Melher, Ricciardo and Rosberg.

No 2016 race result exceeds 30 points, since the maximum is 25. You then defined the criterion as scoring the maximum 25 points in a single race (a win), so I used that. "Veteran" means competing in 5 or more seasons, counted through 2016. I took "main page" to mean the `principalUrl` column, since the schema describes it as the driver's principal website.

| Surname | Main page (principalUrl) |
|---|---|
| Behelmererer | http://FrancisBehelmererer.com/principal |
| Hamilton | http://en.wikipedia.org/wiki/Lewis_Hamilton/principal |
| Melher | http://JonathanMelher.com/principal |
| Ricciardo | http://en.wikipedia.org/wiki/Daniel_Ricciardo/principal |
| Rosberg | http://en.wikipedia.org/wiki/Nico_Rosberg/principal |

```sql
SELECT d.surname, d.principalUrl, COUNT(DISTINCT r.year) AS career_seasons
FROM results res
JOIN races r ON r.raceId = res.raceId
JOIN drivers d ON d.driverId = res.driverId
WHERE res.driverId IN (
    SELECT res2.driverId FROM results res2 JOIN races r2 ON r2.raceId = res2.raceId
    WHERE r2.year = 2016 AND res2.points = 25)
  AND r.year <= 2016
GROUP BY d.driverId, d.surname, d.principalUrl
HAVING COUNT(DISTINCT r.year) >= 5
ORDER BY d.surname;
```