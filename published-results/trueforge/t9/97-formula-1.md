No veteran driver scored more than 30 points in a single 2016 race, so the query returns no rows.

The highest single-race score in 2016 was 25 points, across 445 result rows. The 30-point threshold is never reached, so the veteran filter had nothing to apply to.

Two interpretations I used:
- **Veteran:** you defined it as competing in 5 or more seasons. I counted distinct race years across each driver's whole career in `results`, not only up to 2016.
- **Main page:** you said this is `wikiUrl` in the `drivers` table.

If you meant a different threshold, such as 25 points or more, tell me and I'll rerun it.

```sql
SELECT d.surname, d.wikiUrl
FROM drivers d
WHERE d.driverId IN (
    SELECT r.driverId
    FROM results r
    JOIN races ra ON ra.raceId = r.raceId
    WHERE ra.year = 2016 AND r.points > 30
)
AND (
    SELECT COUNT(DISTINCT ra2.year)
    FROM results r2
    JOIN races ra2 ON ra2.raceId = r2.raceId
    WHERE r2.driverId = d.driverId
) >= 5
ORDER BY d.surname ASC;
```