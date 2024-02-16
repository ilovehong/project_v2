from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

class HKBU_ChatGPT:
    def __init__(self):
        self.basicurl = os.environ.get('CHATGPT_BASICURL')
        self.modelname = os.environ.get('CHATGPT_MODELNAME')
        self.apiversion = os.environ.get('CHATGPT_APIVERSION')
        self.access_token = os.environ.get('CHATGPT_ACCESS_TOKEN')

    def submit(self, message):
        conversation = [{"role": "user", "content": message}]
        url = (self.basicurl) + "/deployments/" + (self.modelname) + "/chat/completions/?api-version=" + (self.apiversion)
        headers = {'Content-Type': 'application/json', 'api-key': (self.access_token)}
        payload = {'messages': conversation}
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data['choices'][0]['message']['content']
        else:
            return 'Error:', response.status_code

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    message = data['message']
    chatgpt = HKBU_ChatGPT()
    response_message = chatgpt.submit(message)
    return jsonify({"message": response_message})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
