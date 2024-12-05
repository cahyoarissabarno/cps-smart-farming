import Adafruit_DHT

# Tentukan tipe sensor (DHT11) dan GPIO yang digunakan
SENSOR = Adafruit_DHT.DHT11
PIN = 23  # Gunakan GPIO 23

def read_dht11():
    # Membaca suhu dan kelembapan
    humidity, temperature = Adafruit_DHT.read(SENSOR, PIN)

    if humidity is not None and temperature is not None:
        print(f"Suhu: {temperature:.1f}°C")
        print(f"Kelembapan: {humidity:.1f}%")
    else:
        print("Gagal membaca data dari sensor. Coba lagi.")

if __name__ == "__main__":
    while True:
        read_dht11()

