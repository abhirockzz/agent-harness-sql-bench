No driver meets the criteria: no 2016 result has more than 30 points. The highest single-race score in 2016 was 25, so the query below returns zero rows.

I used these definitions, from your answers and the data:
- **Veteran:** competed in 5 or more distinct seasons, counting seasons up to and including 2016.
- **Main page:** `wikiUrl` in the `drivers` table.
- **Points:** `results.points` for a single race.

The query runs as written and returns no rows. If you meant a lower threshold, such as 20 points, or a different definition of veteran, I can rerun it.

```sql
WITH vet AS (
  SELECT r.driverId, COUNT(DISTINCT ra.year) AS seasons
  FROM results r JOIN races ra ON ra.raceId = r.raceId
  WHERE ra.year <= 2016
  GROUP BY r.driverId
  HAVING COUNT(DISTINCT ra.year) >= 5
)
SELECT DISTINCT d.surname, d.wikiUrl, v.seasons, res.points, ra.name, ra.year
FROM results res
JOIN races ra ON ra.raceId = res.raceId
JOIN drivers d ON d.driverId = res.driverId
JOIN vet v ON v.driverId = res.driverId
WHERE ra.year = 2016 AND res.points > 30
ORDER BY d.surname ASC;
```