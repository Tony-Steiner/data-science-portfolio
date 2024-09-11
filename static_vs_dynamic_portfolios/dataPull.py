import os
import yfinance as yf
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from datetime import datetime, timedelta
import requests

pd.set_option("future.no_silent_downcasting", True)

# Tickers we'll use to pull data from Yahoo Finance
# 28 day mexican bond data (CETES) will be pulled from a different source
tickers = ["VT", "QQQ", "VOO", "VEA", "VWO", "FUNO11.MX"]

# Define start and end dates
start_date = "2011-01-01"
end_date = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")

# Define the folder path where you want to save the CSV files
save_folder = r"C:\Users\pale4\OneDrive\Documentos\GitHub\data-science-portfolio\static_vs_dynamic_portfolios\files"
os.makedirs(save_folder, exist_ok=True)

# Fetch the data for each ticker
data = {}
for ticker in tickers:
    df = yf.download(ticker, start=start_date, end=end_date)
    df.reset_index(inplace=True)
    df["Ticker"] = ticker
    data[ticker] = df


# Function to reindex DataFrame based on a specified date range
def reindex_data(data, start_date, end_date):
    date_range = pd.date_range(start=start_date, end=end_date, freq="B")
    reindexed_data = {}
    for ticker, df in data.items():
        df.set_index("Date", inplace=True)  # Set Date as index
        reindexed_df = df.reindex(date_range).bfill()  # Reindex and fill missing data
        reindexed_data[ticker] = reindexed_df
    return reindexed_data


# Apply the reindexing function to the data
reindexed_data = reindex_data(data, start_date, end_date)

# Pulling daily rates data of 28-day CETES
# Define your API key here
API_KEY = "566eec9f34b4126afd028c362657959b4669fbe8faa0a3cad9452411df0dfb1e"

# Base URL for Banxico API
base_url = "https://www.banxico.org.mx/SieAPIRest/service/v1/series/"

# Series ID for 28-day CETES
series_id = "SF43783"

# Full URL with parameters
url = f"{base_url}{series_id}/datos/{start_date}/{end_date}"

# Request headers with API key
headers = {"Bmx-Token": API_KEY}

# Make the API request
response = requests.get(url, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    data_cetes = response.json()

    # Extract relevant data
    dates = [item["fecha"] for item in data_cetes["bmx"]["series"][0]["datos"]]
    values = [float(item["dato"]) for item in data_cetes["bmx"]["series"][0]["datos"]]

    # Create a DataFrame
    cetes_df = pd.DataFrame({"Date": dates, "Rate": values})

    # Convert Date column to datetime format
    cetes_df["Date"] = pd.to_datetime(cetes_df["Date"], dayfirst=True)

cetes_df.set_index("Date", inplace=True)
cetes_df.index = pd.to_datetime(cetes_df.index)

date_range_cetes = pd.date_range(start=start_date, end=end_date, freq="B")
reindexed_cetes = cetes_df.reindex(date_range_cetes).bfill()  # fill missing data

# Rename the index to 'Date'
reindexed_cetes.index.name = "Date"

# Save data to local database pgadmin4

# Prepare Data for PostgreSQL
for ticker, df in reindexed_data.items():
    df["Date"] = df.index
    df["Date"] = pd.to_datetime(
        df["Date"]
    ).dt.date  # Convert index to Date column and format it

# Create an engine to connect to the PostgreSQL database in pgadmin4
engine = create_engine(
    "postgresql://tony_steiner:039804@localhost:5432/portfolio_analysis"
)


# Define a function to insert data into specific tables
def insert_data(ticker, df, engine):
    table_name = ""
    if ticker == "VOO":
        table_name = "usa_stocks"
    elif ticker == "QQQ":
        table_name = "usa_tech"
    elif ticker == "VT":
        table_name = "world_stocks"
    elif ticker == "VEA":
        table_name = "developed_economies"
    elif ticker == "VWO":
        table_name = "developing_economies"
    elif ticker == "FUNO11.MX":
        table_name = "real_estate"
    df.to_sql(table_name, engine, if_exists="replace", index=False)


# Insert data for each ticker (calling the function)
for ticker, df in reindexed_data.items():
    insert_data(ticker, df, engine)

# For CETES data
reindexed_cetes.reset_index(inplace=True)
reindexed_cetes[["Date", "Rate"]].to_sql(
    "cetes28", engine, if_exists="replace", index=False
)


# Define a function to fetch data for a given asset
def fetch_asset_data(ticker, engine):
    table_mapping = {
        "VOO": "usa_stocks",
        "QQQ": "usa_tech",
        "VT": "world_stocks",
        "VEA": "developed_economies",
        "VWO": "developing_economies",
        "FUNO11.MX": "real_estate",
    }

    if ticker in table_mapping:
        table_name = table_mapping[ticker]
        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql(query, engine)
        df["Date"] = pd.to_datetime(df["Date"])
        return df
    else:
        raise ValueError(f"Ticker {ticker} is not recognized.")


# Dictionary to store the DataFrames
dataframes = {}

# Fetch data for each asset and store in the dictionary
for ticker in tickers:
    dataframes[ticker] = fetch_asset_data(ticker, engine)

# Fetch CETES data from table and into the dictionary
cetes_df = pd.read_sql('SELECT "Date", "Rate" FROM cetes28', engine)
cetes_df["Date"] = pd.to_datetime(cetes_df["Date"])
cetes_df["Rate"] = cetes_df["Rate"] / 100

# Save each DataFrame from the dictionary to individual CSV files
for ticker, df in dataframes.items():
    # Determine the filename based on their ticker
    if ticker == "VOO":
        filename = "df_voo.csv"
    elif ticker == "QQQ":
        filename = "df_qqq.csv"
    elif ticker == "VT":
        filename = "df_vt.csv"
    elif ticker == "VEA":
        filename = "df_vea.csv"
    elif ticker == "VWO":
        filename = "df_vwo.csv"
    elif ticker == "FUNO11.MX":
        filename = "df_funo11.csv"

    # Save the DataFrame to a CSV file in the specified folder
    df.to_csv(os.path.join(save_folder, filename), index=False)

# Save CETES DataFrame to a CSV file
cetes_filename = "df_cetes.csv"
cetes_df.to_csv(os.path.join(save_folder, cetes_filename), index=False)

# Define the path for the combined Excel file
combined_excel_filename = os.path.join(save_folder, "combined_data.xlsx")

# Create an Excel writer object
with pd.ExcelWriter(combined_excel_filename, engine="xlsxwriter") as writer:
    # Save each DataFrame from the dictionary to a separate sheet
    for ticker, df in dataframes.items():
        sheet_name = ""
        if ticker == "VOO":
            sheet_name = "df_voo"
        elif ticker == "QQQ":
            sheet_name = "df_qqq"
        elif ticker == "VT":
            sheet_name = "df_vt"
        elif ticker == "VEA":
            sheet_name = "df_vea"
        elif ticker == "VWO":
            sheet_name = "df_vwo"
        elif ticker == "FUNO11.MX":
            sheet_name = "df_funo11"

        # Write the DataFrame to a specific sheet
        df.to_excel(writer, sheet_name=sheet_name, index=False)

    # Save CETES DataFrame to a separate sheet
    cetes_df.to_excel(writer, sheet_name="df_cetes", index=False)

print("All DataFrames have been saved to separate sheets in a single Excel file.")
