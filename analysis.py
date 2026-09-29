import pandas as pd

sp500 = pd.read_csv('SP500.csv', parse_dates=['observation_date'])
vix = pd.read_csv('VIXCLS.csv', parse_dates=['observation_date'])

df = sp500.merge(vix, on='observation_date', how='inner')
df = df.dropna(subset=['SP500', 'VIXCLS'])

df['VIXCLS_norm'] = (df['VIXCLS'] - df['VIXCLS'].min()) / (df['VIXCLS'].max() -  df['VIXCLS'].min())

print(f'SP500 rows: {len(sp500)}, VIX rows: {len(vix)}')
print(f'Merged aligned rows: {len(df)}')
print(f'Date range: {df.observation_date.min()} to {df.observation_date.max()}')
print(df.head())
print('...')
print(df.tail())
