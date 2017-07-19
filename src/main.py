import client
import sqlite3
import time

YOUR_API_ID = ''
YOUR_API_KEY = ''

ddl_recipe = 'INSERT INTO recipes VALUES (?,?,?,?,?,?,?)'
ddl_nutrition = 'INSERT INTO nutrition VALUES (?,?,?,?,?)'

mxResult = 50

# default option values
TIMEOUT = 5.0
RETRIES = 0

conn = sqlite3.connect('juicerecipes.db')

c = conn.cursor()

cl = client.Client(api_id=YOUR_API_ID, api_key=YOUR_API_KEY, timeout=TIMEOUT, retries=RETRIES)

start_time = time.time()
print(start_time)

params = {
    'q': 'fresh juice',
    'maxResult': 50,
    'allowedCourse': 'Beverages',
    'excludedTechnique': 'Blending'
}

#search = cl.search('smoothie', maxResult=1)
search = cl.search(**params)

totalMatchCount = search['totalMatchCount']

index = 0
id_cntr = 0

maxMatches = 100000#totalMatchCount

nutritionDescriptionDict = {}

while index < maxMatches:

    try:
        #search = cl.search('smoothie', maxResult=mxResult, start=index)
        search = cl.search(**params, start=index)
        print(search)

        matches = search.matches

        for match in matches:
            #print(match)
            recipe = cl.recipe(match.id)

            RecipeID = match['id']
            Flavors = str(list(match['flavors']))
            Ingredients = str(match['ingredients'])
            Rating = match['rating']
            Name = match['recipeName']
            TotalTime = match['totalTimeInSeconds']
            RecipeSource = str(recipe['source']['sourceRecipeUrl'])
            nutritionEstimates = recipe['nutritionEstimates']

            t = (RecipeID, Name, Ingredients, Rating, Flavors, TotalTime, RecipeSource,)

            try:
                # Insert a row of data
                c.execute(ddl_recipe, t)
            except:
                pass

            try:
                nutritionList = []
                for nutrition in nutritionEstimates:
                    attr = nutrition['attribute']
                    nutritionDescriptionDict.update({attr: nutrition['description']})
                    abbr = nutrition['unit']['abbreviation']
                    value = nutrition['value']
                    t = (id_cntr, RecipeID, attr, abbr, value,)
                    nutritionList.append(t)
                    id_cntr += 1

                c.executemany(ddl_nutrition, nutritionList)
            except:
                print('err')
                pass
    except:
        print('search err!')
        pass

    index += mxResult
    print(index)
    if index % (mxResult * 2):
        conn.commit()
        elapsed_time = time.time() - start_time
        print(elapsed_time)

# Save (commit) the changes
conn.commit()

elapsed_time = time.time() - start_time
print(elapsed_time)

# We can also close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.
conn.close()
