from flask import Flask
from dapr.clients import DaprClient
import json

app = Flask(__name__)

def invoke_microservice_b():
    with DaprClient() as d:
        microservice_b_app_id = "order-processor"
        method_name = "greet"
        message = "this works"
        response = d.invoke_method(app_id=microservice_b_app_id, method_name=method_name, data=json.dumps({'message': message}), http_verb="POST")
        return response.text()

@app.route('/')
def hello():
    # This endpoint still exists to handle HTTP requests to Microservice A
    return "Microservice A is running and ready to handle requests."

if __name__ == '__main__':
    # Invoke the function directly before starting the Flask app
    print("Invoking Microservice B at launch...")
    response_message = invoke_microservice_b()
    print(f"Response from Microservice B: {response_message}")
    
    # Start the Flask application
    app.run(host='0.0.0.0', port=5000, debug=True)
