from flask import Flask
from twilio.twiml.voice_response import VoiceResponse

app = Flask(__name__)

@app.route("/voice", methods=["POST"])
def voice():
    resp = VoiceResponse()
    resp.say("Hello, good to see you!")
    print("receive request")
    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)