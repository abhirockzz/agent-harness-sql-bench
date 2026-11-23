No veteran drivers match. In the 2016 season, no driver scored more than 30 points in a single race. The highest single-race total was 25 points, across 445 race results from that season. So the list is empty, and there are no surnames or profile URLs to report.

I used your definition of a veteran (5 or more seasons raced) and counted seasons through 2016. The filter returned no rows because the points threshold excludes every driver, so the veteran condition doesn't change the result.

If you meant a different points threshold, such as 20 or more, or a different season, I can rerun the query with that change.

```sql
WITH top AS (
  SELECT DISTINCT r.driverId
  FROM results r JOIN races ra ON r.raceId = ra.raceId
  WHERE ra.year = 2016 AND r.points > 30
),
career AS (
  SELECT r.driverId, COUNT(DISTINCT ra.year) AS seasons_thru_2016
  FROM results r JOIN races ra ON r.raceId = ra.raceId
  WHERE ra.year <= 2016
  GROUP BY r.driverId
)
SELECT d.surname, d.principalUrl, c.seasons_thru_2016
FROM top t
JOIN drivers d ON d.driverId = t.driverId
JOIN career c ON c.driverId = t.driverId
WHERE c.seasons_thru_2016 >= 5
ORDER BY d.surname;
```