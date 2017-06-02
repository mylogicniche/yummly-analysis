import sqlite3
import ast
from collections import Counter
import numpy
from itertools import combinations
import csv
from nltk import pos_tag
import nltk

query_ingredients = 'SELECT ID,Ingredients from recipes;'
query_calories = 'SELECT * FROM nutrition WHERE attr="ENERC_KCAL" ORDER BY value ASC;'
query_fiber = 'SELECT * FROM nutrition WHERE attr="FIBTG" ORDER BY value DESC;'
query_nutritions = 'SELECT * FROM nutrition WHERE recipeidf in (SELECT id from recipes) and value<>0;'
query_nutrition_attr = 'SELECT attr FROM nutrition;'
query_nutrition_number = 'SELECT recipeidf FROM nutrition WHERE recipeidf="{ID}" and value<>0;'

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

singlelist = ["ice", "kale", "spinach", "yogurt", "lime"]

skin = ["olive","tomato","chocolate","oatmeal","tea","kale","walnut","orange peel","lemon peel","rosemary","almond milk",
        "water","ice","soy","bell","cofee","kiwi","egg","pumpkin","wine","carrot","chickpee","avocado","pomegranate","bean",
        "sweet potato","broccoli",""]

hangover = ["coconut","coconut milk","coconut water","asparagus","ginger","tomato","lemon","lemon juice","banana",
            "egg","cayenne pepper","honey","coffee"]

constipation = ["bean","kiwi","sweet potato","walnut","nut","pear","plum","apple","berry","strawberry","flaxseed",
                "broccoli","prune"]

cold = ["garlic","orange juice","lemon juice", "fennel seed","fennel","fennel bulb","yogurt","kefir","tea","red pepper",
        "milk","mushroom","arugula","blueberry","brazil nut","carrot","sweet potato","oat",""]

wnl = nltk.stem.WordNetLemmatizer()

intersectionPerRecipe = []
cancer_preventers = []
for l in phytochemicals.values():
    cancer_preventers.extend([wnl.lemmatize(p.lower()) for p in l])

conn = sqlite3.connect('recipes.db')

c = conn.cursor()

c.execute(query_nutritions)

coverDict = {}
coverList = []
rows = c.fetchall()
i = 0
for row in rows:
    coverList.append(row[1])

coverListUnique = list(set(coverList))

b = Counter(coverList)
bm = b.most_common()

with open("coverage.csv", "w") as f:
    fields = ["name", "number", "raiting", "link", "list"]
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    i = 0
    for bb in bm:
        if "smoothie" not in bb[0].lower():
            continue
        c.execute("SELECT * from recipes WHERE ID=?", (bb[0],))
        r = c.fetchall()
        name = r[0][1]
        number = bb[1]
        raiting = r[0][3]
        link = r[0][6]
        c.execute("SELECT attr FROM nutrition WHERE recipeidf=?", (bb[0],))
        rl = c.fetchall()
        nutlist = [r[0] for r in rl]
        for r in rl:
            nutlist.append(r[0])
        l = len(set(nutlist))
        s = str(set(nutlist))
        writer.writerow({'name':name, 'number':l, "raiting":raiting, 'link':link, 'list':s})
        i += 1
        if i >= 500:
            break

with open("easiest.csv", "w") as f:
    fields = ["name", "ingreds", "time", "rating", "url"]
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    c.execute("SELECT Name,Ingredients,TotalTime,Rating,SourceUrl from recipes WHERE TotalTime<>0 ORDER BY TotalTime ASC;")
    rows = c.fetchall()
    for row in rows[:20]:
        writer.writerow({"name":row[0], "ingreds":row[1], "time":row[2], "rating":row[3], "url":row[4]})

print("unique recipe list", len(coverDict))

c.execute(query_nutrition_attr)

wholeNutritionList = []
rows = c.fetchall()
for row in rows:
    wholeNutritionList.append(row[0])

nutritionListUnique = list(set(wholeNutritionList))

c.execute(query_ingredients)

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


allIngredListUnique = list(set(allIngredList))

counts = Counter(allIngredList)

print(counts)

def find_recipes_for_health(recipeDict, preventer, fname):
    intersectionPerRecipe = {}
    for key, val in recipeDict.items():
        inter = set(val).intersection(set(preventer))
        intersectionPerRecipe.update({key : [inter, len(inter)]})

    SortedintersectionPerRecipe = sorted(intersectionPerRecipe.items(), key = lambda x: x[1][1], reverse = True)

    with open(fname, "w") as f:
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


    print(SortedintersectionPerRecipe)

find_recipes_for_health(ingredDictPerRecipe, cancer_preventers, "cancer.csv")
find_recipes_for_health(ingredDictPerRecipe, skin, "skin.csv")
find_recipes_for_health(ingredDictPerRecipe, hangover, "hangover.csv")

#http://www.medicinenet.com/top_foods_for_constipation_relief/page13.htm
find_recipes_for_health(ingredDictPerRecipe, constipation, "constipation.csv")

#http://www.health.com/health/gallery/0,,20631007,00.html
find_recipes_for_health(ingredDictPerRecipe, cold, "cold.csv")

with open('ingredients.txt', 'w') as f:
    for ingred in counts.items():
        f.writelines(str(ingred) + '\n')

c.execute(query_calories)

calorieList = []
rows = c.fetchall()
for row in rows:
    calorieList.append(row[4])

calorieArr = numpy.array(calorieList)
print("calorie (min): ",numpy.min(calorieArr))
print("calorie (max): ",numpy.max(calorieArr))
print("calorie (mean): ",numpy.mean(calorieArr, axis=0))
print("calorie (std): ",numpy.std(calorieArr, axis=0))

with open("calorie.csv", "w") as f:
    fields = ["id", "name", "calorie", "ingreds", "time", "rating", "url"]
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    for row in rows[:500]:
        id = row[1]
        c.execute("SELECT * from recipes WHERE ID=?", (id,))
        recs = c.fetchall()
        name = recs[0][1]
        calorie = row[4]
        ingreds = recs[0][2]
        rating = recs[0][3]
        time = recs[0][5]
        url = recs[0][6]
        writer.writerow({"id":id, "name":name, "calorie":calorie, "ingreds":ingreds,
                         "time":time, "rating":raiting, "url":url})

c.execute(query_fiber)
rows = c.fetchall()

with open("fiber.csv", "w") as f:
    fields = ["id", "name", "fiber", "ingreds", "time", "rating", "url"]
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    for row in rows[:500]:
        id = row[1]
        c.execute("SELECT * from recipes WHERE ID=?", (id,))
        recs = c.fetchall()
        name = recs[0][1]
        fiber = row[4]
        ingreds = recs[0][2]
        rating = recs[0][3]
        time = recs[0][5]
        url = recs[0][6]
        writer.writerow({"id":id, "name":name, "fiber":fiber, "ingreds":ingreds,
                         "time":time, "rating":raiting, "url":url})

with open("fiber_per_calorie.csv", "w") as f:
    fields = ["id", "name", "fiberPerCalorie", "ingreds", "time", "rating", "url"]
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    for row in rows[:500]:
        id = row[1]
        c.execute("SELECT value FROM nutrition WHERE attr='ENERC_KCAL' AND recipeidf=?", (id,))
        recs = c.fetchall()
        calorie =recs[0][0]
        if calorie < 30:
            continue
        c.execute("SELECT * from recipes WHERE ID=?", (id,))
        recs = c.fetchall()
        name = recs[0][1]
        fiber = row[4]
        ingreds = recs[0][2]
        rating = recs[0][3]
        time = recs[0][5]
        url = recs[0][6]
        fiberPerCalorie = fiber/calorie
        writer.writerow({"id":id, "name":name, "fiberPerCalorie":str(fiberPerCalorie), "ingreds":ingreds,
                         "time":time, "rating":raiting, "url":url})


fiberList = []
for row in rows:
    fiberList.append(row[4])

fiberArr = numpy.array(fiberList)
print("fiber (min): ",numpy.min(fiberArr, axis=0))
print("fiber (max): ",numpy.max(fiberArr, axis=0))
print("fiber (mean): ",numpy.mean(fiberArr, axis=0))
print("fiber (std): ",numpy.std(fiberArr, axis=0))

conn.close()

def ingred_combination(ListArr, Num, exclude):
    d = Counter()
    for ingredList in ListArr:
        if len(ingredList) < Num:
            continue

        ingredList.sort()
        for comb in combinations(ingredList, Num):
            if any(item in comb for item in exclude):
                continue
            d[comb] += 1

    combs = d.most_common()

    ingredcnts = [x[1] for x in combs[:10]]#    list(map(lambda x: x[1], combs[:10]))
    print(["{:10.2f}".format(x / max(ingredcnts)) for x in ingredcnts])

    return combs

def write_comb(fname, ingredcomb):
    with open(fname, "w") as f:
        for comb in ingredcomb[:20]:
            s = ""
            for c in comb[0]:
                s += str(c) + '+'
            s = s[:-1] + ';'
            f.write(s)

        f.write('\n')

        for comb in ingredcomb[:20]:
            f.write(str(comb[1]) + ';')

def writeCombResult(fname, comb):
    with open(fname, "w") as f:
        fields = ["ingred", "number"]
        writer = csv.DictWriter(f, fields)
        writer.writeheader()
        for ingred in comb:
            s = " - ".join(ingred[0])
            writer.writerow({"ingred": s, "number": ingred[1]})


ingredcomb = ingred_combination(ingredListsPerRecipe, 1, [])
writeCombResult("single.csv", ingredcomb)
write_comb("single.txt", ingredcomb)


ingredcomb = ingred_combination(ingredListsPerRecipe, 2, [])
writeCombResult("duple.csv", ingredcomb)
write_comb("duple.txt", ingredcomb)

ingredcomb = ingred_combination(ingredListsPerRecipe, 3, [])
writeCombResult("triple.csv", ingredcomb)
write_comb("triple.txt", ingredcomb)

ingredcomb = ingred_combination(ingredListsPerRecipe, 1, ["banana","ice","water","honey"])
writeCombResult("single_ex.csv", ingredcomb)
write_comb("single_ex.txt", ingredcomb)

ingredcomb = ingred_combination(ingredListsPerRecipe, 2, ["banana","ice","water","honey"])
writeCombResult("duple_ex.csv", ingredcomb)
write_comb("duple_ex.txt", ingredcomb)

ingredcomb = ingred_combination(ingredListsPerRecipe, 3, ["banana","ice","water","honey"])
writeCombResult("triple_ex.csv", ingredcomb)
write_comb("triple_ex.txt", ingredcomb)

#ingredcomb = ingred_combination(ingredListsPerRecipe, 4)
#write_comb("quad.txt", ingredcomb)



pass