import sqlite3
import ast
from collections import Counter
import numpy
from itertools import combinations
import csv
from nltk import pos_tag
import nltk

phytochemicals = {
 'Allyl-sulphides':['Onion', 'garlic', 'chives', 'leek'],
 'Sulforaphanes-indoles':['Broccoli', 'Brussels sprout', 'cabbage', 'cauliflower'],
 'Lutein-zeaxanthin':['Asparagus', 'collard green', 'spinach', 'winter squash'],
 'Cryptoxanthin-flavonoids': ['Cantaloupe', 'nectarines', 'orange', 'papaya', 'peaches'],
 'Alpha-beta-carotenes':['Carrot', 'mango', 'pumpkin'],
 'Anthocyanins-polyphenols': ['Berries', 'grape', 'plums'],
 'Lycopene':['Tomatoes', 'pink', 'grapefruit', 'watermelon'],
 'Extra': ['beet', 'beet root', 'beetroot', 'rutabaga', 'radishes', 'grean bean', 'goji berry', 'blueberry','strawberry',
           'Acai Berries', 'Bilberries','Blackberries','Cherries','Pecans','Cranberries','Cilantro','pecans'],
 'Herb_Antioxidants': ['Clove','Cinnamon','Oregano','turmeric','cocoa','cumin','parsley','basil','ginger','thyme']
}

skin = ["olive","tomato","chocolate","oatmeal","tea","kale","walnut","orange peel","lemon peel","rosemary","almond milk",
        "water","ice","soy","bell","cofee","kiwi","egg","pumpkin","wine","carrot","chickpee","avocado","pomegranate","bean",
        "sweet potato","broccoli",""]

hangover = ["coconut","coconut milk","coconut water","asparagus","ginger","tomato","lemon","lemon juice","banana",
            "egg","cayenne pepper","honey","coffee"]

constipation = ["bean","kiwi","sweet potato","walnut","nut","pear","plum","apple","berry","strawberry","flaxseed",
                "broccoli","prune"]

cold = ["garlic","orange juice","lemon juice", "fennel seed","fennel","fennel bulb","yogurt","kefir","tea","red pepper",
        "milk","mushroom","arugula","blueberry","brazil nut","carrot","sweet potato","oat",""]

singlelist = ["ice", "kale", "spinach", "yogurt", "lime"]

ratingDict = {}

conn = sqlite3.connect('../db/recipes.db')
c = conn.cursor()

c.execute('SELECT * from recipes;')
rows = c.fetchall()

for row in rows:
    ratingDict.update({row[0]: {"preptime":0, "skincare": 0, "antiox":0, "userrating":0, "fiber":0,
                                "calorie":0, "fiberpercalorie":0, "constipation":0, "cold":0, "hangover":0}})
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

    try:
        ratingDict[id]["fiberpercalorie"] = fiberDict[id] / calDict[id]
    except:
        pass

wnl = nltk.stem.WordNetLemmatizer()
cancer_preventers = []
for l in phytochemicals.values():
    cancer_preventers.extend([wnl.lemmatize(p.lower()) for p in l])

def find_recipes_for_health(recipeDict, preventer, fname, prevType):
    intersectionPerRecipe = {}
    for key, val in recipeDict.items():
        inter = set(val).intersection(set(preventer))
        intersectionPerRecipe.update({key : [inter, len(inter)]})

    SortedintersectionPerRecipe = sorted(intersectionPerRecipe.items(), key = lambda x: x[1][1], reverse = True)


    with open('../out/' + fname, "w") as f:
        fields = ["id", "name", "ingreds", "preventives", "prevnumber", "time", "rating", "url"]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for r in SortedintersectionPerRecipe:
            id = r[0]
            c.execute("SELECT * FROM recipes WHERE ID=?", (id,))
            rows = c.fetchall()
            name = rows[0][1]
            ingreds = rows[0][2]
            rating = rows[0][3]
            time = rows[0][5]
            url = rows[0][6]
            writer.writerow({"id":id, "name":name, "ingreds":ingreds, "preventives":str(r[1][0]),
                             "prevnumber":r[1][1], "time":time, "rating":rating, "url":url })


            ratingDict[id][prevType] = r[1][1]

c.execute('SELECT ID,Ingredients from recipes;')

allIngredListRow = c.fetchall()

allIngredList = []
ingredListsPerRecipe = []
ingredDictPerRecipe = {}
for ingredListRow in allIngredListRow:
    l = ast.literal_eval(ingredListRow[1])
    for i in l:
        low = [x.lower() for x in i.split()]
        tagged_sent = pos_tag([wnl.lemmatize(x) for x in low])
        ta = [word for word, pos in tagged_sent if pos == 'NN' or pos == 'NNS']
        if len(ta) == 0:
            continue

        s = " ".join(ta)

        for item in singlelist:
            if item in ta:
                s = item
                break

        l[l.index(i)] = s


    allIngredList.extend(l)
    ingredListsPerRecipe.append(l)
    ingredDictPerRecipe.update({ingredListRow[0]:l})

find_recipes_for_health(ingredDictPerRecipe, cancer_preventers, "cancer.csv", "antiox")
find_recipes_for_health(ingredDictPerRecipe, skin, "skin.csv", "skincare")
find_recipes_for_health(ingredDictPerRecipe, constipation, "constipation.csv", "constipation")
find_recipes_for_health(ingredDictPerRecipe, cold, "cold.csv", "cold")
find_recipes_for_health(ingredDictPerRecipe, hangover, "hangover.csv", "hangover")

with open('../out/allraiting.csv', "w") as f:
    fields = ["id", "calorie", "cold", "fiberpercalorie", "userrating", "constipation", "fiber", "preptime", "antiox",
              "hangover", "skincare"]
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    for id,ratings in ratingDict.items():
        writer.writerow({'id':id, "calorie":ratings["calorie"], "cold":ratings["cold"],
                         "fiberpercalorie":ratings["fiberpercalorie"], "userrating":ratings["userrating"],
                         "constipation":ratings["constipation"], "fiber":ratings["fiber"], "preptime":ratings["preptime"],
                         "antiox":ratings["antiox"], "hangover":ratings["hangover"], "skincare":ratings["skincare"]})

pass