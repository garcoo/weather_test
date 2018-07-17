import requests
import yaml

class ControlChatwork():

    def __init__(self):

        # read yaml
        with open('application.yaml', 'rt') as fp:
            text = fp.read()
        data = yaml.safe_load(text)
        self.crient_id = data['api']['chatwork']['client_id']
        self.base_url = data['api']['chatwork']['base_url']
          
    
    # do talk
    def talk(self, room_id, message):
        
        url = '%s/rooms/%s/messages' % (self.base_url , room_id)
        headers = { 'X-ChatWorkToken': self.crient_id }
        params = { 'body': message }

        resp = requests.post(url,
                     headers=headers,
                     params=params)
        print(resp.content)