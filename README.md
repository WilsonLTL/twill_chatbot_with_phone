# twilio_chatbot_to_phone

## call survey
http://ec2-13-250-98-66.ap-southeast-1.compute.amazonaws.com:80/call_survey
```json
{
	"phoneNumber":"+85266021151",
	"sid":"ACb53b98fdb036d61049759266232ed8e4",
	"token":"c11f1ad436b88c40788cdc24a6fcbcc3"
}
```

## Reference document
Price: https://www.twilio.com/voice/pricing/hk <br >
Voice Recognition: www.twilio.com/docs/voice/twiml/gather#languagetags <br >
Phone call and receive demo: <br >
https://www.youtube.com/watch?v=-AChTCBoTUM<br >
Speech Recognition demo:<br >
www.youtube.com/watch?v=c_ZlQNitLgE <br >
https://www.twilio.com/blog/2017/06/how-to-use-twilio-speech-recognition.html <br >

## Develop account emergency code:
qVZeg9y9XtP5eVzzARMg5l6i5Xdv1Lg9wV9Sm2RE

## Auto start setting
```
cd /usr/sbin
sudo nano api.sh
modify the code as :sudo python3 /home/ubuntu/twilio_chatbot_with_phone/main.py
save it and reboot
```