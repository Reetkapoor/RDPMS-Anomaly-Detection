from flask import Flask, jsonify
import serial

app = Flask(__name__)

# Global variables
ser = None

latest_data = {
    "v50": 0.0,
    "v150": 0.0
}

# Connect to Arduino
try:
    ser = serial.Serial('COM14', 115200, timeout=1)
    print("✓ Connected to COM14")
except Exception as e:
    print("✗ Could not open COM14:", e)
    ser = None


@app.route('/data')
def data():
    global latest_data

    try:
        if ser is not None and ser.in_waiting:
            line = ser.readline().decode('utf-8').strip()

            values = line.split(',')

            if len(values) == 2:
                latest_data["v50"] = float(values[0])
                latest_data["v150"] = float(values[1])

    except Exception as e:
        print("Serial Read Error:", e)

    return jsonify(latest_data)


@app.route('/')
def home():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )