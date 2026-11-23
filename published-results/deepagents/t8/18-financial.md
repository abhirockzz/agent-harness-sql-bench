The average loan amount is about **$124,353** across 44 loans.

This uses the definitions you gave:
- **High-risk:** the account's district had unemployment above 6.0% in 1995 (A12) or 1996 (A13).
- **Urban:** urbanization ratio (A10) above 65.
- **Stable economic conditions:** stability score above 50, where the score is (economic_resilience × 2 + financial_health_score × 3 + development_index) / 6.

Five districts qualify: Decin, Chomutov, Most, Teplice and Karvina. The average is over loans, not distinct clients. Each account has one loan here, so it's also 44 accounts.

```sql
SELECT AVG(l.amount) AS avg_loan_amount
FROM loan l
JOIN account a ON a.account_id = l.account_id
JOIN district d ON d.district_id = a.district_id
WHERE d.A10 > 65
  AND (d.A12 > 6.0 OR d.A13 > 6.0)
  AND ((d.economic_resilience * 2 + d.financial_health_score * 3 + d.development_index) / 6.0) > 50;
```