The average loan amount is **about 124,353 USD** across 44 loans.

This uses the definitions you gave me:
- **High-risk:** the account's district has an unemployment rate above 6.0% in 1995 (A12) or 1996 (A13).
- **Urban:** urbanization ratio (A10) above 65.
- **Stable economic conditions:** (economic_resilience × 2 + financial_health_score × 3 + development_index) / 6, above 50.

Four districts qualify (33 is excluded: its stability score is about 40.9): 34, 39, 40 and 70. Each loan is counted once, and the district comes from the loan's account (`account.district_id`), as you specified.

```sql
WITH d AS (
  SELECT district_id, A10, A12, A13,
         (economic_resilience*2 + financial_health_score*3 + development_index)/6.0 AS stab
  FROM district
)
SELECT ROUND(AVG(l.amount), 2) AS avg_loan_amount
FROM loan l
JOIN account a ON a.account_id = l.account_id
JOIN d ON d.district_id = a.district_id
WHERE d.A10 > 65
  AND (d.A12 > 6.0 OR d.A13 > 6.0)
  AND d.stab > 50;
```