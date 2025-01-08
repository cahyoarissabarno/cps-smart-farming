import RPi.GPIO as GPIO
import time

# Pin GPIO untuk Motor 1
IN1 = 27   # Pin IN1 (arah Motor 1)
IN2 = 22  # Pin IN2 (arah Motor 1)12
ENA = 13  # Pin ENA (enable Motor 1)22

# Pin GPIO untuk Motor 2
IN3 = 26 # Pin IN3 (arah Motor 2)13
IN4 = 16    # Pin IN4 (arah Motor 2)6
ENB = 12   # Pin ENB (enable Motor 2)5 12

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
pwm_motor1 = GPIO.PWM(ENA, 100)  # PWM Motor 1 dengan 100Hz
pwm_motor2 = GPIO.PWM(ENB, 100)  # PWM Motor 2 dengan 100Hz

pwm_motor1.start(0)  # Mulai PWM Motor 1 dengan duty cycle 0%
pwm_motor2.start(0)  # Mulai PWM Motor 2 dengan duty cycle 0%

# Fungsi untuk mengontrol Motor 1
def motor1_on(direction, speed):
    # GPIO.output(ENA, GPIO.HIGH)  # Aktifkan Motor 1
    pwm_motor1.ChangeDutyCycle(speed)
    if direction == 'forward':
        GPIO.output(IN1, GPIO.HIGH)
        GPIO.output(IN2, GPIO.LOW)
    elif direction == 'backward':
        GPIO.output(IN1, GPIO.LOW)
        GPIO.output(IN2, GPIO.HIGH)
    print(f"Motor 1 menyala, arah: {direction}")

def motor1_off():
    pwm_motor1.ChangeDutyCycle(0)  # Set duty cycle Motor 2 ke 0%
    GPIO.output(ENA, GPIO.LOW)  # Matikan Motor 1
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    print("Motor 1 mati")

# Fungsi untuk mengontrol Motor 2
def motor2_on(direction, speed):
    # GPIO.output(ENB, GPIO.HIGH)  # Aktifkan Motor 2
    pwm_motor2.ChangeDutyCycle(speed)
    if direction == 'forward':
        GPIO.output(IN3, GPIO.HIGH)
        GPIO.output(IN4, GPIO.LOW)
    elif direction == 'backward':
        GPIO.output(IN3, GPIO.LOW)
        GPIO.output(IN4, GPIO.HIGH)
    print(f"Motor 2 menyala, arah: {direction}")

def motor2_off():
    pwm_motor2.ChangeDutyCycle(0)  # Set duty cycle Motor 2 ke 0%
    GPIO.output(ENB, GPIO.LOW)  # Matikan Motor 2
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.LOW)
    print("Motor 2 mati")

motor1_off()
motor2_off()

try:
    while True:
        command = input(
            "Ketik 'm1 maju', 'm1 mundur', 'm1 off' untuk Motor 1.\n"
            "Ketik 'm2 maju', 'm2 mundur', 'm2 off' untuk Motor 2.\n"
            "Perintah: "
        ).lower()

        # Kontrol Motor 1
        if command == 'm1 maju':
            motor1_on('forward', 50)
        elif command == 'm1 mundur':
            motor1_on('backward', 50)
        elif command == 'm1 off':
            motor1_off()

        # Kontrol Motor 2
        elif command == 'm2 maju':
            motor2_on('forward', 50)
        elif command == 'm2 mundur':
            motor2_on('backward', 50)
        elif command == 'm2 off':
            motor2_off()

        else:
            print("Perintah tidak valid. Gunakan 'm1 maju', 'm1 mundur', 'm1 off', atau perintah serupa untuk m2.")

except KeyboardInterrupt:
    print("Program dihentikan oleh pengguna")

finally:
    pwm_motor1.stop()
    pwm_motor2.stop()
    GPIO.cleanup()
