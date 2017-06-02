import sqlite3
import ast
from collections import Counter
import numpy
from itertools import combinations
import csv
from nltk import pos_tag
import nltk

ratingDict = {}

conn = sqlite3.connect('../db/recipes.db')
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

c.execute("SELECT recipeidf, value from nutrition where attr='ENERC_KCAL'")
nuts = c.fetchall()
calDict = {}
callist = []
for row in nuts:
    cal = row[1]
    if cal >= 30:
        callist.append(cal)
    calDict.update({row[0]:cal})

mntime = min(timelist)
mncal = min(callist)

c.execute("SELECT recipeidf, value from nutrition where attr='FIBTG' ORDER BY value DESC")
nuts = c.fetchall()
mxfiber = nuts[0][1]

print('mxfiber', mxfiber)

fiberDict = {}
for row in nuts:
    fiberDict.update({row[0]:row[1]})

for row in rows:
    id = row[0]
    t = row[5]
    if t:
        ratingDict[row[0]]["preptime"] = int((mntime / t) * 10)
    rating = row[3]
    ratingDict[id]["userrating"] = rating
    try:
        cal = calDict[id]
        ratingDict[id]["calorie"] = int((mncal / cal) * 10)
    except:
        pass

    try:
        ratingDict[id]["fiber"] = int(fiberDict[id]/mxfiber)
    except:
        pass

print(mntime)

pass