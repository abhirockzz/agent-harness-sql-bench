The average loan amount is about **$124,353** across 44 loans.

This uses the definitions you gave:
- **High-risk:** the account's district has unemployment above 6.0% in 1995 (A12) or 1996 (A13).
- **Urban:** urbanization ratio A10 above 65.
- **Stable economic conditions:** the stability score `(economic_resilience × 2 + financial_health_score × 3 + development_index) / 6` is above 50.

Loans are linked to districts through `account.district_id`, as you specified.

```sql
SELECT AVG(l.amount) AS avg_loan_amount
FROM loan l
JOIN account a ON l.account_id = a.account_id
JOIN district d ON a.district_id = d.district_id
WHERE (d.A12 > 6.0 OR d.A13 > 6.0)
  AND d.A10 > 65
  AND (d.economic_resilience * 2 + d.financial_health_score * 3 + d.development_index) / 6.0 > 50;
```