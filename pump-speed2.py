import RPi.GPIO as GPIO
import time

# Pin GPIO untuk Motor 1 (DRV8833)
AIN1 = 27   # Pin AIN1 sebagai enable Motor 1
PWMA = 12   # Pin PWMA untuk PWM Motor 1

# Pin GPIO untuk Motor 2 (DRV8833)
BIN1 = 6    # Pin BIN1 sebagai enable Motor 2
PWMB = 13   # Pin PWMB untuk PWM Motor 2

# Pin GPIO untuk Standby (DRV8833)
STBY = 22   # Pin STBY
STBY2 = 5   # Pin STBY

# Setup GPIO
GPIO.setmode(GPIO.BCM)

# Konfigurasi pin untuk Motor 1
GPIO.setup(AIN1, GPIO.OUT)
GPIO.setup(PWMA, GPIO.OUT)

# Konfigurasi pin untuk Motor 2
GPIO.setup(BIN1, GPIO.OUT)
GPIO.setup(PWMB, GPIO.OUT)

# Konfigurasi pin untuk Standby
GPIO.setup(STBY, GPIO.OUT)
GPIO.setup(STBY2, GPIO.OUT)
# GPIO.output(STBY, GPIO.HIGH)  # Aktifkan driver motor

#====================

# Inisialisasi PWM
pwm_motor1 = GPIO.PWM(PWMA, 100)  # PWM Motor 1 dengan 100Hz
pwm_motor2 = GPIO.PWM(PWMB, 100)  # PWM Motor 2 dengan 100Hz

pwm_motor1.start(0)  # Mulai PWM Motor 1 dengan duty cycle 0%
pwm_motor2.start(0)  # Mulai PWM Motor 2 dengan duty cycle 0%

GPIO.output(AIN1, GPIO.LOW)
GPIO.output(BIN1, GPIO.LOW)
GPIO.output(STBY, GPIO.LOW)
GPIO.output(STBY2, GPIO.LOW)

# Fungsi untuk mengontrol Motor 1
def motor1_on(speed):
    pwm_motor1.ChangeDutyCycle(speed)  # Atur duty cycle Motor 1
    GPIO.output(AIN1, GPIO.LOW)  # Aktifkan Motor 1
    GPIO.output(STBY, GPIO.HIGH)  # Keluar dari mode standby
    print(f"Motor 1 menyala dengan kecepatan: {speed}%")

def motor1_off():
    pwm_motor1.ChangeDutyCycle(0)  # Set duty cycle Motor 1 ke 0%
    GPIO.output(AIN1, GPIO.LOW)  # Matikan Motor 1
    GPIO.output(STBY, GPIO.LOW)  # Keluar dari mode standby
    print("Motor 1 mati")

# Fungsi untuk mengontrol Motor 2
def motor2_on(speed):
    pwm_motor2.ChangeDutyCycle(speed)  # Atur duty cycle Motor 2
    GPIO.output(BIN1, GPIO.LOW)  # Aktifkan Motor 2
    GPIO.output(STBY2, GPIO.HIGH)  # Keluar dari mode standby
    print(f"Motor 2 menyala dengan kecepatan: {speed}%")

def motor2_off():
    pwm_motor2.ChangeDutyCycle(0)  # Set duty cycle Motor 2 ke 0%
    GPIO.output(BIN1, GPIO.LOW)  # Matikan Motor 2
    GPIO.output(STBY2, GPIO.LOW)  # Keluar dari mode standby
    print("Motor 2 mati")

try:
    while True:
        command = input(
            "Ketik 'm1 pelan', 'm1 sedang', 'm1 cepat', 'm1 off' untuk Motor 1.\n"
            "Ketik 'm2 pelan', 'm2 sedang', 'm2 cepat', 'm2 off' untuk Motor 2.\n"
            "Perintah: "
        ).lower()

        # Kontrol Motor 1
        if command == 'm1 pelan':
            motor1_on(60)  # 60% duty cycle Motor 1 (kecepatan pelan)
        elif command == 'm1 sedang':
            motor1_on(80)  # 80% duty cycle Motor 1 (kecepatan sedang)
        elif command == 'm1 cepat':
            motor1_on(100)  # 100% duty cycle Motor 1 (kecepatan penuh)
        elif command == 'm1 off':
            motor1_off()

        # Kontrol Motor 2
        elif command == 'm2 pelan':
            motor2_on(60)  # 60% duty cycle Motor 2 (kecepatan pelan)
        elif command == 'm2 sedang':
            motor2_on(80)  # 80% duty cycle Motor 2 (kecepatan sedang)
        elif command == 'm2 cepat':
            motor2_on(100)  # 100% duty cycle Motor 2 (kecepatan penuh)
        elif command == 'm2 off':
            motor2_off()

        else:
            print("Perintah tidak valid. Gunakan 'm1 pelan', 'm1 sedang', 'm1 cepat', 'm1 off', atau perintah serupa untuk m2.")

except KeyboardInterrupt:
    print("Program dihentikan oleh pengguna")

finally:
    pwm_motor1.stop()
    pwm_motor2.stop()
    GPIO.cleanup()
