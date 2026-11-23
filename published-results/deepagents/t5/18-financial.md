The average loan amount for high-risk clients in urban districts with stable economic conditions is about **124,353 USD**, based on 44 loans.

I used the definitions you gave:
- **High-risk:** the client's account is in a district where unemployment (A12 for 1995 or A13 for 1996) is above 6.0%.
- **Urban:** urbanization ratio (A10) is above 65.
- **Stable economic conditions:** (economic_resilience × 2 + financial_health_score × 3 + development_index) / 6 is above 50.

The average is over loans, not distinct clients, and district is taken from the account, not the client's home address.

```sql
SELECT AVG(l.amount) AS avg_loan_amount
FROM loan l
JOIN account a ON a.account_id = l.account_id
JOIN district d ON d.district_id = a.district_id
WHERE (d.A12 > 6.0 OR d.A13 > 6.0)
  AND d.A10 > 65
  AND (d.economic_resilience * 2 + d.financial_health_score * 3 + d.development_index) / 6 > 50;
```