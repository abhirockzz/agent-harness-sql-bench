No veteran drivers scored more than 30 points in a single race during the 2016 season, so the query returns no rows.

The highest single-race score in 2016 was 25 points, across 445 result rows. The only results above 30 points in the whole database are from other years.

I applied the definitions you gave me:
- **Veteran:** a driver with 5 or more distinct seasons in the database, counted across their whole career.
- **Main page:** the `wikiUrl` field.

```sql
SELECT d.surname AS last_name, d.wikiUrl AS main_page
FROM drivers d
WHERE d.driverId IN (
  SELECT r.driverId
  FROM results r
  JOIN races ra ON ra.raceId = r.raceId
  WHERE ra.year = 2016 AND r.points > 30
)
AND d.driverId IN (
  SELECT r.driverId
  FROM results r
  JOIN races ra ON ra.raceId = r.raceId
  GROUP BY r.driverId
  HAVING COUNT(DISTINCT ra.year) >= 5
)
ORDER BY d.surname ASC;
```