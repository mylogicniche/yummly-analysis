import csv
import sqlite3
import ast

conn = sqlite3.connect('../db/recipes.db')
c = conn.cursor()

with open("../out/allraiting.csv", "r") as f:
    alllines = f.readlines()

with open("../out/ratingsWoBanana.csv", "w") as f:
    f.writelines(alllines[0])
    for line in alllines[1:]:
        id = line.split(",")[0]
        c.execute('SELECT Ingredients from recipes where id=?;', (id,))
        rows = c.fetchall()
        l = ast.literal_eval(rows[0][0])
        if not 'bananas' in [x.lower() for x in l]:
            f.writelines(line)
        pass