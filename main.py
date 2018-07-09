from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse,Gather

app = Flask(__name__)


@app.route("/voice", methods=['GET', 'POST'])
def voice():
    """Respond to incoming phone calls and mention the caller's city"""
    resp = VoiceResponse()
    gather = Gather(input='speech',action='/intent',language='yue-Hant-HK', method='POST')
    gather.say('Hello你好,有咩幫到你?', language="zh-HK")
    resp.append(gather)
    resp.say('Hello你好,有咩幫到你?', language="zh-HK")
    resp.redirect('/voice',method='GET')
    return str(resp)

@app.route("/voice_eng", methods=['GET', 'POST'])
def voice_eng():
    """Respond to incoming phone calls and mention the caller's city"""
    resp = VoiceResponse()
    gather = Gather(input='speech',action='/intent', method='POST')
    gather.say('Enter somthing')
    resp.append(gather)
    resp.say('Hello,what can i help you?')
    resp.redirect('/voice',method='GET')
    return str(resp)

@app.route("/intent", methods=['POST'])
def intent():
    resp = VoiceResponse()
    if 'SpeechResult' in request.values:
        choice = request.values['SpeechResult']
        print("result:",choice)
        if choice == '好啊':
            resp.say('好啊,等一陣',language="zh-HK")
            return str(resp)

        elif choice == '唔需要':
            resp.say('唔緊要,拜拜',language="zh-HK")
            return str(resp)
        else:
            resp.say('唔好意思,我唔知你講緊乜',language="zh-HK")
    else:
        resp.say('唔好意思,你冇講嘢喎', language="zh-HK")
    resp.redirect('/voice', method='GET')


@app.route("/intent_eng", methods=['POST'])
def intent_eng():
    resp = VoiceResponse()
    if 'SpeechResult' in request.values:
        choice = request.values['SpeechResult']
        print("result:",choice)
        if choice == '好啊':
            resp.say('Ok')
            return str(resp)

        elif choice == '唔需要':
            resp.say('No')
            return str(resp)
        else:
            resp.say('唔好意思,我唔知你講緊乜')
    else:
        resp.say('唔好意思,你冇講嘢喎', language="zh-HK")
    resp.redirect('/voice', method='GET')
if __name__ == "__main__":
    app.run(debug=True)