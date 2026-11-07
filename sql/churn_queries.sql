-- =====================================================================
-- Telecom Churn Analysis - MySQL (works on MySQL 5.7 and 8.x)
-- Dataset: IBM Telco Customer Churn (Kaggle), 7,043 customers
-- Load data/telco_clean.csv (created by churn_analysis.py) first.
-- =====================================================================

CREATE DATABASE IF NOT EXISTS telco;
USE telco;

DROP TABLE IF EXISTS customers;
CREATE TABLE customers (
    customerID          VARCHAR(20) PRIMARY KEY,
    City                VARCHAR(40),
    State               VARCHAR(20),
    ZipCode             VARCHAR(10),
    gender              VARCHAR(10),
    SeniorCitizen       VARCHAR(3),
    Partner             VARCHAR(3),
    Dependents          VARCHAR(3),
    tenure              INT,
    PhoneService        VARCHAR(3),
    MultipleLines       VARCHAR(3),
    InternetService     VARCHAR(20),
    OnlineSecurity      VARCHAR(3),
    OnlineBackup        VARCHAR(3),
    DeviceProtection    VARCHAR(3),
    TechSupport         VARCHAR(3),
    StreamingTV         VARCHAR(3),
    StreamingMovies     VARCHAR(3),
    Contract            VARCHAR(20),
    PaperlessBilling    VARCHAR(3),
    PaymentMethod       VARCHAR(40),
    MonthlyCharges      DECIMAL(8,2),
    TotalCharges        DECIMAL(10,2),
    Churn               VARCHAR(3),
    ChurnFlag           TINYINT,
    ChurnScore          INT,
    CLTV                INT,
    ChurnReason         VARCHAR(60),
    TenureBand          VARCHAR(10),
    ProtectionServices  TINYINT
);

-- Load the data: in MySQL Workbench, right-click the table "customers"
-- -> Table Data Import Wizard -> choose data/telco_clean.csv
-- (use telco_clean.csv, NOT the original Kaggle file).

-- ---------------------------------------------------------------------
-- 0. Sanity checks
-- ---------------------------------------------------------------------
SELECT COUNT(*) AS total_customers FROM customers;

SELECT COUNT(DISTINCT customerID) AS unique_customers FROM customers;

-- ---------------------------------------------------------------------
-- 1. Overall churn rate and revenue at risk
-- ---------------------------------------------------------------------
SELECT
    COUNT(*)                                                        AS customers,
    SUM(ChurnFlag)                                                  AS churned,
    ROUND(100 * AVG(ChurnFlag), 1)                                  AS churn_rate_pct,
    ROUND(SUM(CASE WHEN ChurnFlag = 1 THEN MonthlyCharges END), 0)  AS monthly_revenue_lost,
    ROUND(100 * SUM(CASE WHEN ChurnFlag = 1 THEN MonthlyCharges END)
              / SUM(MonthlyCharges), 1)                             AS pct_of_monthly_revenue
FROM customers;

-- ---------------------------------------------------------------------
-- 2. Churn by contract type
-- ---------------------------------------------------------------------
SELECT
    Contract,
    COUNT(*)                         AS customers,
    SUM(ChurnFlag)                   AS churned,
    ROUND(100 * AVG(ChurnFlag), 1)   AS churn_rate_pct
FROM customers
GROUP BY Contract
ORDER BY churn_rate_pct DESC;

-- ---------------------------------------------------------------------
-- 3. Churn by tenure band (when do customers leave?)
-- ---------------------------------------------------------------------
SELECT
    TenureBand,
    COUNT(*)                         AS customers,
    ROUND(100 * AVG(ChurnFlag), 1)   AS churn_rate_pct
FROM customers
GROUP BY TenureBand
ORDER BY MIN(tenure);

-- ---------------------------------------------------------------------
-- 4. Contract x tenure band (which segment is worst?)
-- ---------------------------------------------------------------------
SELECT
    Contract,
    TenureBand,
    COUNT(*)                         AS customers,
    ROUND(100 * AVG(ChurnFlag), 1)   AS churn_rate_pct
FROM customers
GROUP BY Contract, TenureBand
HAVING COUNT(*) >= 30            -- ignore tiny groups
ORDER BY churn_rate_pct DESC;

-- ---------------------------------------------------------------------
-- 5. Internet service type and payment method
-- ---------------------------------------------------------------------
SELECT
    InternetService,
    COUNT(*)                         AS customers,
    ROUND(100 * AVG(ChurnFlag), 1)   AS churn_rate_pct
FROM customers
GROUP BY InternetService
ORDER BY churn_rate_pct DESC;

SELECT
    PaymentMethod,
    COUNT(*)                         AS customers,
    ROUND(100 * AVG(ChurnFlag), 1)   AS churn_rate_pct
FROM customers
GROUP BY PaymentMethod
ORDER BY churn_rate_pct DESC;

-- ---------------------------------------------------------------------
-- 6. Do support / security add-ons reduce churn?
-- ---------------------------------------------------------------------
SELECT
    ProtectionServices               AS addon_services_count,
    COUNT(*)                         AS customers,
    ROUND(100 * AVG(ChurnFlag), 1)   AS churn_rate_pct
FROM customers
WHERE InternetService <> 'No'
GROUP BY ProtectionServices
ORDER BY ProtectionServices;

SELECT
    TechSupport,
    COUNT(*)                         AS customers,
    ROUND(100 * AVG(ChurnFlag), 1)   AS churn_rate_pct
FROM customers
WHERE InternetService <> 'No'
GROUP BY TechSupport;

-- ---------------------------------------------------------------------
-- 7. High-risk segment: where is the money?
--    Month-to-month, fibre optic, no tech support, tenure <= 12 months
-- ---------------------------------------------------------------------
SELECT
    COUNT(*)                                                        AS customers,
    ROUND(100 * AVG(ChurnFlag), 1)                                  AS churn_rate_pct,
    ROUND(AVG(MonthlyCharges), 2)                                   AS avg_monthly_charge,
    ROUND(SUM(CASE WHEN ChurnFlag = 1 THEN MonthlyCharges END), 0)  AS monthly_revenue_lost
FROM customers
WHERE Contract = 'Month-to-month'
  AND InternetService = 'Fiber optic'
  AND TechSupport = 'No'
  AND tenure <= 12;

-- ---------------------------------------------------------------------
-- 8. Share of all churn contributed by each contract type
--    (uses a subquery, so it works on every MySQL version)
-- ---------------------------------------------------------------------
SELECT
    Contract,
    SUM(ChurnFlag) AS churned,
    ROUND(100.0 * SUM(ChurnFlag) / (SELECT SUM(ChurnFlag) FROM customers), 1) AS pct_of_all_churn
FROM customers
GROUP BY Contract
ORDER BY pct_of_all_churn DESC;

-- ---------------------------------------------------------------------
-- 9. Payment methods within each contract type, highest churn first
-- ---------------------------------------------------------------------
SELECT
    Contract,
    PaymentMethod,
    COUNT(*)                         AS customers,
    ROUND(100 * AVG(ChurnFlag), 1)   AS churn_rate_pct
FROM customers
GROUP BY Contract, PaymentMethod
ORDER BY Contract, churn_rate_pct DESC;

-- ---------------------------------------------------------------------
-- 10. Churn by monthly-charge band
-- ---------------------------------------------------------------------
SELECT
    CASE
        WHEN MonthlyCharges < 35 THEN '1: under 35'
        WHEN MonthlyCharges < 70 THEN '2: 35 to 70'
        WHEN MonthlyCharges < 90 THEN '3: 70 to 90'
        ELSE '4: 90 and above'
    END                              AS charge_band,
    COUNT(*)                         AS customers,
    ROUND(100 * AVG(ChurnFlag), 1)   AS churn_rate_pct
FROM customers
GROUP BY charge_band
ORDER BY charge_band;


-- ---------------------------------------------------------------------
-- 11. Why do customers leave? Top reasons given by churned customers
-- ---------------------------------------------------------------------
SELECT
    ChurnReason,
    COUNT(*) AS churned_customers,
    ROUND(100.0 * COUNT(*) / (SELECT SUM(ChurnFlag) FROM customers), 1) AS pct_of_churners
FROM customers
WHERE ChurnFlag = 1
GROUP BY ChurnReason
ORDER BY churned_customers DESC
LIMIT 10;

-- ---------------------------------------------------------------------
-- 12. Churned vs retained customers: value, price and tenure
-- ---------------------------------------------------------------------
SELECT
    Churn,
    COUNT(*)                         AS customers,
    ROUND(AVG(CLTV), 0)              AS avg_cltv,
    ROUND(AVG(MonthlyCharges), 2)    AS avg_monthly_charge,
    ROUND(AVG(tenure), 1)            AS avg_tenure_months
FROM customers
GROUP BY Churn;

-- ---------------------------------------------------------------------
-- 13. Cities with the highest churn (at least 50 customers)
-- ---------------------------------------------------------------------
SELECT
    City,
    COUNT(*)                         AS customers,
    ROUND(100 * AVG(ChurnFlag), 1)   AS churn_rate_pct
FROM customers
GROUP BY City
HAVING COUNT(*) >= 50
ORDER BY churn_rate_pct DESC
LIMIT 10;


-- =====================================================================
-- OPTIONAL - MySQL 8.0+ ONLY (window functions and CTE)
-- Run SELECT VERSION(); first. If it shows 8.x, remove the /* and */
-- around a query to use it. These are good to show in interviews.
-- =====================================================================

/*
-- 8b. Share of all churn per contract type (window function)
SELECT
    Contract,
    SUM(ChurnFlag) AS churned,
    ROUND(100.0 * SUM(ChurnFlag) / SUM(SUM(ChurnFlag)) OVER (), 1) AS pct_of_all_churn
FROM customers
GROUP BY Contract;

-- 9b. Rank payment methods by churn within each contract type
SELECT *
FROM (
    SELECT
        Contract,
        PaymentMethod,
        COUNT(*)                         AS customers,
        ROUND(100 * AVG(ChurnFlag), 1)   AS churn_rate_pct,
        RANK() OVER (PARTITION BY Contract ORDER BY AVG(ChurnFlag) DESC) AS churn_rank
    FROM customers
    GROUP BY Contract, PaymentMethod
) t
ORDER BY Contract, churn_rank;

-- 10b. Churn by monthly-charge quartile (CTE + NTILE)
WITH ranked AS (
    SELECT c.*, NTILE(4) OVER (ORDER BY MonthlyCharges) AS charge_quartile
    FROM customers c
)
SELECT
    charge_quartile,
    MIN(MonthlyCharges)              AS min_charge,
    MAX(MonthlyCharges)              AS max_charge,
    COUNT(*)                         AS customers,
    ROUND(100 * AVG(ChurnFlag), 1)   AS churn_rate_pct
FROM ranked
GROUP BY charge_quartile
ORDER BY charge_quartile;
*/
