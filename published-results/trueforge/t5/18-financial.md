The average loan amount is about **124,353.27 USD**, across 44 loans.

This uses your definitions:
- **High-risk:** the account's district has unemployment above 6.0% in 1995 (A12) or 1996 (A13).
- **Urban:** urbanization ratio (A10) above 65.
- **Stable economic conditions:** the weighted score `(economic_resilience × 2 + financial_health_score × 3 + development_index) / 6` is above 50.

Loans are linked to districts through `account.district_id`. The query counts each loan once, so the result is an average per loan, not per client.

```sql
SELECT ROUND(AVG(l.amount), 2) AS avg_loan_amount, COUNT(*) AS loan_count
FROM loan l
JOIN account a ON a.account_id = l.account_id
JOIN district d ON d.district_id = a.district_id
WHERE (d.A12 > 6.0 OR d.A13 > 6.0)
  AND d.A10 > 65
  AND ((d.economic_resilience * 2 + d.financial_health_score * 3 + d.development_index) / 6.0) > 50;
```