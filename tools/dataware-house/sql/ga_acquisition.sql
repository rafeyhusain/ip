IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES 
           WHERE TABLE_NAME = N'ga_acquisition')
BEGIN
  CREATE TABLE [ga_acquisition](
			ipg_batchNo                   VARCHAR(100),
			ga_bounces                    INT,
			ga_deviceCategory             VARCHAR(50),
			ga_goalCompletionsAll         INT,
			ga_landingPagePath            NVARCHAR(1024),
			ga_newUsers                   INT,
			ga_pageViews                  INT,
			ga_sessionDuration            INT,
			ga_sessions                   INT,
			ga_users                      INT,
			ipg_cc                        CHAR(2),
			ipg_date                      DATE,
			ipg_device                    NVARCHAR(50),
			ipg_level0Category            NVARCHAR(100),
			ipg_month                     INT,
			ipg_pageType                  NVARCHAR(300),
			ipg_product                   NVARCHAR(500),
			ipg_subProduct                NVARCHAR(500),
			ipg_website                   NVARCHAR(50),
			ipg_week                      INT,
			ipg_year                      INT,
			ipg_year_month                AS CONCAT(ipg_year, '-', RIGHT('0' + CAST(ipg_month AS VARCHAR(2)), 2)),
			ipg_year_week                 AS CONCAT(ipg_year, '-', RIGHT('0' + CAST(ipg_week AS VARCHAR(2)), 2)),

  )

END
GO

CREATE NONCLUSTERED INDEX date_index ON ga_acquisition  (ipg_date);
CREATE NONCLUSTERED INDEX year_index ON ga_acquisition  (ipg_year);
CREATE NONCLUSTERED INDEX month_index ON ga_acquisition  (ipg_month);
CREATE NONCLUSTERED INDEX week_index ON ga_acquisition  (ipg_week);
CREATE NONCLUSTERED INDEX year_week_index ON ga_acquisition  (ipg_year_week);
CREATE NONCLUSTERED INDEX year_month_index ON ga_acquisition  (ipg_year_month);
CREATE NONCLUSTERED INDEX cc_index ON ga_acquisition  (ipg_cc);
CREATE NONCLUSTERED INDEX product_index ON ga_acquisition  (ipg_product);
CREATE NONCLUSTERED INDEX level0Category_index ON ga_acquisition  (ipg_level0Category);
CREATE NONCLUSTERED INDEX device_index ON ga_acquisition  (ipg_device);
GO
