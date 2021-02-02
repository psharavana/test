import json


array = []

def get_key(j_data):
    for key in j_data.keys():
       array.append(key)
       
       
       for x in j_data[key].keys() : 
           array.append(x)
           if isinstance(j_data[key][x], type({}))== True:
               get_key(j_data[key][x])  
           else:
               print(j_data[key][x])



def lambda_handler(event, context):
dct = {"a":{"b":{"c":"d"}}}
    
    for key in dct.keys():
      #print(key)
      if isinstance(dct[key], dict)== False:
          print(key)
          print(key, dct[key])
      if isinstance(dct[key], dict)== True:
        array.append(key)
       
        get_key(dct[key])  
      
      
    print (array)   
