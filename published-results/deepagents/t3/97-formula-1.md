No driver meets the criteria, so the query returns no rows.

In the 2016 season, the highest single-race points total in the `results` table is 25.0. Under the scoring system used that year, a driver can't score more than 25 points in one race, so no driver scored more than 30. The veteran filter and the wikiUrl column therefore don't affect the result.

I asked you two clarifying questions before running this. You said a veteran is a driver who has competed in 5 or more seasons, and that the main page is the `wikiUrl` column. The query below applies the points filter to 2016 races. It doesn't apply the veteran filter, because the result is empty either way.

```sql
SELECT DISTINCT d.surname, d.wikiUrl
FROM results r
JOIN races ra ON ra.raceId = r.raceId AND ra.year = 2016
JOIN drivers d ON d.driverId = r.driverId
WHERE r.points > 30
ORDER BY d.surname;
```