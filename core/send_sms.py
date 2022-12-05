import africastalking

# TODO: Initialize Africa's Talking
username = 'Sandbox'
api_key = 'b0bb3a35c726e6e8d381efd9ed1fdf5af917f24d903793ba6e9d6c7b0c527b87'
africastalking.initialize(username, api_key)
africastalking.initialize(
    username='sandbox',
    api_key='b0bb3a35c726e6e8d381efd9ed1fdf5af917f24d903793ba6e9d6c7b0c527b87'
)

sms = africastalking.SMS

class send_sms():

    
        
        #TODO: Send message
        def sending(self):
            # Set the numbers in international format
            recipients = ["+254741433144"]
            # Set your message
            message = "Thank you for settling your bill Promptly"
            # Set your shortCode or senderId
            sender = "Wangetha Water"
            try:
                response = self.sms.send(message, recipients, sender)
                print (response)
            except Exception as e:
                print (f'Houston, we have a problem: {e}')

        pass #delete this code