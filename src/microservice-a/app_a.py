from flask import Flask
from dapr.clients import DaprClient

app = Flask(__name__)

@app.before_first_request
def invoke_microservice_b_and_print():
    with DaprClient() as d:
        microservice_b_app_id = "microservice-b"
        method_name = "greet"
        response = d.invoke_method(app_id=microservice_b_app_id, method_name=method_name, http_verb="get")
        print(f"Response from microservice B: {response.text()}")

@app.route('/')
def hello():
    return "Microservice A is running."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
