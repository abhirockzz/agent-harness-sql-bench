No driver qualifies. In the 2016 season, the highest single-race points total in the `results` table is 25.0, so nobody scored more than 30 points in one race. The query below returns no rows, so there are no surnames or wiki links to list.

I used these definitions, from your answers:
- **Veteran:** a driver who has competed in 5 or more seasons (distinct years in `results` joined to `races`).
- **Main page:** `wikiUrl` in the `drivers` table.

The query is written to show the list if the data changes or the threshold is revised:

```sql
WITH hi AS (
  SELECT r.driverId
  FROM results r
  JOIN races ra ON ra.raceId = r.raceId
  WHERE ra.year = 2016
  GROUP BY r.driverId
  HAVING MAX(r.points) > 30
),
career AS (
  SELECT r.driverId, COUNT(DISTINCT ra.year) AS seasons_total
  FROM results r
  JOIN races ra ON ra.raceId = r.raceId
  GROUP BY r.driverId
)
SELECT d.surname AS last_name, d.wikiUrl AS main_page
FROM hi
JOIN drivers d ON d.driverId = hi.driverId
JOIN career c ON c.driverId = hi.driverId
WHERE c.seasons_total >= 5
ORDER BY d.surname ASC;
```