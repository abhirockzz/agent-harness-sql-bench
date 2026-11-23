No driver scored more than 30 points in a single race in 2016, so the query returns no rows. No 2016 result exceeds 25 points, so the empty answer is correct, not a query error.

Two definitions came from you:
- **Veteran:** a driver with 5 or more distinct seasons, counting only seasons up to and including 2016.
- **Main page:** the `wikiUrl` column in the `drivers` table.

The query below is correct and runs as is. It returns zero rows for this data. If you meant a different points threshold, such as 20 or 25, tell me and I'll rerun it.

```sql
WITH hi AS (
  SELECT DISTINCT r.driverId, ra.year FROM results r JOIN races ra ON r.raceId=ra.raceId WHERE ra.year<=2016
),
vet AS (
  SELECT driverId FROM hi GROUP BY driverId HAVING COUNT(*)>=5
),
big AS (
  SELECT DISTINCT r.driverId FROM results r JOIN races ra ON r.raceId=ra.raceId WHERE ra.year=2016 AND r.points>30
)
SELECT d.surname, d.wikiUrl
FROM drivers d
JOIN big b ON b.driverId=d.driverId
JOIN vet v ON v.driverId=d.driverId
ORDER BY d.surname ASC;
```