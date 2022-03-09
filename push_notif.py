import requests
import json

class PushBullet:
    def __init__(self, access_token) -> None:
        self.auth_token = access_token
    
    def push_note(self, title, body):
        payload = {
            "type": "note",
            "title": title,
            "body": body,
        }

        res = requests.post(
            url='https://api.pushbullet.com/v2/pushes',
            data=json.dumps(payload),
            headers={'Authorization': f'Bearer {self.auth_token}', 'Content-Type': 'application/json'}
        )
        
        if res.status_code != 200:
            raise Exception(res.content)
