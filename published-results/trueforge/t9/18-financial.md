The average loan amount for high-risk clients in urban districts with stable economic conditions is about **$124,353** across 44 loans.

I used these definitions, all taken from your answers:
- **High-risk:** the loan's account is in a district where unemployment (A12 for 1995, A13 for 1996) exceeds 6.0% in either year.
- **Urban:** urbanization ratio (A10) is above 65.
- **Stable economic conditions:** (economic_resilience × 2 + financial_health_score × 3 + development_index) / 6 is above 50.

The average is per loan, not per client, and districts are linked through each loan's account.

```sql
SELECT AVG(l.amount) AS avg_loan_amount, COUNT(*) AS loan_count
FROM loan l
JOIN account a ON l.account_id = a.account_id
JOIN district d ON a.district_id = d.district_id
WHERE (d.A12 > 6.0 OR d.A13 > 6.0)
  AND d.A10 > 65
  AND (d.economic_resilience * 2 + d.financial_health_score * 3 + d.development_index) / 6.0 > 50;
```