Here are the patients with LDH above 500 whose first hospital visit (Date3) falls between 1990-01-01 and 1997-12-31. The query returns 109 patients. Each appears once, even if they have several qualifying lab rows.

The filters follow your answers:
- **LDH beyond normal range:** LDH > 500.
- **"Many first years of the 1990s":** 1990 through 1997 inclusive.
- **"Went to the hospital":** Patient.Date3, which the clarification identified as the date the patient first went to the hospital.

I did not filter on the Admission column ('+' = admitted, '-' = outpatient), since the question was about the visit date.

```sql
SELECT DISTINCT p.ID, p.SEX
FROM Patient p
JOIN Laboratory l ON l.ID = p.ID
WHERE l.LDH > 500
  AND p.Date3 BETWEEN '1990-01-01' AND '1997-12-31'
ORDER BY p.ID;
```