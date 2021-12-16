import json

import mybackend as bk
from flask import Flask, request, redirect, url_for, jsonify, abort

app = Flask(__name__)


@app.route('/', methods=['GET'])
def handle_recommendation_req():
    start_location = request.args.get('startlocation', type=str)
    time_duration = request.args.get('timeduration', type=int)
    num_of_recommendation = request.args.get('k', type=int)

    try:
        if not bk.check_location_in_db(start_location):
            abort(404, description="Resource not found")

        ret_val = bk.get_location_for_recommendation(start_location, time_duration, num_of_recommendation)
        return json.dumps(ret_val)

    except Exception as e:
        abort(500, description="error in db call")

if __name__ == '__main__':
    app.run(debug=True)

