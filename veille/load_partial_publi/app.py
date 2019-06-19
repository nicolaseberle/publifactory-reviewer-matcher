import pandas as pd
import random

filename = '../BDD/data.csv'
n = sum(1 for line in open(filename))-1
s = n//1
skip = sorted(random.sample(range(1, n+1), n-s))
df = pd.read_csv(filename, skiprows=skip)

print(df.head())
