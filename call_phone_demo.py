from twilio.rest import Client

account_sid = 'AC9ffe4a3ec0e5d977ec8e48bf06faf478'
auth_token = 'd32d0fc46c52384f55286c4dc3bdf48a'
client = Client(account_sid, auth_token)

call = client.calls.create(
                        url='http://demo.twilio.com/docs/voice.xml',
                        to='+85266021151',
                        from_='+15623208460'
                    )
print(call.sid)

