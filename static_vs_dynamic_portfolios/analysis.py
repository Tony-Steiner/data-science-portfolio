import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import os


# Define the path for the combined Excel file
save_folder = r"C:\Users\pale4\OneDrive\Documentos\GitHub\data-science-portfolio\static_vs_dynamic_portfolios\files"
save_folder_images = r"C:\Users\pale4\OneDrive\Documentos\GitHub\data-science-portfolio\static_vs_dynamic_portfolios\images"
combined_excel_filename = os.path.join(save_folder, "combined_data.xlsx")

# Read data from each sheet into a dictionary of DataFrames
sheets = ["df_voo", "df_qqq", "df_vt", "df_vea", "df_vwo", "df_funo11", "df_cetes"]

# Create a dictionary to store the DataFrames
dataframes = {}

# Load each sheet into a DataFrame
for sheet in sheets:
    dataframes[sheet] = pd.read_excel(combined_excel_filename, sheet_name=sheet)


# Access individual DataFrames
df_voo = dataframes["df_voo"]
df_qqq = dataframes["df_qqq"]
df_vt = dataframes["df_vt"]
df_vea = dataframes["df_vea"]
df_vwo = dataframes["df_vwo"]
df_funo11 = dataframes["df_funo11"]
df_cetes = dataframes["df_cetes"]

# From the "df_cetes" DataFrame, we rename the 'Rate' column to 'Adj Close' to make the calculation of returns easier.
df_cetes.rename(columns={"Rate": "Adj Close"}, inplace=True)


# Define a function to calculate daily returns and add it as a new column
def calculate_daily_returns(df):
    df["Returns"] = df["Adj Close"].pct_change(fill_method=None)
    return df


# Apply the function to each DataFrame in the dictionary
for ticker, df in dataframes.items():
    dataframes[ticker] = calculate_daily_returns(df)


# We merge the 'Date' and 'Returns' data into single portfolio DataFrames according to the 3 portfolio configurations

# For portfolio with VOO, VEA, VWO, FUNO11.MX and CETES
portfolio_voo = pd.merge(
    df_voo[["Date", "Returns"]],
    df_vea[["Date", "Returns"]],
    on="Date",
    how="outer",
    suffixes=("_voo", "_vea"),
)

portfolio_voo = pd.merge(
    portfolio_voo,
    df_vwo[["Date", "Returns"]],
    on="Date",
    how="outer",
    suffixes=("", "_vwo"),
)

portfolio_voo = pd.merge(
    portfolio_voo,
    df_funo11[["Date", "Returns"]],
    on="Date",
    how="outer",
    suffixes=("", "_funo"),
)

portfolio_voo = pd.merge(
    portfolio_voo,
    df_cetes[["Date", "Returns"]],
    on="Date",
    how="outer",
    suffixes=("", "_cetes"),
).dropna()

portfolio_voo.rename(columns={"Returns": "Returns_vwo"}, inplace=True)


# For portfolio with QQQ, VEA, VWO, FUNO11.MX and CETES
portfolio_qqq = pd.merge(
    df_qqq[["Date", "Returns"]],
    df_vea[["Date", "Returns"]],
    on="Date",
    how="outer",
    suffixes=("_qqq", "_vea"),
)

portfolio_qqq = pd.merge(
    portfolio_qqq,
    df_vwo[["Date", "Returns"]],
    on="Date",
    how="outer",
    suffixes=("", "_vwo"),
)

portfolio_qqq = pd.merge(
    portfolio_qqq,
    df_funo11[["Date", "Returns"]],
    on="Date",
    how="outer",
    suffixes=("", "_funo"),
)

portfolio_qqq = pd.merge(
    portfolio_qqq,
    df_cetes[["Date", "Returns"]],
    on="Date",
    how="outer",
    suffixes=("", "_cetes"),
).dropna()

portfolio_qqq.rename(columns={"Returns": "Returns_vwo"}, inplace=True)


# For portfolio with VT, FUNO11.MX and CETES
portfolio_vt = pd.merge(
    df_vt[["Date", "Returns"]],
    df_funo11[["Date", "Returns"]],
    on="Date",
    how="outer",
    suffixes=("_vt", "_funo"),
)

portfolio_vt = pd.merge(
    portfolio_vt,
    df_cetes[["Date", "Returns"]],
    on="Date",
    how="outer",
    suffixes=("", "_cetes"),
).dropna()

portfolio_vt.rename(columns={"Returns": "Returns_cetes"}, inplace=True)


# Set 'Date' as index for each portfolio configuration
portfolios = [portfolio_voo, portfolio_qqq, portfolio_vt]

for portfolio in portfolios:
    portfolio.set_index("Date", inplace=True)


# We begin the portfolio analysis
# We start with the static analysis of VOO configuration

# We define the portfolio weights according to Swensen's model
weights = [0.30, 0.15, 0.05, 0.20, 0.30]

# Calculate weighted returns
weighted_returns_voo = portfolio_voo.mul(weights, axis=1)

# We add the returns on each row to get the total returns per day
static_returns_voo = weighted_returns_voo.sum(axis=1)


# Next is the dynamic portfolio analysis
# Assuming initial investment at age 20 (2011)
# Following the 110 rule: 110 - 20 = 90
# 90% of portfolio should be composed of stocks and 10% of bonds

# initial asset allocations at the beginning of the period
weights_voo = {"VOO": 0.30, "VEA": 0.15, "VWO": 0.05, "FUNO11.MX": 0.20, "CETES": 0.30}

# Convert weights to DataFrame for easy adjustment
weights_voo_df = pd.DataFrame.from_dict(
    weights_voo, orient="index", columns=["weights"]
)

# Generate a list of dates starting from 2011 to the present year
period = pd.date_range(
    start="2011-01-01", end=datetime.today().strftime("%Y-%m-%d"), freq="B"
)

# initialize DataFrame for portfolio returns
dynamic_returns_voo = pd.Series(index=period)

num_years = 2024 - 2011

# Adjust weights annually
for year in range(num_years):
    year_start = f"{2011 + year}-01-01"
    year_end = f"{2024 + year}-12-31"

    if year_end not in portfolio_voo.index:
        year_end = portfolio_voo.index[-1].strftime("%Y-%m-%d")

    # Subset returns for each year
    annual_returns_voo = portfolio_voo.loc[year_start:year_end]

    # Calculate weighted returns
    weight_returns_annual_voo = annual_returns_voo.mul(
        weights_voo_df["weights"].values, axis=1
    )
    sum_returns_voo = weight_returns_annual_voo.sum(axis=1)

    # Store the returns in dynamic_returns_voo
    dynamic_returns_voo.loc[year_start:year_end] = sum_returns_voo

    # Adjust weights
    weights_voo["VOO"] -= 0.0025
    weights_voo["VEA"] -= 0.0025
    weights_voo["VWO"] -= 0.0025
    weights_voo["FUNO11.MX"] -= 0.0025
    weights_voo["CETES"] += 0.01

    # Update weights DataFrame
    weights_voo_df = pd.DataFrame.from_dict(
        weights_voo, orient="index", columns=["weights"]
    )


# Static analysis of QQQ configuration
# Calculate weighted returns
weighted_returns_qqq = portfolio_qqq.mul(weights, axis=1)

# We add the returns on each row to get the total returns per day
static_returns_qqq = weighted_returns_qqq.sum(axis=1)


# Next is the dynamic portfolio analysis of QQQ configuration
# initial asset allocations at the beginning of the period
weights_qqq = {"QQQ": 0.30, "VEA": 0.15, "VWO": 0.05, "FUNO11.MX": 0.20, "CETES": 0.30}

# Convert weights to DataFrame for easy adjustment
weights_qqq_df = pd.DataFrame.from_dict(
    weights_qqq, orient="index", columns=["weights"]
)

# initialize DataFrame for portfolio returns
dynamic_returns_qqq = pd.Series(index=period)

# Adjust weights annually
for year in range(num_years):
    year_start = f"{2011 + year}-01-01"
    year_end = f"{2024 + year}-12-31"

    if year_end not in portfolio_qqq.index:
        year_end = portfolio_qqq.index[-1].strftime("%Y-%m-%d")

    # Subset returns for each year
    annual_returns_qqq = portfolio_qqq.loc[year_start:year_end]

    # Calculate weighted returns
    weight_returns_annual_qqq = annual_returns_qqq.mul(
        weights_qqq_df["weights"].values, axis=1
    )
    sum_returns_qqq = weight_returns_annual_qqq.sum(axis=1)

    # Store the returns in dynamic_returns_voo
    dynamic_returns_qqq.loc[year_start:year_end] = sum_returns_qqq

    # Adjust weights
    weights_qqq["QQQ"] -= 0.0025
    weights_qqq["VEA"] -= 0.0025
    weights_qqq["VWO"] -= 0.0025
    weights_qqq["FUNO11.MX"] -= 0.0025
    weights_qqq["CETES"] += 0.01

    # Update weights DataFrame
    weights_qqq_df = pd.DataFrame.from_dict(
        weights_qqq, orient="index", columns=["weights"]
    )


# Static analysis of VT configuration
weights_vt = [0.50, 0.20, 0.30]

# Calculate weighted returns
weighted_returns_vt = portfolio_vt.mul(weights_vt, axis=1)

# We add the returns on each row to get the total returns per day
static_returns_vt = weighted_returns_vt.sum(axis=1)


# Next is the dynamic portfolio analysis of QQQ configuration
# initial asset allocations at the beginning of the period
weights_dynamic_vt = {"VT": 0.50, "FUNO11.MX": 0.20, "CETES": 0.30}

# Convert weights to DataFrame for easy adjustment
weights_vt_df = pd.DataFrame.from_dict(
    weights_dynamic_vt, orient="index", columns=["weights"]
)

# initialize DataFrame for portfolio returns
dynamic_returns_vt = pd.Series(index=period)

# Adjust weights annually
for year in range(num_years):
    year_start = f"{2011 + year}-01-01"
    year_end = f"{2024 + year}-12-31"

    if year_end not in portfolio_vt.index:
        year_end = portfolio_vt.index[-1].strftime("%Y-%m-%d")

    # Subset returns for each year
    annual_returns_vt = portfolio_vt.loc[year_start:year_end]

    # Calculate weighted returns
    weight_returns_annual_vt = annual_returns_vt.mul(
        weights_vt_df["weights"].values, axis=1
    )
    sum_returns_vt = weight_returns_annual_vt.sum(axis=1)

    # Store the returns in dynamic_returns_voo
    dynamic_returns_vt.loc[year_start:year_end] = sum_returns_vt

    # Adjust weights
    weights_dynamic_vt["VT"] -= 0.0050
    weights_dynamic_vt["FUNO11.MX"] -= 0.0050
    weights_dynamic_vt["CETES"] += 0.01

    # Update weights DataFrame
    weights_vt_df = pd.DataFrame.from_dict(
        weights_dynamic_vt, orient="index", columns=["weights"]
    )


# To calculate the required metrics for each portfolio we first need to define helper functions.


# Annual returns
def calculate_annual_returns(returns):
    annual_returns = returns.mean() * 252
    return annual_returns


# Cumulative returns
def calculate_cumulative_returns(returns):
    cumulative_returns = (1 + returns).cumprod() - 1
    return cumulative_returns


# Annual volatility
def calculate_annual_volatility(returns):
    annual_volatility = returns.std() * np.sqrt(252)
    return annual_volatility


# Max drawdown
def calculate_max_drawdown(returns):
    cumulative_returns = calculate_cumulative_returns(returns)
    peak = cumulative_returns.cummax()
    drawdown = (cumulative_returns - peak) / peak
    max_drawdown = drawdown.min()
    return max_drawdown


# Sortino Ratio (annualized)
def calculate_sortino_ratio(returns, risk_free_rate=0.0):
    downside_returns = returns[returns < 0]
    expected_return = returns.mean() * 252
    downside_deviation = downside_returns.std() * np.sqrt(252)
    sortino_ratio = (expected_return - risk_free_rate) / downside_deviation
    return sortino_ratio


# Define the summary function that uses the helper functions
def portfolio_summary(returns, name, risk_free_rate=0.0):
    annual_returns = calculate_annual_returns(returns)
    cumulative_returns = calculate_cumulative_returns(returns)
    annual_volatility = calculate_annual_volatility(returns)
    max_drawdown = calculate_max_drawdown(returns)
    sortino_ratio = calculate_sortino_ratio(returns, risk_free_rate)

    summary = {
        "Portfolio": name,
        "Annual Returns": annual_returns.mean(),
        "Cumulative Returns": cumulative_returns.iloc[-1],
        "Annual Volatility": annual_volatility,
        "Max Drawdown": max_drawdown,
        "Sortino Ratio": sortino_ratio,
    }

    print(f"Summary for {name}:")
    print(f"Annual Returns: {summary['Annual Returns']:.3%}")
    print(f"Cumulative Returns: {summary['Cumulative Returns']:.3%}")
    print(f"Annual Volatility: {summary['Annual Volatility']:.3%}")
    print(f"Max Drawdown: {summary['Max Drawdown']:.3%}")
    print(f"Sortino Ratio: {summary['Sortino Ratio']:.3f}")
    print()

    return summary


# apply the summary function to each portfolio
summaries = []

static_summaries = {
    "static_returns_voo": static_returns_voo,
    "static_returns_qqq": static_returns_qqq,
    "static_returns_vt": static_returns_vt,
}

dynamic_summaries = {
    "dynamic_returns_voo": dynamic_returns_voo.ffill().bfill(),
    "dynamic_returns_qqq": dynamic_returns_qqq.ffill().bfill(),
    "dynamic_returns_vt": dynamic_returns_vt.ffill().bfill(),
}

for name, returns in static_summaries.items():
    summaries.append(portfolio_summary(returns, name, risk_free_rate=0.0))

for name, returns in dynamic_summaries.items():
    summaries.append(portfolio_summary(returns, name, risk_free_rate=0.0))

# Visualizations

static_colors = ["#1E90FF", "#0000CD", "#ADD8E6"]
dynamic_colors = ["#FFA500", "#FF8C00", "#FFD700"]

plt.figure(figsize=(14, 7))
plt.plot((1 + static_returns_voo).cumprod(), label="Static VOO", color=static_colors[0])
plt.plot((1 + static_returns_qqq).cumprod(), label="Static QQQ", color=static_colors[1])
plt.plot((1 + static_returns_vt).cumprod(), label="Static VT", color=static_colors[2])
plt.legend()
plt.title("Cumulative Returns of Static Portfolios")
plt.xlabel("Date")
plt.ylabel("Cumulative Returns")
plt.grid(True)
plt.savefig(
    r"C:\Users\pale4\OneDrive\Documentos\GitHub\data-science-portfolio\static_vs_dynamic_portfolios\images\cumulative_returns_static.png"
)
plt.show()


plt.figure(figsize=(14, 7))
plt.plot(
    (1 + dynamic_returns_voo).cumprod(), label="Dynamic VOO", color=dynamic_colors[0]
)
plt.plot(
    (1 + dynamic_returns_qqq).cumprod(), label="Dynamic QQQ", color=dynamic_colors[1]
)
plt.plot(
    (1 + dynamic_returns_vt).cumprod(), label="Dynamic VT", color=dynamic_colors[2]
)
plt.legend()
plt.title("Cumulative Returns of Dynamic Portfolios")
plt.xlabel("Date")
plt.ylabel("Cumulative Returns")
plt.grid(True)
plt.savefig(
    r"C:\Users\pale4\OneDrive\Documentos\GitHub\data-science-portfolio\static_vs_dynamic_portfolios\images\cumulative_returns_dynamic.png"
)
plt.show()


plt.figure(figsize=(14, 7))
plt.plot((1 + static_returns_voo).cumprod(), label="Static VOO", color=static_colors[0])
plt.plot((1 + static_returns_qqq).cumprod(), label="Static QQQ", color=static_colors[1])
plt.plot((1 + static_returns_vt).cumprod(), label="Static VT", color=static_colors[2])
plt.plot(
    (1 + dynamic_returns_voo).cumprod(), label="Dynamic VOO", color=dynamic_colors[0]
)
plt.plot(
    (1 + dynamic_returns_qqq).cumprod(), label="Dynamic QQQ", color=dynamic_colors[1]
)
plt.plot(
    (1 + dynamic_returns_vt).cumprod(), label="Dynamic VT", color=dynamic_colors[2]
)
plt.legend()
plt.title("Cumulative Returns of Portfolios")
plt.xlabel("Date")
plt.ylabel("Cumulative Returns")
plt.grid(True)
plt.savefig(
    r"C:\Users\pale4\OneDrive\Documentos\GitHub\data-science-portfolio\static_vs_dynamic_portfolios\images\cumulative_returns_all.png"
)
plt.show()


annual_returns_df = pd.concat(
    [
        static_returns_voo.resample("YE")
        .apply(lambda x: np.prod(1 + x) - 1)
        .rename("Static VOO"),
        static_returns_qqq.resample("YE")
        .apply(lambda x: np.prod(1 + x) - 1)
        .rename("Static QQQ"),
        static_returns_vt.resample("YE")
        .apply(lambda x: np.prod(1 + x) - 1)
        .rename("Static VT"),
        dynamic_returns_voo.resample("YE")
        .apply(lambda x: np.prod(1 + x) - 1)
        .rename("Dynamic VOO"),
        dynamic_returns_qqq.resample("YE")
        .apply(lambda x: np.prod(1 + x) - 1)
        .rename("Dynamic QQQ"),
        dynamic_returns_vt.resample("YE")
        .apply(lambda x: np.prod(1 + x) - 1)
        .rename("Dynamic VT"),
    ],
    axis=1,
)

# Format the date index to show only the year
annual_returns_df.index = annual_returns_df.index.year

annual_returns_df.plot(kind="bar", figsize=(14, 7))
plt.title("Annual Returns of Portfolios")
plt.xlabel("Year")
plt.ylabel("Annual Return")
plt.grid(True)
plt.savefig(
    r"C:\Users\pale4\OneDrive\Documentos\GitHub\data-science-portfolio\static_vs_dynamic_portfolios\images\annual_returns.png"
)
plt.show()


rolling_volatility_df = pd.DataFrame(
    {
        "Static VOO": static_returns_voo.rolling(window=252).std() * np.sqrt(252),
        "Static QQQ": static_returns_qqq.rolling(window=252).std() * np.sqrt(252),
        "Static VT": static_returns_vt.rolling(window=252).std() * np.sqrt(252),
        "Dynamic VOO": dynamic_returns_voo.rolling(window=252).std() * np.sqrt(252),
        "Dynamic QQQ": dynamic_returns_qqq.rolling(window=252).std() * np.sqrt(252),
        "Dynamic VT": dynamic_returns_vt.rolling(window=252).std() * np.sqrt(252),
    }
)

rolling_volatility_df.plot(figsize=(14, 7))
plt.title("Rolling Annual Volatility of Portfolios")
plt.xlabel("Date")
plt.ylabel("Annual Volatility")
plt.grid(True)
plt.savefig(
    r"C:\Users\pale4\OneDrive\Documentos\GitHub\data-science-portfolio\static_vs_dynamic_portfolios\images\rolling_volatility.png"
)
plt.show()


def drawdown(return_series):
    cumulative = (1 + return_series).cumprod()
    peak = cumulative.cummax()
    drawdown = (cumulative - peak) / peak
    return drawdown


drawdown_static_df = pd.DataFrame(
    {
        "Static VOO": drawdown(static_returns_voo),
        "Static QQQ": drawdown(static_returns_qqq),
        "Static VT": drawdown(static_returns_vt),
    }
)

drawdown_dynamic_df = pd.DataFrame(
    {
        "Dynamic VOO": drawdown(dynamic_returns_voo),
        "Dynamic QQQ": drawdown(dynamic_returns_qqq),
        "Dynamic VT": drawdown(dynamic_returns_vt),
    }
)

drawdown_static_df.plot(figsize=(14, 7))
plt.title("Drawdown of Static Portfolios")
plt.xlabel("Date")
plt.ylabel("Drawdown")
plt.grid(True)
plt.savefig(
    r"C:\Users\pale4\OneDrive\Documentos\GitHub\data-science-portfolio\static_vs_dynamic_portfolios\images\drawdown_static.png"
)
plt.show()

drawdown_dynamic_df.plot(figsize=(14, 7))
plt.title("Drawdown of Dynamic Portfolios")
plt.xlabel("Date")
plt.ylabel("Drawdown")
plt.grid(True)
plt.savefig(
    r"C:\Users\pale4\OneDrive\Documentos\GitHub\data-science-portfolio\static_vs_dynamic_portfolios\images\drawdown_dynamic.png"
)
plt.show()


# Convert the summaries to a DataFrame
summary_df = pd.DataFrame(summaries)

# Round the numbers to 3 decimal places
summary_df = summary_df.round(3)


# Function to plot and save summary as image
def plot_summary_table(summary_df, filename):
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.axis("tight")
    ax.axis("off")
    table = ax.table(
        cellText=summary_df.values,
        colLabels=summary_df.columns,
        cellLoc="center",
        loc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1.2, 1.2)
    plt.savefig(filename, bbox_inches="tight", pad_inches=0.1)
    plt.close()


# Define the path to save the summary image
summary_image_filename = os.path.join(save_folder_images, "portfolio_summaries.png")

# Plot and save the summary DataFrame as an image
plot_summary_table(summary_df, summary_image_filename)

print(f"Summaries exported to {summary_image_filename}")


# Define the path to save the summary file
summary_excel_filename = os.path.join(save_folder, "portfolio_summaries.xlsx")

# Save the summary DataFrame to an Excel file
summary_df.to_excel(summary_excel_filename, index=False)

print(f"Summaries exported to {summary_excel_filename}")
