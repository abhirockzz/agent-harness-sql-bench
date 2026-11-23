No driver meets the criteria, so the answer is an empty list.

In the 2016 season, the highest number of points any driver scored in a single race was 25. The `results` table has no race with more than 30 points in 2016, so no driver can qualify, whatever the veteran definition.

For reference, I used these definitions:
- **Veteran:** competed in 5 or more seasons. I counted distinct seasons up to and including 2016. Your answer to the counting-window question didn't address that choice, so I made it myself. Using whole-career seasons would not change the result, because the points filter alone eliminates every driver.
- **Main page:** `wikiUrl` in the `drivers` table.

```sql
SELECT d.surname, d.wikiUrl
FROM drivers d
JOIN (
  SELECT res.driverId
  FROM results res
  JOIN races r ON r.raceId = res.raceId
  WHERE r.year = 2016 AND res.points > 30
  GROUP BY res.driverId
) s ON s.driverId = d.driverId
WHERE (
  SELECT COUNT(DISTINCT r2.year)
  FROM results res2
  JOIN races r2 ON r2.raceId = res2.raceId
  WHERE res2.driverId = d.driverId AND r2.year <= 2016
) >= 5
ORDER BY d.surname ASC;
```