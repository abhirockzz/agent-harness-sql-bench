Five drivers match: Behelmererer, Hamilton, Melher, Ricciardo and Rosberg.

Nobody scored more than 30 points in a single 2016 race, because the maximum possible is 25 for a win. Following your clarification, I used 25 points as the threshold. The surnames as stored include odd spellings ("Behelmererer", "Melher", "Ricciardo"), which I returned unchanged.

Two assumptions to check:
- **Veteran:** a driver with results in 5 or more distinct seasons across their whole career, not only up to 2016.
- **Main page:** the `fanUrl` column, since its description says it is "considered as the main page by some." The `principalUrl` column is the alternative if you meant the official site.

```sql
SELECT d.surname AS last_name, d.fanUrl AS main_page
FROM drivers d
WHERE d.driverId IN (
  SELECT r.driverId FROM results r
  JOIN races ra ON ra.raceId = r.raceId
  WHERE ra.year = 2016 AND r.points >= 25
)
AND d.driverId IN (
  SELECT r2.driverId FROM results r2
  JOIN races ra2 ON ra2.raceId = r2.raceId
  GROUP BY r2.driverId
  HAVING COUNT(DISTINCT ra2.year) >= 5
)
ORDER BY d.surname ASC;
```