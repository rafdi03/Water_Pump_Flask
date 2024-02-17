from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import json
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

state_data = {
    "state": "ON"
}


def read_data():
    data = []
    with open('data.txt', 'r') as file:
        lines = file.readlines()
        for line in lines[1:]:  # Skip the header line
            values = line.strip().split()
            kekeruhan_air = float(values[0])
            status_pompa = int(values[1])
            timestamp = values[2:]
            combined_timestamp = " ".join(timestamp)

            data.append({
                'Timestamp': combined_timestamp,
                'Kekeruhan_Air': kekeruhan_air,
                'Status_Pompa': status_pompa,
            })

    return data


def read_data_status_pompa():
    data = []
    with open('data_status_pompa.txt', 'r') as file:
        lines = file.readlines()
        for line in lines[1:]:  # Skip the header line
            values = line.strip().split()
            status_pompa = values[0]
            timestamp = values[2:]
            combined_timestamp = " ".join(timestamp)

            data.append({
                'Timestamp': combined_timestamp,
                'Status_Pompa': status_pompa,
            })

    return data


@app.route("/")
def index():
    data = read_data()
    data_status_pompa = read_data_status_pompa()
    print(data)
    return render_template("index.html",
                           data=data,
                           pump_status=state_data["state"],
                           data_status_pompa=data_status_pompa)


@app.route("/api/add_data", methods=["POST"])
def add_data():
    global pump_status

    if request.method == "POST":
        new_data = request.get_json()
        print(new_data)
        if new_data:
            timestamp_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            kekeruhan_air = new_data["Kekeruhan_Air"]
            status_pompa = new_data["Status_Pompa"]

            pump_status = status_pompa

            # Handle both full timestamp and date-only timestamp
            try:
                timestamp = datetime.datetime.strptime(
                    timestamp_str, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                timestamp = datetime.datetime.strptime(
                    timestamp_str, '%Y-%m-%d')

            with open('data.txt', 'a') as file:
                file.write(f"{kekeruhan_air} {status_pompa} {timestamp}\n")

            socketio.emit('update data', {'data': read_data()})
            socketio.emit('pump status', {'status': pump_status})

            return jsonify({
                "message": "Data added successfully"
            }), 201
        else:
            return jsonify({
                "error": "Invalid JSON data"
            }), 400


@app.route("/control_state", methods=["GET", "POST"])
def control_state():
    if request.method == "POST":
        global state_data
        input_data = request.get_json()
        state = input_data["state"]
        timestamp_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(input_data)
        
        with open('data_status_pompa.txt', 'a') as file:
            file.write(f"{state} {timestamp_str}\n")

        if state:
            state_data["state"] = state
            return jsonify({
                "status": {
                    "code": 200,
                    "message": "Success changing the state",
                },
                "data": {
                    "state": state_data["state"]
                },
            }), 200
        else:
            return jsonify({
                "status": {
                    "code": 400,
                    "message": "No state detected"
                },
                "data": None,
            }), 400
    else:
        return jsonify(state_data)


@app.route("/state_iot")
def state_iot():
    return jsonify(state_data)


@socketio.on('connect')
def test_connect():
    emit('after connect', {'data': 'Connected'})


@socketio.on('request data')
def handle_request_data():
    data = read_data()
    data_status_pompa = read_data_status_pompa()
    print("***" * 15)
    print(data)
    print("===" * 15)
    print(data_status_pompa)
    emit('update data', {'data': data, 'data_status_pompa': data_status_pompa})


if __name__ == "__main__":
    socketio.run(app, debug=True)
