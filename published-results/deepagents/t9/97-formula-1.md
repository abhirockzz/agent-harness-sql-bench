No driver meets the criteria, so the answer is an empty list.

In the 2016 season, the highest single-race points total in the `results` table is 25. No driver scored more than 30 points in any race that year, so no veteran drivers qualify, and there are no last names or URLs to list.

I used your definition of a veteran (at least 5 distinct seasons in the results table) and the `wikiUrl` column as the main page. The threshold filter removes every row before the veteran check matters, so the result would be empty under any veteran definition.

If you meant a different season, or a different measure (for example, season totals from `driverStandings`), tell me and I'll rerun it.

```sql
WITH veterans AS (
  SELECT res.driverId
  FROM results res
  JOIN races r ON r.raceId = res.raceId
  GROUP BY res.driverId
  HAVING COUNT(DISTINCT r.year) >= 5
)
SELECT DISTINCT d.surname, d.wikiUrl
FROM results res
JOIN races r ON r.raceId = res.raceId AND r.year = 2016
JOIN drivers d ON d.driverId = res.driverId
WHERE res.points > 30 AND res.driverId IN (SELECT driverId FROM veterans)
ORDER BY d.surname ASC;
```