from flask import Flask, request, url_for, jsonify
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather
import random, string, requests, json
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
    resp.say('Hello你好,有咩幫到你?', language="zh-HK", voice='alice')
    resp.play(url='https://api.twilio.com/cowbell.mp3')
    gather = Gather(input='speech', action='/intent', language='yue-Hant-HK', method='POST', speechTimeout='auto')
    resp.append(gather)
    resp.redirect('/voice', method='GET')
    return str(resp)


@app.route("/voice_eng", methods=['GET', 'POST'])
def voice_eng():
    """Respond to incoming phone calls and mention the caller's city"""
    resp = VoiceResponse()
    gather = Gather(input='speech', action='/intent', method='POST')
    resp.append(gather)
    resp.say('Hello,what can i help you?')
    resp.redirect('/voice', method='GET')
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
        resp.say('You just say ' + choice)
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
                record=True,
                url=url_for('.start_survey', _external=True),
                to=phone_number,
                from_='+85230080480',
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
    say_str = "你好,呢度係" + str(config.SURVEY_FROM) + "問卷調查,唔知你有冇時間幫手做份問卷呢?"

    print(say_str)
    resp.say(say_str, language="zh-HK")
    gather = Gather(input='speech', action="/survey/" + record_id + "/1/0", hints=config.SURVEY_ACCEPT_HINT,
                    language='yue-Hant-HK', method='POST',
                    speechTimeout='auto')

    resp.append(gather)
    resp.redirect('/start_survey', method='POST')
    resp.say('I did not receive a recording')
    #resp.play(url=config.WELCOME_ASKING_VOICE)
    return str(resp)


@app.route('/survey/<record_id>/<question_id>/<error_count>', methods=['POST'])
def survery(record_id, question_id, error_count):
    status = True
    error_count = int(error_count)
    question_id = int(question_id)
    resp = VoiceResponse()
    # resp.record(timeout=10, transcribe=True)
    print(request.values)
    choice = request.values['SpeechResult']

    if question_id == 1:
        print(choice)
        for hint in config.SURVEY_ACCEPT_HINT:
            if hint in choice:
                status = True
                break
            else:
                status = False
    print("status:", status)
    if status is False:
        resp.say(config.SURVEY_REJECT_SENTENCE, language="zh-HK")
        # resp.play(url=config.SURVEY_REJECT_VOICE)
        return str(resp)

    current_question_location = question_id - 1
    item = []
    for items in data:
        if items["record_id"] == record_id:
            item = items["question"]

    print("user response:", choice)
    print("question_id:", question_id)
    if question_id >= 2 and question_id <= 5:
        hints_size = len(item[current_question_location - 1]["hints"])
        if hints_size == 0:
            item[question_id - 2]["answer"] = choice
        else:
            for hint in item[current_question_location - 1]["hints"]:
                if hint in choice:
                    status = True
                    item[question_id - 2]["answer"] = choice
                    break
                else:
                    status = False

    if status is False and error_count < 2:
        question_id -= 1
        current_question_location = question_id - 1

    if current_question_location >= 0 and current_question_location <= 3:
        question = item[current_question_location]["question_asking_sentence"]
        len_size = len(question)

        if status is False and error_count < 1:
            error_count += 1
            say_sen = config.REPEAT_SENTENCE1 + question[randint(0, len_size - 1)]
            resp.say(say_sen, language="zh-HK")
            # resp.play(url=config.REPEAT_VOICE1)
        elif status is False and error_count < 2:
            error_count += 1
            say_sen = config.REPEAT_SENTENCE2 + question[randint(0, len_size - 1)]
            resp.say(say_sen, language="zh-HK")
            # resp.play(url=config.REPEAT_VOICE2)
        elif status is False and error_count >= 2:
            error_count = 0
            # say_sen = config.NEXT_QUESTION + question[randint(0, len_size - 1)]
            say_sen = config.DIAL_PHONE
            resp.say(say_sen, language="zh-HK")
            resp.dial(config.DIAL_PHONE_CALL)
            #  resp.play(url=config.NEXT_QUESTION_VOICE)
        else:
            error_count = 0
            say_sen = question[randint(0, len_size - 1)]
            resp.say(say_sen, language="zh-HK")
        # resp.dial(
        #     "+85296613227"
        # )
    else:
        resp.say(config.THANKS_SENTENCE, language="zh-HK")
        # resp.play(url=config.THANKS_VOICE)

    if question_id == config.QUESTION_SIZE + 1:
        print(item)
        create_agent_db(item)
    else:
        gather = Gather(input='speech',
                        action='/survey/' + record_id + '/' + str(question_id + 1) + '/' + str(error_count),
                        language='yue-Hant-HK', method='POST', speechTimeout='auto')
        resp.append(gather)
        resp.redirect('/survey/' + record_id + '/' + str(question_id) + '/' + str(error_count), method='POST')
    return str(resp)


@app.route('/end_survey/<record_id>', methods=['POST'])
def end_survery(record_id):
    for item in data:
        if item['record_id'] == record_id:
            create_agent_db(item)
    return str(True)


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
    url = "https://nlp.asiabots.com/CareClub?Key=f9bbe5f386487c416d4153b9ba307ad7&SessionID=CareClubXXX&Say=" + choice
    response = requests.get(url)
    print(json.loads(response.text))
    if 'Speech' in json.loads(response.text):
        result = json.loads(response.text)['Speech']
    else:
        result = "唔好意思,我唔係好明你講咩,你啱啱講咗" + choice
    return str(result)


def create_agent_db(result):
    try:
        result = fb.post('/survey', result)
        return {"status": "success"}
    except Exception as ex:
        print(ex)
        return {"status": "fail"}


if __name__ == "__main__":
    app.run(port=5000)
