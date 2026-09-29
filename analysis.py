from dataclasses import dataclass
from typing import List

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


sp500 = pd.read_csv('SP500.csv', parse_dates=['observation_date'])
vix = pd.read_csv('VIXCLS.csv', parse_dates=['observation_date'])

df = sp500.merge(vix, on='observation_date', how='inner')
df = df.dropna(subset=['SP500', 'VIXCLS'])

df['VIXCLS_norm'] = (df['VIXCLS'] - df['VIXCLS'].min()) / (df['VIXCLS'].max() - df['VIXCLS'].min())

df['observation_date'] = pd.to_datetime(df['observation_date'])
df = df.sort_values('observation_date').reset_index(drop=True)

df['SP500_pct_change'] = df['SP500'].pct_change() + 1
df['SPX_pct_change'] =  3 * df['SP500'].pct_change() + 1

vol_threshold = .25
max_trading_days = 8 * 252

years = df['observation_date'].dt.year.unique()
start_dates = []

for year in years:
    year_mask = df['observation_date'].dt.year == year
    year_dates = df.loc[year_mask, 'observation_date'].tolist()
    n = min(100, len(year_dates))
    selected = np.random.choice(year_dates, size=n, replace=False)
    if year <= 2019:
        start_dates.extend(selected)

start_dates.sort()

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
            levered = row['VIXCLS_norm'] <= vol_threshold
            portfolio.invest(levered=levered, amount=1000)

    results.append({
        'start_date': start_date,
        'pure_spy': portfolio.pure_spy,
        'pure_spx': portfolio.pure_spx,
        'heuristic': portfolio.spx + portfolio.spy
    })

sim_df = pd.DataFrame(results)

print(f'\nTotal simulations: {len(sim_df)}')
print(f'Avg pure_spy: ${sim_df["pure_spy"].mean():,.2f}')
print(f'Avg pure_spx: ${sim_df["pure_spx"].mean():,.2f}')
print(f'Avg heuristic: ${sim_df["heuristic"].mean():,.2f}')
print(f'Median pure_spy: ${sim_df["pure_spy"].median():,.2f}')
print(f'Median pure_spx: ${sim_df["pure_spx"].median():,.2f}')
print(f'Median heuristic: ${sim_df["heuristic"].median():,.2f}')


