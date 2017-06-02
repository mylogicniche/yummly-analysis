import sqlite3
import ast
from collections import Counter
import numpy
from itertools import combinations
import csv
from nltk import pos_tag
import nltk

ratingDict = {}

conn = sqlite3.connect('recipes.db')
c = conn.cursor()

c.execute('SELECT * from recipes;')
rows = c.fetchall()

for row in rows:
    ratingDict.update({row[0]: {"preptime":0, "skincare": 0, "antiox":0, "userrating":0, "fiber":0,
                                "calorie":0, "fiberpercalorie":0}})
#calc prep time rating
timelist = []
calorielist = []
for row in rows:
    id = row[0]
    t = row[5]
    if t:
        timelist.append(t)
    c.execute("""SELECT value from nutrition where attr='ENERC_KCAL' and recipeidf=?""", (id,))
    nuts = c.fetchall()
    if nuts:
        cal = nuts[0][0]
        if cal >= 10:
            calorielist.append(nuts[0])
    pass

mntime = min(timelist)
mncal = min(calorielist)

for row in rows:
    id = row[0]
    t = row[5]
    if t:
        ratingDict[row[0]]["preptime"] = int((mntime / t) * 10)
    rating = row[3]
    ratingDict[id]["userrating"] = rating
    c.execute("""SELECT value from nutrition where attr='ENERC_KCAL' and recipeidf=?""", (id,))
    nuts = c.fetchall()
    cal = nuts[0]
    ratingDict[id]["calorie"] = int((mncal / cal) * 10)

print(mntime)

pass