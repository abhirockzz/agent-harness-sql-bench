No drivers meet the criteria. The query returns zero rows.

In the `results` table, the highest single-race points total in 2016 is 25 (the winner's score under the current points system). No driver scored more than 30 points in one race that year, so the list is empty.

Two things I checked:
- **Veteran definition:** you said a veteran is a driver who has competed in 5 or more seasons. I counted distinct race years across all of each driver's results, not only up to 2016.
- **Main page:** you said this is the `wikiUrl` column in `drivers`.

If you meant cumulative season points rather than points from a single race, the answer would be different. The `driverStandings` table holds running totals, and in 2016 many drivers were well above 30 there. Tell me if that is what you intended and I will rerun the query on that basis.

```sql
SELECT DISTINCT d.surname AS last_name, d.wikiUrl AS main_page
FROM results res
JOIN races r ON r.raceId = res.raceId
JOIN drivers d ON d.driverId = res.driverId
WHERE r.year = 2016
  AND res.points > 30
  AND res.driverId IN (
    SELECT res2.driverId
    FROM results res2
    JOIN races r2 ON r2.raceId = res2.raceId
    GROUP BY res2.driverId
    HAVING COUNT(DISTINCT r2.year) >= 5
  )
ORDER BY d.surname ASC;
```