The average loan amount is about **124,353 USD**, across 44 loans.

This uses your definitions:
- **High-risk:** the account's district has unemployment above 6.0% in 1995 (A12) or 1996 (A13).
- **Urban:** urbanization ratio (A10) above 65.
- **Stable economic conditions:** the weighted score `(economic_resilience × 2 + financial_health_score × 3 + development_index) / 6` is above 50.

Each loan is counted once, joined through its account to the account's district.

```sql
SELECT AVG(l.amount) AS avg_loan_amount, COUNT(*) AS loan_count
FROM loan l
JOIN account a ON l.account_id = a.account_id
JOIN district d ON a.district_id = d.district_id
WHERE (d.A12 > 6.0 OR d.A13 > 6.0)
  AND d.A10 > 65
  AND (d.economic_resilience * 2 + d.financial_health_score * 3 + d.development_index) / 6.0 > 50;
```