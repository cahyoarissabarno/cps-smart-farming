from flask import Flask, request, jsonify
import RPi.GPIO as GPIO

app = Flask(__name__)

# Pin GPIO yang digunakan
AIN1 = 17  # Pin kontrol AIN1
AIN2 = 27  # Pin kontrol AIN2
STBY = 22  # Pin standby

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(AIN1, GPIO.OUT)
GPIO.setup(AIN2, GPIO.OUT)
GPIO.setup(STBY, GPIO.OUT)
GPIO.output(AIN1, GPIO.LOW)
GPIO.output(AIN2, GPIO.LOW)
GPIO.output(STBY, GPIO.LOW)

# Function to turn the motor on
def motor_on():
    GPIO.output(AIN1, GPIO.HIGH)
    GPIO.output(AIN2, GPIO.LOW)
    GPIO.output(STBY, GPIO.HIGH)  # Keluar dari mode standby
    print("Motor menyala")

# Function to turn the motor off
def motor_off():
    GPIO.output(AIN1, GPIO.LOW)
    GPIO.output(AIN2, GPIO.LOW)
    GPIO.output(STBY, GPIO.LOW)  # Kembali ke mode standby
    print("Motor mati")

# API route to control the motor
@app.route('/motor/control', methods=['POST'])
def motor_control():
    data = request.get_json()  # Get JSON data from request
    if not data or 'state' not in data:
        return jsonify({"error": "Invalid input, 'state' required"}), 400

    # Check if the state is 1 (on) or 0 (off)
    state = data['state']
    if state == 1:
        motor_on()
        return jsonify({"status": "Motor menyala"}), 200
    elif state == 0:
        motor_off()
        return jsonify({"status": "Motor mati"}), 200
    else:
        return jsonify({"error": "Invalid state. Use 1 for on, 0 for off"}), 400

# Cleanup GPIO when server shuts down
@app.route('/shutdown', methods=['POST'])
def shutdown():
    GPIO.cleanup()  # Cleanup GPIO
    return jsonify({"status": "GPIO cleaned up"}), 200

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5001)
    except KeyboardInterrupt:
        GPIO.cleanup()  # Ensure GPIO is cleaned up on keyboard interrupt
