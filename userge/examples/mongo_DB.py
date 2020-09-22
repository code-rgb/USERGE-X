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
BUTTON_BASE = get_collection("TEMP_BUTTON")             # DELETE All
await BUTTON_BASE.drop()



dir of BUTTON_BASE ->

  ['aggregate', 'aggregate_raw_batches', 'bulk_write', 'codec_options', 
  'count_documents', 'create_index', 'create_indexes', 'database', 'delegate', 
  'delete_many', 'delete_one', 'distinct', 'drop', 'drop_index', 'drop_indexes', 
  'estimated_document_count', 'find', 'find_one', 'find_one_and_delete', 
  'find_one_and_replace', 'find_one_and_update', 'find_raw_batches', 'full_name', 
  'get_io_loop', 'index_information', 'inline_map_reduce', 'insert_many', 
  'insert_one', 'list_indexes', 'map_reduce', 'name', 'options', 'read_concern', 
  'read_preference', 'reindex', 'rename', 'replace_one', 'update_many', 'update_one', 
  'watch', 'with_options', 'wrap', 'write_concern']