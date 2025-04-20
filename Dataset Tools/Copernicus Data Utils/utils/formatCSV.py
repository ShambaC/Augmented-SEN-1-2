import pandas as pd

season = "winter"
number = 172
df = pd.read_csv(f"../../../Dataset/{season}/prompts_{number}.csv")

# Split prompt into individual columns
df[['season', 'region']] = df['prompt'].str.split(', ', n=1, expand=True)

# Remove prompt column
df.drop(['prompt'], axis=1, inplace=True)

# Remove labels from season and region columns
df['season'] = df['season'].str.slice(start=8)
df['region'] = df['region'].str.slice(start=8)

# Save the file
df.to_csv(f"../../../Dataset/{season}/info_{number}.csv", index=False)