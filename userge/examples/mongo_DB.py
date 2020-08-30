"""
MongoDB Example
"""

from userge import get_collection
BUTTON_BASE = get_collection("TEMP_BUTTON")
BUTTON_BASE.insert_one(                                 # INSERT
            {'msg_data': "test 123"}),
    
***************************************************   
from userge import get_collection
BUTTON_BASE = get_collection("TEMP_BUTTON")      
async for data in BUTTON_BASE.find():                   # LOAD
  print(data)
  
***************************************************  
from userge import get_collection
BUTTON_BASE = get_collection("TEMP_BUTTON")             # DELETE
await BUTTON_BASE.drop()