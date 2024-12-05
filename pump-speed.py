import RPi.GPIO as GPIO
import time

# Pin GPIO yang digunakan
PWM_PIN = 12  # Pin PWM pada Raspberry Pi 3
AIN2 = 27     # Pin kontrol AIN2
STBY = 22     # Pin standby

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(PWM_PIN, GPIO.OUT)
GPIO.setup(AIN2, GPIO.OUT)
GPIO.setup(STBY, GPIO.OUT)

#====================

# Inisialisasi PWM pada pin PWM_PIN (GPIO 12)
pwm_motor = GPIO.PWM(PWM_PIN, 100)  # 100Hz frekuensi PWM
pwm_motor.start(0)  # Mulai PWM dengan duty cycle 0%

GPIO.output(AIN2, GPIO.LOW)
GPIO.output(STBY, GPIO.LOW)

def motor_on(speed):
    # Menyalakan motor dengan PWM di pin PWM_PIN dan AIN2 LOW (rotasi searah)
    pwm_motor.ChangeDutyCycle(speed)  # Mengatur kecepatan berdasarkan duty cycle
    GPIO.output(AIN2, GPIO.LOW)
    GPIO.output(STBY, GPIO.HIGH)  # Keluar dari mode standby
    print(f"Motor menyala dengan kecepatan: {speed}%")

def motor_off():
    # Mematikan motor dengan PWM diatur ke 0% dan AIN2 LOW
    pwm_motor.ChangeDutyCycle(0)  # Set duty cycle ke 0%
    GPIO.output(AIN2, GPIO.LOW)
    GPIO.output(STBY, GPIO.LOW)  # Kembali ke mode standby
    print("Motor mati")

try:
    while True:
        command = input("Ketik 'pelan', 'sedang', 'cepat' untuk mengatur kecepatan, atau 'off' untuk mematikan motor: ").lower()
        if command == 'pelan':
            motor_on(60)  # 60% duty cycle untuk kecepatan pelan
        elif command == 'sedang':
            motor_on(80)  # 80% duty cycle untuk kecepatan sedang
        elif command == 'cepat':
            motor_on(100)  # 100% duty cycle untuk kecepatan cepat
        elif command == 'off':
            motor_off()
        else:
            print("Perintah tidak valid, gunakan 'pelan', 'sedang', 'cepat', atau 'off'.")

except KeyboardInterrupt:
    print("Program dihentikan oleh pengguna")

finally:
    pwm_motor.stop()  # Hentikan PWM
    GPIO.cleanup()  # Membersihkan pengaturan GPIO setelah program selesai