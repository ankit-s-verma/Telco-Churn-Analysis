from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
import pandas as pd
from sqlalchemy import text

load_dotenv()

telco_df = pd.read_csv('Updated_Churn_Analysis_Dataset.csv')

PASSWORD = os.getenv('PASSWORD')
if not PASSWORD:
    raise ValueError("PASSWORD not set in environment")

username = "postgres"
password = PASSWORD
host = "127.0.0.1"
port = "5432"
database = "telco_db"

# Create engine
engine = create_engine(
    f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}"
)

print("Connection successful!")

telco_df.to_sql(
    name = 'telco_churn',
    con = engine,
    if_exists='replace', #'replace',        #if re-uploading, use append instead
    index=False
)
print("Data upload successfully")

def create_views(view_name, query):
    with engine.begin() as conn:
        conn.execute(text(query))

    print(f"{view_name} view created successfully!")

query_list = {
    "churn_summary": """
    CREATE OR REPLACE VIEW churn_summary AS
    SELECT
        COUNT(*) AS total_customers,

        ROUND(
            (100 *
                SUM(CASE WHEN "Churn" = 'Yes' THEN 1 ELSE 0 END)::NUMERIC
                / COUNT(*)
            ),
            2
        ) AS churn_rate,

        ROUND(
            SUM("MonthlyCharges")::NUMERIC,
            2
        ) AS monthly_revenue,

        ROUND(
            SUM(
                CASE
                    WHEN "Churn" = 'Yes'
                    THEN "MonthlyCharges"
                    ELSE 0
                END
            )::NUMERIC,
            2
        ) AS revenue_lost

    FROM telco_churn;
    """,

    "churn_by_contract": """
    CREATE OR REPLACE VIEW churn_by_contract AS
    SELECT
        "Contract",
        COUNT(*) AS customers,
        ROUND(
            100.0 *
            SUM(
                CASE
                    WHEN "Churn" = 'Yes'
                    THEN 1
                    ELSE 0
                END
            ) / COUNT(*),
            2
        ) AS churn_rate
    FROM telco_churn
    GROUP BY "Contract";
    """,

    "churn_by_internet": """
    CREATE OR REPLACE VIEW churn_by_internet AS
    SELECT
        "InternetService",
        COUNT(*) AS customers,
        ROUND(
            100.0 *
            SUM(
                CASE
                    WHEN "Churn" = 'Yes'
                    THEN 1
                    ELSE 0
                END
            ) / COUNT(*),
            2
        ) AS churn_rate
    FROM telco_churn
    GROUP BY "InternetService";
    """,

    "revenue_by_contract": """
    CREATE OR REPLACE VIEW revenue_by_contract AS
    SELECT
        "Contract",
        ROUND(SUM("TotalCharges")::NUMERIC, 2) AS revenue
    FROM telco_churn
    GROUP BY "Contract"
    ORDER BY revenue DESC;
    """,

    "churn_by_payment": """
    CREATE OR REPLACE VIEW churn_by_payment AS
    SELECT
        "PaymentMethod",
        COUNT(*) AS customers,
        ROUND(
            100.0 *
            SUM(
                CASE
                    WHEN "Churn" = 'Yes'
                    THEN 1
                    ELSE 0
                END
            ) / COUNT(*),
            2
        ) AS churn_rate
    FROM telco_churn
    GROUP BY "PaymentMethod"
    ORDER BY churn_rate DESC;
    """,

    "customer_segments": """
    CREATE OR REPLACE VIEW customer_segments AS
    SELECT
        "TenureGroup",
        COUNT(*) AS customers,

        ROUND(
            AVG("MonthlyCharges")::NUMERIC,
            2
        ) AS avg_monthly_charge,

        ROUND(
            SUM("TotalCharges")::NUMERIC,
            2
        ) AS revenue

    FROM telco_churn
    GROUP BY "TenureGroup";
    """
}


for name, sql_query in query_list.items():
    create_views(name, sql_query)