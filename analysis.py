from dataclasses import dataclass
from typing import List

import argparse
import numpy as np
import pandas as pd

class Portfolio:
    def __init__(self):
        self.pure_spy = 0.0
        self.pure_spx = 0.0
        self.spy = 0.0
        self.spx = 0.0

    def invest(self, levered: bool, amount: float):
        if levered:
            self.spx += amount
        else:
            self.spy += amount

        self.pure_spx += amount
        self.pure_spy += amount

    def simulate_trading_day(self, sp500_pct_change: float, spx_pct_change: float):
        self.spy *= sp500_pct_change
        self.pure_spy *= sp500_pct_change

        self.spx *= spx_pct_change
        self.pure_spx *= spx_pct_change

    def __str__(self) -> str:
        return f"SPY: {self.pure_spy} | SPX: {self.pure_spx} | Heuristic: {self.spx + self.spy}"

parser = argparse.ArgumentParser(description='Volatility-based leverage simulation')
parser.add_argument('--holding_period_years', type=int, default=5, help='Simulation horizon in years (default: 5)')
args = parser.parse_args()

sp500 = pd.read_csv('SP500.csv', parse_dates=['observation_date'])
vix = pd.read_csv('VIXCLS.csv', parse_dates=['observation_date'])

df = sp500.merge(vix, on='observation_date', how='inner')
df = df.dropna(subset=['SP500', 'VIXCLS'])

df['VIXCLS_norm'] = (df['VIXCLS'] - df['VIXCLS'].min()) / (df['VIXCLS'].max() - df['VIXCLS'].min())

df['observation_date'] = pd.to_datetime(df['observation_date'])
df = df.sort_values('observation_date').reset_index(drop=True)

df['SP500_pct_change'] = df['SP500'].pct_change() + 1
df['SPX_pct_change'] =  3 * df['SP500'].pct_change() + 1

weights = np.array([1, 2, 3, 4, 5, 6, 7], dtype=float)
weights = weights / weights.sum()
df['VIXCLS_norm_7d_weighted'] = df['VIXCLS_norm'].rolling(window=7).apply(
    lambda x: np.dot(x, weights), raw=True
)

holding_period_years = args.holding_period_years
max_trading_days = holding_period_years * 252

years = df['observation_date'].dt.year.unique()
start_dates = []

for year in years:
    year_mask = df['observation_date'].dt.year == year
    year_dates = df.loc[year_mask, 'observation_date'].tolist()
    n = min(100, len(year_dates))
    selected = np.random.choice(year_dates, size=n, replace=False)
    if year <= 2026 - args.holding_period_years:
        start_dates.extend(selected)

start_dates.sort()

all_results = []

for vol_threshold in np.arange(15, 22, 2.5):
    results = []

    for start_date in start_dates:
        portfolio = Portfolio()
        subset = df[df['observation_date'] >= start_date].head(max_trading_days)

        for j, (i, row) in enumerate(subset.iterrows()):
            portfolio.simulate_trading_day(
                sp500_pct_change=row['SP500_pct_change'],
                spx_pct_change=row['SPX_pct_change']
            )

            if j % 14 == 0:
                levered = row['VIXCLS'] <= vol_threshold
                portfolio.invest(levered=levered, amount=1000)

        results.append({
            'start_date': start_date,
            'pure_spy': portfolio.pure_spy,
            'pure_spx': portfolio.pure_spx,
            'heuristic': portfolio.spx + portfolio.spy,
            'vol_threshold': vol_threshold,
        })

    all_results.append(pd.DataFrame(results))

sim_df = pd.concat(all_results, ignore_index=True)

print(f'\nTotal simulations: {len(sim_df)}')
print(f'Vol thresholds tested: {sorted(sim_df["vol_threshold"].unique())}')
print()

for threshold in sorted(sim_df['vol_threshold'].unique()):
    subset = sim_df[sim_df['vol_threshold'] == threshold]
    subset["delta"] = subset["heuristic"] - subset["pure_spy"]
    print(f'--- vol_threshold = {threshold:.2f} ---')
    print(f'  Max Underperformance: ${subset["delta"].min():,.2f}')
    print(f'  Avg delta (vs SPY): ${subset["delta"].mean():,.2f}')
    print(f'  Delta distribution:')
    print(f'    5th percentile:  ${subset["delta"].quantile(0.05):,.2f}')
    print(f'    25th percentile: ${subset["delta"].quantile(0.25):,.2f}')
    print(f'    50th percentile: ${subset["delta"].median():,.2f}')
    print(f'    75th percentile: ${subset["delta"].quantile(0.75):,.2f}')
    print(f'    95th percentile: ${subset["delta"].quantile(0.95):,.2f}')
    print(f'    Std deviation:   ${subset["delta"].std():,.2f}')
    print()


