from flask import Flask, request, jsonify
from flask_cors import CORS
import RPi.GPIO as GPIO

# Setup Flask
app = Flask(__name__)
CORS(app)

# Pin GPIO untuk Motor 1
IN1 = 27   
IN2 = 22  
ENA = 13  

# Pin GPIO untuk Motor 2
IN3 = 26 
IN4 = 16    
ENB = 12   

# Setup GPIO
GPIO.setmode(GPIO.BCM)

# Konfigurasi pin untuk Motor 1
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(ENA, GPIO.OUT)

# Konfigurasi pin untuk Motor 2
GPIO.setup(IN3, GPIO.OUT)
GPIO.setup(IN4, GPIO.OUT)
GPIO.setup(ENB, GPIO.OUT)

# Inisialisasi PWM
pwm_motor1 = GPIO.PWM(ENA, 100)  
pwm_motor2 = GPIO.PWM(ENB, 100)  

pwm_motor1.start(0)  
pwm_motor2.start(0)  

# Fungsi untuk mengontrol Motor 1
def motor1_on(direction, speed):
    pwm_motor1.ChangeDutyCycle(speed)
    if direction == 'forward':
        GPIO.output(IN1, GPIO.HIGH)
        GPIO.output(IN2, GPIO.LOW)
    elif direction == 'backward':
        GPIO.output(IN1, GPIO.LOW)
        GPIO.output(IN2, GPIO.HIGH)

def motor1_off():
    pwm_motor1.ChangeDutyCycle(0)
    GPIO.output(ENA, GPIO.LOW)
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)

# Fungsi untuk mengontrol Motor 2
def motor2_on(direction, speed):
    pwm_motor2.ChangeDutyCycle(speed)
    if direction == 'forward':
        GPIO.output(IN3, GPIO.HIGH)
        GPIO.output(IN4, GPIO.LOW)
    elif direction == 'backward':
        GPIO.output(IN3, GPIO.LOW)
        GPIO.output(IN4, GPIO.HIGH)

def motor2_off():
    pwm_motor2.ChangeDutyCycle(0)
    GPIO.output(ENB, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.LOW)

@app.route('/motor1', methods=['POST'])
def control_motor1():
    data = request.get_json()
    direction = data.get('direction', '')
    speed = data.get('speed', 0)

    if direction not in ['forward', 'backward']:
        return jsonify({'error': 'Invalid direction. Use "forward" or "backward".'}), 400
    if not (0 <= speed <= 100):
        return jsonify({'error': 'Speed must be between 0 and 100.'}), 400

    motor1_on(direction, speed)
    return jsonify({'message': f'Motor 1 {direction} at {speed}% speed.'})

@app.route('/motor1/off', methods=['POST'])
def motor1_off_api():
    motor1_off()
    return jsonify({'message': 'Motor 1 turned off.'})

@app.route('/motor2', methods=['POST'])
def control_motor2():
    data = request.get_json()
    direction = data.get('direction', '')
    speed = data.get('speed', 0)

    if direction not in ['forward', 'backward']:
        return jsonify({'error': 'Invalid direction. Use "forward" or "backward".'}), 400
    if not (0 <= speed <= 100):
        return jsonify({'error': 'Speed must be between 0 and 100.'}), 400

    motor2_on(direction, speed)
    return jsonify({'message': f'Motor 2 {direction} at {speed}% speed.'})

@app.route('/motor2/off', methods=['POST'])
def motor2_off_api():
    motor2_off()
    return jsonify({'message': 'Motor 2 turned off.'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
