IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES 
           WHERE TABLE_NAME = N'ho_performance')
BEGIN
  CREATE TABLE [ho_performance](
			ipg_batchNo                   VARCHAR(100),
			ipg_affiliateNetwork          NVARCHAR(50),
			ipg_brand                     NVARCHAR(500),
			ipg_campaign                  NVARCHAR(500),
			ipg_catalogId                 NVARCHAR(100),
			ipg_category                  NVARCHAR(500),
			ipg_cc                        CHAR(2),
			ipg_channel                   NVARCHAR(100),
			ipg_commission                DECIMAL(38,25),
			ipg_cookieId                  NVARCHAR(100),
			ipg_couponCode                NVARCHAR(100),
			ipg_created                   DATETIME,
			ipg_currency                  CHAR(3),
			ipg_date                      DATE,
			ipg_dealType                  VARCHAR(3),
			ipg_device                    VARCHAR(50),
			ipg_discount                  NVARCHAR(100),
			ipg_download                  VARCHAR(50),
			ipg_exitUrl                   NVARCHAR(1024),
			ipg_features                  NVARCHAR(100),
			ipg_ip                        VARCHAR(50),
			ipg_landingUrl                NVARCHAR(1024),
			ipg_level0Category            NVARCHAR(50),
			ipg_logId                     CHAR(9),
			ipg_merchantId                NVARCHAR(500),
			ipg_merchantName              NVARCHAR(500),
			ipg_month                     INT,
			ipg_order                     INT,
			ipg_orderId                   NVARCHAR(500),
			ipg_orderValue                DECIMAL(38,25),
			ipg_originalCommission        DECIMAL(38,25),
			ipg_originalConversionId      NVARCHAR(100),
			ipg_originalCurrency          CHAR(3),
			ipg_originalOrderValue        DECIMAL(38,25),
			ipg_position                  INT,
			ipg_price                     DECIMAL(38,25),
			ipg_product                   NVARCHAR(500),
			ipg_productName               NVARCHAR(500),
			ipg_site                      NVARCHAR(50),
			ipg_sku                       NVARCHAR(100),
			ipg_source                    NVARCHAR(50),
			ipg_sourceAffiliate           NVARCHAR(50),
			ipg_status                    VARCHAR(50),
			ipg_subProduct                NVARCHAR(500),
			ipg_suspicious                NVARCHAR(100),
			ipg_time                      TIME,
			ipg_timestamp                 DECIMAL(38,25),
			ipg_userAgent                 NVARCHAR(100),
			ipg_userId                    NVARCHAR(100),
			ipg_week                      INT,
			ipg_year                      INT,
			ipg_year_month                AS CONCAT(ipg_year, '-', RIGHT('0' + CAST(ipg_month AS VARCHAR(2)), 2)),
			ipg_year_week                 AS CONCAT(ipg_year, '-', RIGHT('0' + CAST(ipg_week AS VARCHAR(2)), 2)),

  )

END
GO

CREATE NONCLUSTERED INDEX date_index ON ho_performance  (ipg_date);
CREATE NONCLUSTERED INDEX year_index ON ho_performance  (ipg_year);
CREATE NONCLUSTERED INDEX month_index ON ho_performance  (ipg_month);
CREATE NONCLUSTERED INDEX week_index ON ho_performance  (ipg_week);
CREATE NONCLUSTERED INDEX year_week_index ON ho_performance  (ipg_year_week);
CREATE NONCLUSTERED INDEX year_month_index ON ho_performance  (ipg_year_month);
CREATE NONCLUSTERED INDEX cc_index ON ho_performance  (ipg_cc);
CREATE NONCLUSTERED INDEX product_index ON ho_performance  (ipg_product);
CREATE NONCLUSTERED INDEX level0Category_index ON ho_performance  (ipg_level0Category);
CREATE NONCLUSTERED INDEX merchant_index ON ho_performance  (ipg_merchantName);
CREATE NONCLUSTERED INDEX device_index ON ho_performance  (ipg_device);
CREATE NONCLUSTERED INDEX dealType_index ON ho_performance  (ipg_dealType);
GO
