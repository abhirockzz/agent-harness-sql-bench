No driver scored more than 30 points in a single race in the 2016 season, so the query returns no rows.

The 2016 season's highest single-race score was 25 points, and the database has no 2016 result above 30. The only results above 30 points in the whole database are two from the 2014 Abu Dhabi Grand Prix (Hamilton with 50 and Massa with 36), which points to double-points scoring in that race. If you meant a different season or threshold, tell me and I'll rerun the query.

I used your definition of a veteran as a driver who has raced in 5 or more different seasons. I read "main page" as the `principalUrl` column in `drivers`, since that is the principal website; the other candidates are `introductionUrl`, `wikiUrl` and `fanUrl`.

```sql
SELECT d.surname, d.principalUrl
FROM results res
JOIN races r ON r.raceId = res.raceId
JOIN drivers d ON d.driverId = res.driverId
WHERE r.year = 2016
  AND res.points > 30
  AND (
    SELECT COUNT(DISTINCT r2.year)
    FROM results x
    JOIN races r2 ON r2.raceId = x.raceId
    WHERE x.driverId = d.driverId
  ) >= 5
ORDER BY d.surname ASC;
```