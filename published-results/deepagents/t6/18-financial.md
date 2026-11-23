The average loan amount for high-risk clients in urban districts with stable economic conditions is **about 124,353 USD**, across 44 loans.

The result depends on the definitions you gave:
- **High-risk:** the account's district has unemployment above 6.0% in 1995 (A12) or 1996 (A13). District 69 has no 1995 value, so it qualifies on 1996 alone.
- **Urban:** urbanization ratio (A10) above 65.
- **Stable economic conditions:** the weighted score (economic_resilience × 2 + financial_health_score × 3 + development_index) / 6 is above 50.

The average is over individual loans, using the account's district. Loan amounts are in USD.

```sql
SELECT AVG(l.amount) AS avg_loan_amount
FROM loan l
JOIN account a ON a.account_id = l.account_id
JOIN district d ON d.district_id = a.district_id
WHERE (d.A12 > 6.0 OR d.A13 > 6.0)
  AND d.A10 > 65
  AND ((d.economic_resilience * 2 + d.financial_health_score * 3 + d.development_index) / 6.0) > 50;
```