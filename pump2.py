import RPi.GPIO as GPIO
import time

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

def motor_on():
    # Menyalakan motor dengan AIN1 HIGH dan AIN2 LOW (rotasi searah)
    GPIO.output(AIN1, GPIO.HIGH)
    GPIO.output(AIN2, GPIO.LOW)
    GPIO.output(STBY, GPIO.HIGH)  # Keluar dari mode standby
    print("Motor menyala")

def motor_off():
    # Mematikan motor dengan AIN1 dan AIN2 LOW
    GPIO.output(AIN1, GPIO.LOW)
    GPIO.output(AIN2, GPIO.LOW)
    GPIO.output(STBY, GPIO.LOW)  # Kembali ke mode standby
    print("Motor mati")

try:
    while True:
        command = input("Ketik 'on' untuk menyalakan atau 'off' untuk mematikan motor: ").lower()
        if command == 'on':
            motor_on()
        elif command == 'off':
            motor_off()
        else:
            print("Perintah tidak valid, gunakan 'on' atau 'off'.")

except KeyboardInterrupt:
    print("Program dihentikan oleh pengguna")

finally:
    GPIO.cleanup()  # Membersihkan pengaturan GPIO setelah program selesai
