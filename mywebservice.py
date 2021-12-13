import mybackend
from flask import Flask, request, redirect, url_for,jsonify

app = Flask(__name__)


@app.route('/', methods=['GET'])
def handle_recommendation_req():
    start_location = request.args.get('startlocation', type=str)
    time_duration = request.args.get('timeduration', type=int)
    num_of_recommendation = request.args.get('k', type=int)
    ret_val = mybackend.get_location_for_recommendation(start_location, time_duration, num_of_recommendation)
    return jsonify(ret_val)

if __name__ == '__main__':
    app.run(debug=True)

