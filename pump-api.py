from flask import Flask, jsonify
import RPi.GPIO as GPIO
import time

app = Flask(__name__)

# Pin GPIO yang digunakan
AIN1 = 17  # Pin kontrol AIN1
AIN2 = 27  # Pin kontrol AIN2
STBY = 22  # Pin standby

# Function to set up GPIO and turn the motor on
def motor_on():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(AIN1, GPIO.OUT)
    GPIO.setup(AIN2, GPIO.OUT)
    GPIO.setup(STBY, GPIO.OUT)
    GPIO.output(AIN1, GPIO.HIGH)
    GPIO.output(AIN2, GPIO.LOW)
    GPIO.output(STBY, GPIO.HIGH)
    print("Motor menyala")
    GPIO.cleanup()  # Reset GPIO after use

# Function to set up GPIO and turn the motor off
def motor_off():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(AIN1, GPIO.OUT)
    GPIO.setup(AIN2, GPIO.OUT)
    GPIO.setup(STBY, GPIO.OUT)
    GPIO.output(AIN1, GPIO.LOW)
    GPIO.output(AIN2, GPIO.LOW)
    GPIO.output(STBY, GPIO.LOW)
    print("Motor mati")
    GPIO.cleanup()  # Reset GPIO after use

# API route to turn the motor on
@app.route('/motor/on', methods=['GET'])
def api_motor_on():
    motor_on()
    return jsonify({"status": "Motor menyala"}), 200

# API route to turn the motor off
@app.route('/motor/off', methods=['GET'])
def api_motor_off():
    motor_off()
    return jsonify({"status": "Motor mati"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
