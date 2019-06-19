#!/bin/python3

import ijson
import json
import pandas as pd


in_file = open('../BDD/sample-S2-records.json', 'r')
#print(in_file)
#parser = ijson.parse(in_file)
#print(parser)

#for item in ijson.items(in_file, "item"):
#        print(item)


test = pd.DataFrame.from_dict(list(ijson.items(in_file, "item")))
#test = pd.DataFrame.from_dict(test)

temp = test.iloc[0]

temp.to_json('../BDD/test.json')

#f = urlopen('../BDD/sample-S2-records_v3.json')
#objects = ijson.items(f, 'entities')
#cities = (o for o in objects if o['type'] == 'city')
#for city in cities:
#    do_something_with(city)
