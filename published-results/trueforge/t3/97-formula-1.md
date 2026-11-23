No driver scored more than 30 points in a single race in 2016, so the query returns no rows. In the 2016 results the highest single-race total is 25 points, so the 30-point threshold excludes everyone.

I used your definition of a veteran (5 or more distinct seasons in the results data). The `drivers` table has four URL fields (`introductionUrl`, `principalUrl`, `wikiUrl`, `fanUrl`) and none is labelled "main page". I've used `principalUrl` as a placeholder, but that choice doesn't affect the result while the list is empty.

If you meant a lower threshold, such as 20 or 25 points, tell me and I'll rerun it.

```sql
SELECT d.surname, d.principalUrl AS main_page
FROM drivers d
WHERE d.driverId IN (
  SELECT r.driverId
  FROM results r
  JOIN races ra ON r.raceId = ra.raceId
  WHERE ra.year = 2016 AND r.points > 30
)
AND (
  SELECT COUNT(DISTINCT ra2.year)
  FROM results r2
  JOIN races ra2 ON r2.raceId = ra2.raceId
  WHERE r2.driverId = d.driverId
) >= 5
ORDER BY d.surname ASC;
```