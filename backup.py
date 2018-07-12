from flask import Flask, request,url_for,jsonify
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse,Gather
import random,string,requests,json
from firebase import firebase
from random import randint
import config
fb = firebase.FirebaseApplication(config.CUSTOM_ACCESS_URL, None)

app = Flask(__name__)

data = []

@app.route("/voice", methods=['GET', 'POST'])
def voice():
    """Respond to incoming phone calls and mention the caller's city"""
    resp = VoiceResponse()
    resp.say('Hello你好,有咩幫到你?', language="zh-HK",voice='alice')
    gather = Gather(input='speech',action='/intent',language='yue-Hant-HK', method='POST', speechTimeout='auto')
    resp.append(gather)
    resp.redirect('/voice',method='GET')
    return str(resp)


@app.route("/voice_eng", methods=['GET', 'POST'])
def voice_eng():
    """Respond to incoming phone calls and mention the caller's city"""
    resp = VoiceResponse()
    gather = Gather(input='speech',action='/intent', method='POST')
    resp.append(gather)
    resp.say('Hello,what can i help you?')
    resp.redirect('/voice',method='GET')
    return str(resp)


@app.route("/intent", methods=['POST'])
def intent():
    resp = VoiceResponse()
    if 'SpeechResult' in request.values:
        choice = request.values['SpeechResult']
        result = get_response_get(choice)
        print("choice:", choice)
        print("result:", result)
        resp.say(result, language="zh-HK")
        gather = Gather(input='speech', action='/intent', language='yue-Hant-HK', method='POST', speechTimeout='auto')
        resp.append(gather)

    else:
        print("inside else")
        resp.say('唔好意思,你冇講嘢喎', language="zh-HK")
    resp.redirect('/voice', method='GET')
    return str(resp)


@app.route("/intent_eng", methods=['POST'])
def intent_eng():
    resp = VoiceResponse()
    if 'SpeechResult' in request.values:
        print("enter if SpeechResult")
        choice = request.values['SpeechResult']
        print("result:", choice)
        resp.say('You just say '+choice)
    else:
        print("inside else")
        resp.say("Sorry, we can't detect what you say")
    resp.redirect('/voice', method='GET')
    return str(resp)


@app.route("/call_survey", methods=["POST"])
def call_survey():
    try:
        phone_number = request.json['phoneNumber']
        sid = request.json['sid']
        token = request.json['token']
        if phone_number is not None and phone_number != "":
            client = Client(sid, token)
            client.calls.create(
                url=url_for('.start_survey',_external=True),
                to=phone_number,
                from_='+85230080480'
            )
        return jsonify({'message': 'Call incoming!'})
    except Exception as ex:
        return str(ex)


@app.route('/start_survey', methods=['POST'])
def start_survey():
    record_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    data.append({
        "record_id": record_id,
        "question": config.QUESTION
    })
    resp = VoiceResponse()
    resp.say('你好,呢度係'+config.SURVEY_FROM+'問卷調查,唔知你有冇時間幫手做份問卷呢?',language=config.LANG)
    gather = Gather(input='speech', action="/survey/"+record_id+"/1", language='yue-Hant-HK', method='POST',
                    speechTimeout='auto')
    resp.append(gather)
    resp.redirect('/end_survey', method='POST')
    return str(resp)


@app.route('/survey/<record_id>/<question_id>', methods=['POST'])
def survery(record_id,question_id):

    question_id = int(question_id)
    item = []
    for items in data:
        if items["record_id"] == record_id:
            item = items["question"]

    resp = VoiceResponse()
    choice = request.values['SpeechResult']

    if question_id >= 2 and question_id <= 4:
        hints_size = len(item[question_id-1]["hints"])
        if hints_size == 0:
            item[question_id - 1]["answer"] = choice
        else:
            for hint in item[question_id-1]["hints"]:
                if hint in choice:
                    item[question_id - 1]["answer"] = choice
                    break
                else:
                    question_id -= 1

    question = item[question_id - 1]["question_asking"]
    len_size = len(question)
    resp.say(question[randint(0, len_size - 1)], language="zh-HK")

    if question_id == 4:
        gather = Gather(input='speech', action='/end_survey/'+record_id, language='yue-Hant-HK', method='POST',
                        speechTimeout='auto')
    else:
        gather = Gather(input='speech', action='/survey/' + record_id + '/' + str(question_id + 1),
                        language='yue-Hant-HK', method='POST', speechTimeout='auto')

    resp.append(gather)
    resp.redirect('/end_survey', method='POST')

    return str(resp)

@app.route('/end_survey/<record_id>', methods=['POST'])
def end_survery(record_id):
    resp = VoiceResponse()
    choice = request.values['SpeechResult']
    for item in data:
        if item['record_id'] == record_id:
            item['question'].append({"question_id":5,"answer":choice})
            create_agent_db(item)

    resp.say('多謝你接受訪問,拜拜', language="zh-HK")
    print(data)
    return str(resp)


def get_response_post(choice):
    url = "http://127.0.0.1:8080/sub_agent"
    headers = {
        'content-type': "application/json",
        'cache-control': "no-cache",
        'postman-token': "f3915e5e-6734-202e-4ad7-ea1fee3a38e5"
    }
    result = {
        "system_id": 12312,
        "agent_id": "26yjP",
        "text": choice
    }
    data_json = json.dumps(result)
    response = requests.post(url, data=data_json, headers=headers)
    result = json.loads(response.text)['Speech']

    return str(result)


def get_response_get(choice):
    url="http://test.nlp.checkx.hk/NLP?Key=0bb18fb84259c567c723ba96188f47ac&Say="+choice+"&SessionID=xxx"
    response = requests.get(url)
    print(json.loads(response.text))
    if 'Success' in json.loads(response.text):
        if json.loads(response.text)['Success']==False:
            result = "唔好意思,我唔係好明你講咩,你啱啱講咗"+choice
        else:
            result = json.loads(response.text)['Speech']
    else:
        result = json.loads(response.text)['Speech']
    return str(result)


def create_agent_db(result):
    try:
        result = fb.post('/survey',result)
        return {"status":"success"}
    except Exception as ex:
        print(ex)
        return {"status":"fail"}


if __name__ == "__main__":
    app.run(port=5000)
