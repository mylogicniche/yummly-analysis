import pandas as pd

cancer = pd.read_csv("cancer.csv")

mask = cancer['prevnumber'] > 5

print(mask)