# Leverage

Volatility-based leverage simulation using S&P 500 and VIX data.

## Overview

This project simulates a trading strategy that dynamically allocates between unlevered SPY and 3x leveraged SPX based on VIX levels. The core idea: reduce exposure to leverage when volatility (VIX) is elevated, and increase leverage when markets are calm.

Based on the papers cited in [Ben Felix's video](https://www.youtube.com/watch?v=E7pl0tqzIUQ) regarding leveraged ETFs.

## Strategy
Since the outcomes are highly timing dependent and the product may not be suitable for long term holding strategies in taxable accounts, simulate shorter 3 year periods
- **Unlevered position (SPY):** Default allocation, tracks the S&P 500 directly.
- **Levered position (SPX):** 3x leveraged exposure, activated when VIX falls below a configurable threshold.
- **Rebalancing:** Every 14 trading days, $1,000 is invested based on the current VIX signal.
- **Holding period:** Each simulation runs for 3 years.

## Data

| File | Description |
|---|---|
| `SP500.csv` | Daily S&P 500 index values (observation_date, SP500) |
| `VIXCLS.csv` | Daily CBOE VIX Close values (observation_date, VIXCLS) |

## Requirements

```bash
pip install -r requirements.txt
```

## Running

```bash
python analysis.py --holding_period_years 3
```

## Output

For each VIX threshold tested (15–35 in increments of 5), the script prints:

- **Max Underperformance:** Worst-case delta (heuristic − SPY benchmark)
- **Avg / Median delta:** Average and median outperformance vs. pure SPY
- **Delta distribution:** 5th, 25th, 50th, 75th, 95th percentiles and standard deviation

## Code Structure

| File | Purpose |
|---|---|
| `analysis.py` | Main simulation: data loading, feature engineering, Monte Carlo runs |
| `parse_sp500.py` | HTML parser to extract SP500 data from Yahoo Finance tables |
| `SP500.csv` | Historical S&P 500 prices |
| `VIXCLS.csv` | Historical VIX Close values |

## Key Parameters

| Parameter | Default | Description |
|---|---|---|
| `holding_period_years` | 5 | Max year for start dates |
| `max_trading_days` | 252 * holding_period_years | Simulation horizon |
| `vol_threshold` | 15–35 (step 5) | VIX level to trigger leverage |
| Investment freq | 14 days | Trading days between investments, roughly biweekly pay period investing. |
| Investment size | $1,000 | Amount per investment. |
