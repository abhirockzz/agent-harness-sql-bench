Five drivers meet the criteria: Behelmererer, Hamilton, Melher, Ricciardo and Rosberg.

Two of your definitions didn't match the data, so I made these choices:

- **"More than 30 points in a single race" can't be met literally.** The most any driver scored in one 2016 race in the results table is 25. Following your clarification, I treated it as winning a race in 2016 (finishing position 1).
- **"Veteran" is 5 or more distinct seasons.** I counted seasons up to and including 2016. Counting the full career gives the same five drivers.
- **"Main page" is `wikiUrl`,** as you specified.

The Behelmererer and Melher URLs are not Wikipedia links. They are in the data as given, so I left them unchanged.

```sql
SELECT d.surname AS last_name, d.wikiUrl AS main_page
FROM drivers d
WHERE d.driverId IN (
  SELECT r.driverId
  FROM results r JOIN races ra ON ra.raceId = r.raceId
  WHERE ra.year = 2016 AND r.positionOrder = 1
)
AND d.driverId IN (
  SELECT r.driverId
  FROM results r JOIN races ra ON ra.raceId = r.raceId
  WHERE ra.year <= 2016
  GROUP BY r.driverId
  HAVING COUNT(DISTINCT ra.year) >= 5
)
ORDER BY d.surname ASC;
```