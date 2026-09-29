from dataclasses import dataclass
from typing import List

import pandas as pd


class Portfolio:
    pure_spy = 0.0
    pure_spx = 0.0

    spy = 0.0
    spx = 0.0

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
print(df)

portfolio = Portfolio()
vol_threshold = .25


