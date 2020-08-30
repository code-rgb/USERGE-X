import json
import os

if not os.path.exists('userge/xcache'):
    os.mkdir('userge/xcache')
PATH = "userge/xcache/data.txt"   

# Dump
d = []
json.dump(d, open(PATH,'w'))

*************************************************** 
# Load
view_data = json.load(open(PATH))

*************************************************** 
# Update and Dump
view_data[0].update(new_id)
json.dump(view_data, open(PATH,'w'))
