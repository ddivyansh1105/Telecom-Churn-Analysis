# SQL query results

Output of every query in `churn_queries.sql`, run on `data/telco_clean.csv` (7,043 customers).

## 1. Overall churn rate and revenue at risk

| customers | churned | churn_rate_pct | monthly_revenue_lost | pct_of_monthly_revenue |
|---|---|---|---|---|
| 7043 | 1869 | 26.5 | 139131.0 | 30.5 |

## 2. Churn by contract type

| Contract | customers | churned | churn_rate_pct |
|---|---|---|---|
| Month-to-month | 3875 | 1655 | 42.7 |
| One year | 1473 | 166 | 11.3 |
| Two year | 1695 | 48 | 2.8 |

## 3. Churn by tenure band (when do customers leave?)

| TenureBand | customers | churn_rate_pct |
|---|---|---|
| 0-6 mo | 1481 | 52.9 |
| 7-12 mo | 705 | 35.9 |
| 13-24 mo | 1024 | 28.7 |
| 25-48 mo | 1594 | 20.4 |
| 49-72 mo | 2239 | 9.5 |

## 4. Contract x tenure band (which segment is worst?)

| Contract | TenureBand | customers | churn_rate_pct |
|---|---|---|---|
| Month-to-month | 0-6 mo | 1413 | 55.2 |
| Month-to-month | 7-12 mo | 581 | 42.0 |
| Month-to-month | 13-24 mo | 737 | 37.7 |
| Month-to-month | 25-48 mo | 802 | 32.9 |
| Month-to-month | 49-72 mo | 342 | 26.0 |
| One year | 49-72 mo | 634 | 12.9 |
| One year | 25-48 mo | 518 | 10.6 |
| One year | 7-12 mo | 85 | 10.6 |
| One year | 0-6 mo | 39 | 10.3 |
| One year | 13-24 mo | 197 | 8.1 |
| Two year | 49-72 mo | 1263 | 3.3 |
| Two year | 25-48 mo | 274 | 2.2 |
| Two year | 13-24 mo | 90 | 0.0 |
| Two year | 7-12 mo | 39 | 0.0 |

## 5. Internet service type and payment method

| InternetService | customers | churn_rate_pct |
|---|---|---|
| Fiber optic | 3096 | 41.9 |
| DSL | 2421 | 19.0 |
| No | 1526 | 7.4 |

| PaymentMethod | customers | churn_rate_pct |
|---|---|---|
| Electronic check | 2365 | 45.3 |
| Mailed check | 1612 | 19.1 |
| Bank transfer (automatic) | 1544 | 16.7 |
| Credit card (automatic) | 1522 | 15.2 |

## 6. Do support / security add-ons reduce churn?

| addon_services_count | customers | churn_rate_pct |
|---|---|---|
| 0 | 1267 | 56.7 |
| 1 | 1467 | 38.9 |
| 2 | 1372 | 23.8 |
| 3 | 941 | 12.4 |
| 4 | 470 | 5.3 |

| TechSupport | customers | churn_rate_pct |
|---|---|---|
| No | 3473 | 41.6 |
| Yes | 2044 | 15.2 |

## 7. High-risk segment: where is the money?

| customers | churn_rate_pct | avg_monthly_charge | monthly_revenue_lost |
|---|---|---|---|
| 833 | 71.1 | 81.19 | 48490.0 |

## 8. Share of all churn contributed by each contract type

| Contract | churned | pct_of_all_churn |
|---|---|---|
| Month-to-month | 1655 | 88.6 |
| One year | 166 | 8.9 |
| Two year | 48 | 2.6 |

## 9. Payment methods within each contract type, highest churn first

| Contract | PaymentMethod | customers | churn_rate_pct |
|---|---|---|---|
| Month-to-month | Electronic check | 1850 | 53.7 |
| Month-to-month | Bank transfer (automatic) | 589 | 34.1 |
| Month-to-month | Credit card (automatic) | 543 | 32.8 |
| Month-to-month | Mailed check | 893 | 31.6 |
| One year | Electronic check | 347 | 18.4 |
| One year | Credit card (automatic) | 398 | 10.3 |
| One year | Bank transfer (automatic) | 391 | 9.7 |
| One year | Mailed check | 337 | 6.8 |
| Two year | Electronic check | 168 | 7.7 |
| Two year | Bank transfer (automatic) | 564 | 3.4 |
| Two year | Credit card (automatic) | 581 | 2.2 |
| Two year | Mailed check | 382 | 0.8 |

## 10. Churn by monthly-charge band

| charge_band | customers | churn_rate_pct |
|---|---|---|
| 1: under 35 | 1731 | 10.9 |
| 2: 35 to 70 | 1721 | 23.6 |
| 3: 70 to 90 | 1847 | 38.0 |
| 4: 90 and above | 1744 | 32.9 |

## 11. Why do customers leave? Top reasons given by churned customers

| ChurnReason | churned_customers | pct_of_churners |
|---|---|---|
| Attitude of support person | 192 | 10.3 |
| Competitor offered higher download speeds | 189 | 10.1 |
| Competitor offered more data | 162 | 8.7 |
| Don't know | 154 | 8.2 |
| Competitor made better offer | 140 | 7.5 |
| Attitude of service provider | 135 | 7.2 |
| Competitor had better devices | 130 | 7.0 |
| Network reliability | 103 | 5.5 |
| Product dissatisfaction | 102 | 5.5 |
| Price too high | 98 | 5.2 |

## 12. Churned vs retained customers: value, price and tenure

| Churn | customers | avg_cltv | avg_monthly_charge | avg_tenure_months |
|---|---|---|---|---|
| No | 5174 | 4491.0 | 61.27 | 37.6 |
| Yes | 1869 | 4149.0 | 74.44 | 18.0 |

## 13. Cities with the highest churn (at least 50 customers)

| City | customers | churn_rate_pct |
|---|---|---|
| San Diego | 150 | 33.3 |
| San Francisco | 104 | 29.8 |
| Los Angeles | 305 | 29.5 |
| San Jose | 112 | 25.9 |
| Oakland | 52 | 25.0 |
| Long Beach | 60 | 25.0 |
| Fresno | 64 | 25.0 |
| Sacramento | 108 | 24.1 |
