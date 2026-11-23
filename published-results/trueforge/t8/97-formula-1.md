Five drivers match: Behelmererer, Hamilton, Melher, Ricciardo and Rosberg.

Two of your definitions needed interpreting:
- **"More than 30 points in a single race"**: no 2016 result exceeded 30. The highest was 25, so I used your clarification and counted 25-point results (race wins).
- **"Veteran"**: I counted distinct seasons up to and including 2016 and required at least 5.

The "main page" is the `wikiUrl` column. The surnames Behelmererer and Melher are unusual, so you may want to check them against the source data.

```sql
SELECT DISTINCT d.surname AS last_name, d.wikiUrl AS main_page
FROM results res
JOIN races r ON r.raceId = res.raceId
JOIN drivers d ON d.driverId = res.driverId
WHERE r.year = 2016
  AND res.points >= 25
  AND res.driverId IN (
    SELECT r2.driverId
    FROM results r2
    JOIN races ra ON ra.raceId = r2.raceId
    WHERE ra.year <= 2016
    GROUP BY r2.driverId
    HAVING COUNT(DISTINCT ra.year) >= 5
  )
ORDER BY d.surname ASC;
```