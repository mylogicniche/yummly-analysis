with open("nutritionlist", "r") as f:
    with open("nutlist.txt", "w") as f2:
        orig = f.readlines()
        s = orig[0].replace('\\',"").replace("',","',\n")
        f2.writelines(s)