No driver scored more than 30 points in a single race in the 2016 season, so there are no names to list. The highest single-race total in 2016 was 25 points, across 445 race results.

Because the filter returns no rows, the definition of "veteran" doesn't change the answer, so I didn't need to ask about it. If you meant a different threshold, such as 25 points or more, or a different season, tell me and I'll rerun the query.

The "main page" is the `principalUrl` column in `drivers`. The query below runs as written and returns no rows:

```sql
SELECT d.surname, d.principalUrl
FROM results res
JOIN races r ON r.raceId = res.raceId
JOIN drivers d ON d.driverId = res.driverId
WHERE r.year = 2016 AND res.points > 30
ORDER BY d.surname ASC;
```