# Static vs. Dynamic Portfolio Analysis

## Overview

This project investigates the impact of dynamic rebalancing on portfolio performance compared to static asset allocation strategies. Using 13 years of financial data, the analysis focuses on risk-adjusted returns (Sortino ratio) to evaluate the effectiveness of dynamic rebalancing across different asset configurations. The project demonstrates Python skills for data collection, cleaning, analysis, and visualization, while also showcasing an understanding of financial concepts and hypothesis testing.

## Table of Contents

1. [Project Motivation](#project-motivation)
2. [Hypothesis](#hypothesis)
3. [Features](#features)
4. [Data Description](#data-description)
5. [Methodology](#methodology) 
6. [Results](#results)
7. [Installation](#installation)
8. [Usage](#usage)

## Project Motivation

Understanding the potential benefits of dynamic rebalancing in portfolio management is crucial for investors seeking to optimize risk-adjusted returns. This project aims to test the hypothesis that dynamic rebalancing, using the 1/10 rule, leads to superior performance compared to static allocations. The findings contribute to the ongoing discussion on the effectiveness of active portfolio management strategies. 

## Hypothesis

**Primary Hypothesis:** 

* Portfolios with dynamic rebalancing (using the 1/10 rule) will outperform portfolios with static allocations in terms of risk-adjusted returns (Sortino ratio) over the 13-year period.

## Features

- **Portfolio Construction:** Implements both static and dynamic portfolios based on the Swensen model with varying asset allocations.
- **Performance Evaluation:** Calculates key metrics including annual returns, volatility, Sortino ratio, and maximum drawdown.
- **Data Visualization:** Presents clear visual comparisons of portfolio performance and includes a summary table of key metrics.
- **Hypothesis Testing:** Evaluates the primary hypothesis and provides insights into the impact of dynamic rebalancing.
- **Dynamic Portfolio Analysis:** Assesses portfolios with annual rebalancing following the 1/10 Rule. This rule suggests allocating 110 minus your age as a percentage to equities and the remainder to fixed income, adjusting annually.
- **Strategy:** Portfolios are constructed following a simplified version of the Swensen model, which emphasizes diversification across asset classes. The model typically includes allocations to domestic and international equities, bonds, real estate, and commodities. In this project, we adapt the model to include U.S. equities, international equities, and Mexican assets (Fibra Uno and CETES).

## Data Description

The project utilizes historical financial data from 2011 to 2024, sourced from Yahoo Finance and Banxico:

- **U.S. Equities:**
    - VOO (Vanguard S&P 500 ETF)
    - QQQ (Invesco QQQ ETF)
    - VT (Vanguard Total World Stock ETF)
- **International Equities:**
    - VEA (Vanguard FTSE Developed Markets ETF)
    - VWO (Vanguard FTSE Emerging Markets ETF)
- **Mexican Assets:**
    - FUNO11.MX (Fibra Uno)
    - CETES (28-day Mexican bonds)

## Methodology

1. **Data Collection and Cleaning**: 
    - Download data using `yfinance` and Banxico API.
    - Clean and preprocess data, ensuring consistency and handling missing values.
    - Store data in a local database (pgAdmin4) for future use.

2. **Portfolio Construction**:
    - Define static and dynamic portfolios with different asset configurations based on the Swensen model.
    - Implement dynamic rebalancing using the 1/10 rule.

3. **Performance Analysis**: 
    - Calculate annual returns, cumulative returns, annual volatility, max drawdown, and Sortino ratio for each portfolio.

4. **Hypothesis Testing**: 
    - Compare Sortino ratios between static and dynamic portfolios to evaluate the hypothesis.

5. **Visualization**:
    - Create visualizations to illustrate cumulative returns, max drawdown, annual returns, volatility, and the comparison of Sortino ratios.

## Results

The analysis supports the hypothesis that dynamic rebalancing leads to better risk-adjusted returns, as measured by the Sortino ratio, compared to static asset allocation. Across all three asset configurations (qqq, voo, and vt), the dynamic strategy consistently outperformed the static strategy in terms of Sortino ratio.

Asset       Configuration	Difference in Sortino Ratio (dynamic - static)
QQQ	        0.088
VOO	        0.089
VT	        0.081

This suggests that actively managing portfolio allocations through rebalancing can enhance risk-adjusted performance. However, it's important to note that the dynamic strategies also exhibited higher maximum drawdowns compared to their static counterparts.

This observation highlights a potential trade-off between risk and return. While dynamic rebalancing can improve risk-adjusted returns, it might also come with the possibility of larger drawdowns during certain market conditions. The suitability of a dynamic strategy depends on an investor's risk tolerance.

Further analysis is warranted to explore the relationship between dynamic rebalancing and max drawdowns. This could involve examining the timing of rebalancing events relative to market downturns, analyzing the behavior of individual asset classes within the portfolios, and extending the analysis to different time periods.

Overall, the results provide valuable insights into the potential benefits and trade-offs of dynamic rebalancing. While the strategy shows promise in enhancing risk-adjusted returns, it's crucial to consider the potential for increased drawdowns and align the strategy with an investor's risk profile.

## Installation 

This project requires the following Python libraries:

- xlsxwriter
- matplotlib
- openpyxl
- yfinance
- sqlalchemy
- psycopg2

You can install these libraries using pip.

## Usage

*Data*

The necessary data files (CSV and XLSX) are already included in the "files" folder of this repository. You do not need to run any data collection scripts.

*Configuration*

Before running the analysis, you'll need to edit the analysis.py file to specify the correct path to your local "files" folder.