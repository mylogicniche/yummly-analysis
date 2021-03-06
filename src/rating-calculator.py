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
    ratingDict.update({tuple([row[0],row[6]]): {"preptime":0, "skincare": 0, "antiox":0, "userrating":0, "fiber":0,
                                "calorie":0, "fiberpercalorie":0, "constipation":0, "cold":0, "hangover":0, "overall":0}})
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

fiberPerCalDict = {}

for id, fiber in fiberDict.items():
    fiberPerCalDict.update({id:fiber/calDict[id]})

mxfiberpercal = max(list(fiberPerCalDict.values()))

for row in rows:
    id = row[0]
    t = row[5]
    url = row[6]
    if t:
        ratingDict[tuple([id, url])]["preptime"] = int((mntime / t) * 10)
    rating = row[3]
    ratingDict[tuple([id, url])]["userrating"] = rating
    try:
        cal = calDict[id]
        if cal > 30:
            ratingDict[tuple([id, url])]["calorie"] = int((mncal / cal) * 10)
    except:
        pass

    try:
        ratingDict[tuple([id, url])]["fiber"] = int(10 * fiberDict[id]/mxfiber)
    except:
        pass


    try:
        fber = fiberDict[id]
        cal = calDict[id]
        fpercal = int(10 * (fber / cal) / mxfiberpercal)
        ratingDict[tuple([id, url])]["fiberpercalorie"] = fpercal
    except:
        pass

wnl = nltk.stem.WordNetLemmatizer()
cancer_preventers = []
for l in phytochemicals.values():
    cancer_preventers.extend([wnl.lemmatize(p.lower()) for p in l])

print(cancer_preventers)

def find_recipes_for_health(recipeDict, preventer, fname, prevType):
    intersectionPerRecipe = {}
    for key, val in recipeDict.items():
        inter = set(val).intersection(set(preventer))
        intersectionPerRecipe.update({key : [inter, len(inter)]})

    SortedintersectionPerRecipe = sorted(intersectionPerRecipe.items(), key = lambda x: x[1][1], reverse = True)

    mxprevno = max([l[1] for l in list(intersectionPerRecipe.values())])

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
            prevrating = int(10 * r[1][1] / mxprevno)
            d = {"id":id.encode('utf8'), "name":name.encode('utf8'), "ingreds":ingreds.encode('utf8'),
                 "preventives":str(r[1][0]).encode('utf8'),
                 "prevnumber":r[1][1], "time":time, "rating":rating, "url":url.encode('utf8') }
            writer.writerow(d)

            ratingDict[tuple([id, url])][prevType] = prevrating

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

print("unique ingredients: ", len(list(set(allIngredList))))

find_recipes_for_health(ingredDictPerRecipe, cancer_preventers, "cancer.csv", "antiox")
find_recipes_for_health(ingredDictPerRecipe, skin, "skin.csv", "skincare")
find_recipes_for_health(ingredDictPerRecipe, constipation, "constipation.csv", "constipation")
find_recipes_for_health(ingredDictPerRecipe, cold, "cold.csv", "cold")
find_recipes_for_health(ingredDictPerRecipe, hangover, "hangover.csv", "hangover")

for id, ratings in ratingDict.copy().items():
    m = numpy.mean(numpy.array(list(ratings.values())))
    ratingDict[id]["overall"] = m

with open('../out/allraiting.csv', "w") as f:
    fields = ["id", "url", "calorie", "cold", "fiberpercalorie", "userrating", "constipation", "fiber", "preptime", "antiox",
              "hangover", "skincare", "overall"]
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    for id,ratings in ratingDict.items():
        writer.writerow({'id':id[0], 'url':id[1], "calorie":ratings["calorie"], "cold":ratings["cold"],
                         "fiberpercalorie":ratings["fiberpercalorie"], "userrating":ratings["userrating"],
                         "constipation":ratings["constipation"], "fiber":ratings["fiber"], "preptime":ratings["preptime"],
                         "antiox":ratings["antiox"], "hangover":ratings["hangover"], "skincare":ratings["skincare"],
                         "overall":ratings["overall"]})

pass