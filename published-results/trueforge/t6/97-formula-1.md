Five veteran drivers match, using the definitions you gave me:

- **Last name**: Behelmererer, Hamilton, Melher, Ricciardo, Rosberg
- **Main page**: the `wikiUrl` field for each driver

No driver scored more than 30 points in a single 2016 race. The most anyone scored was 25, so I used your clarification of 25 points (a race win) as the threshold. "Veteran" means competing in at least 5 seasons, counted through 2016. Using all career seasons gives the same five drivers.

```sql
SELECT d.surname AS last_name, d.wikiUrl AS main_page
FROM drivers d
WHERE d.driverId IN (
    SELECT res.driverId
    FROM results res
    JOIN races r ON r.raceId = res.raceId
    WHERE r.year = 2016 AND res.points >= 25
)
AND (
    SELECT COUNT(DISTINCT r2.year)
    FROM results x
    JOIN races r2 ON r2.raceId = x.raceId
    WHERE x.driverId = d.driverId AND r2.year <= 2016
) >= 5
ORDER BY d.surname ASC;
```