from twilio.rest import Client

account_sid = 'ACb53b98fdb036d61049759266232ed8e4'
auth_token = 'c11f1ad436b88c40788cdc24a6fcbcc3'
client = Client(account_sid, auth_token)

call = client.calls.create(
                        url='http://demo.twilio.com/docs/voice.xml',
                        to='+85266021151',
                        from_='+85264507224'
                    )
print(call.sid)

