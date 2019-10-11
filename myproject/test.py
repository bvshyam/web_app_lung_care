import json
#from keras.models import Sequential, model_from_json

with open('multi_disease_model.json', 'r') as json_file:
    print(json_file)
    architecture = json.load(json_file)
    #model = model_from_json(json.dumps(architecture))


#model.load_weights('multi_disease_model_weight.h5')
#model._make_predict_function()