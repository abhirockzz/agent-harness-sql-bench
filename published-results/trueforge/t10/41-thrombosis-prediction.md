I found 77 patients with at least one LDH value above 500 whose first hospital visit (Date3) falls between 1990-01-01 and 1997-12-31. The list is in the query output above, and the query is below.

Assumptions used:
- **LDH beyond normal range:** LDH > 500, as you specified.
- **"Went to the hospital":** Date3, which the schema describes as the date the patient first went to the hospital. I did not also filter on the Admission column, because you said that question was irrelevant.
- **"Many first years of the 1990s":** 1990 through 1997 inclusive.
- **Patients with several qualifying LDH values** appear once, because of `DISTINCT`.

```sql
SELECT DISTINCT p.ID, p.SEX
FROM Patient p
JOIN Laboratory l ON l.ID = p.ID
WHERE l.LDH > 500
  AND p.Date3 BETWEEN '1990-01-01' AND '1997-12-31';
```