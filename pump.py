import RPi.GPIO as GPIO
import time

# Setup
GPIO.setmode(GPIO.BCM)  # Gunakan penomoran GPIO (BCM)
GPIO.setup(23, GPIO.OUT)  # Set GPIO 23 sebagai output
GPIO.setup(24, GPIO.OUT)

#GPIO.output(23, GPIO.LOW)
#GPIO.output(24, GPIO.LOW)

def turn_on_gpio():
    GPIO.output(23, GPIO.HIGH)  # Menyalakan GPIO 23
    GPIO.output(24, GPIO.LOW)
    print("GPIO 23 menyala")

def turn_off_gpio():
    GPIO.output(23, GPIO.LOW)  # Mematikan GPIO 23
    GPIO.output(24, GPIO.LOW)
    print("GPIO 23 mati")

try:
    while True:
        command = input("Ketik 'on' untuk menyalakan atau 'off' untuk mematikan GPIO 23: ").lower()
        if command == 'on':
            turn_on_gpio()
        elif command == 'off':
            turn_off_gpio()
        else:
            print("Perintah tidak valid, gunakan 'on' atau 'off'.")

except KeyboardInterrupt:
    print("Program dihentikan oleh pengguna")

finally:
    GPIO.cleanup()  # Membersihkan semua konfigurasi GPIO setelah program selesai
