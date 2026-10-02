# Churn Analysis: Business Summary

**Problem:** 26.5% of 7,043 telecom customers churned.

**Who churns:** Customers in their first 12 months (47.4%), electronic check payers (45.3%),
month-to-month contracts (42.7%) and fiber optic users (41.9%).

**Model:** Logistic regression performed best (ROC-AUC 0.853). At a 0.3 threshold it catches
92.2% of churners (precision 42.3%); at 0.5 it catches 84.0% (precision 52.3%). A lower
threshold finds more churners but wastes more retention offers.

**Revenue at risk:** About $114,508/month in expected revenue; 1,002 high-risk active
customers represent $77,223/month.

**Recommendations:**
1. Offer discounted 12-month contracts to high-risk month-to-month customers.
2. Run an onboarding and check-in program for customers in their first 12 months.
3. Incentivise auto-pay over electronic check.

**Expected impact:** Saving 20% of the high-risk group protects about $15,445/month
(assumption to validate with an A/B test).