import requests
import flask
import json

url = "http://test.nlp.checkx.hk/NLP?Key=0bb18fb84259c567c723ba96188f47ac&Say=咁搭船幾錢&SessionID=xxx"

response = requests.get(url)
result = response.text
print(json.loads(result)['Speech'])

text = ",呢度係櫻島麵包舖"
