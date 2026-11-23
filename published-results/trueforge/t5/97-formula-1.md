Five veteran drivers scored the maximum 25 points in a single 2016 race.

- No driver scored more than 30 points in one race in 2016. The highest single-race total that year is 25, so I used 25 points as the threshold, which you confirmed means a race win.
- I took "veteran" to mean the driver has competed in 5 or more seasons in total across the database. You didn't say whether to count all seasons or only those before 2016, and your answer restated the 5-season rule without settling that. The total-career count is the literal reading, so I used it. Counting only pre-2016 seasons would drop Melher and Behelmererer.
- "Main page" is the `wikiUrl` column in `drivers`.

| last_name | main_page |
|---|---|
| Behelmererer | http://FrancisBehelmererer.com |
| Hamilton | http://en.wikipedia.org/wiki/Lewis_Hamilton |
| Melher | http://JonathanMelher.com |
| Ricciardo | http://en.wikipedia.org/wiki/Daniel_Ricciardo |
| Rosberg | http://en.wikipedia.org/wiki/Nico_Rosberg |

```sql
SELECT d.surname AS last_name, d.wikiUrl AS main_page
FROM drivers d
WHERE d.driverId IN (
    SELECT res.driverId FROM results res
    JOIN races r ON res.raceId = r.raceId
    WHERE r.year = 2016 AND res.points = 25
)
AND (
    SELECT COUNT(DISTINCT r2.year) FROM results x
    JOIN races r2 ON x.raceId = r2.raceId
    WHERE x.driverId = d.driverId
) >= 5
ORDER BY d.surname ASC;
```