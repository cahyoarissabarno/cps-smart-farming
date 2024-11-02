import serial
import time
import paho.mqtt.client as mqtt

# Konfigurasi MQTT
hostname = "127.0.0.1"
broker_port = 1883
topic = "sensor-npk"
client = mqtt.Client()

# Fungsi untuk menghitung CRC16-Modbus
def calculate_crc(data):
    crc = 0xFFFF
    for pos in data:
        crc ^= pos
        for _ in range(8):
            if (crc & 1) != 0:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return crc

# Tambahkan CRC ke query Modbus
def append_crc(query):
    crc_value = calculate_crc(query)
    return query + bytes([crc_value & 0xFF, (crc_value >> 8) & 0xFF])

# Query untuk membaca semua parameter (kelembapan, suhu, konduktivitas, pH, N, P, K)
query_all = append_crc(bytes([0x01, 0x03, 0x00, 0x00, 0x00, 0x07]))

# Membuka komunikasi serial dengan konverter RS485 to USB
ser = serial.Serial(
    port='/dev/ttyUSB0',  # Sesuaikan dengan port USB pada Raspberry Pi
    baudrate=4800,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=2  # Timeout 2 detik untuk menunggu data
)

def read_all_parameters():
    ser.write(query_all)  # Kirim query ke sensor
    time.sleep(0.1)  # Tunggu sebentar untuk respon

    response = ser.read(17)  # Membaca 17 byte respon sesuai spesifikasi (1 byte alamat + 1 byte fungsi + 14 byte data + 2 byte CRC)
    if len(response) == 17:
        # Parsing data dari respons
        humidity = round((response[3] << 8 | response[4]) * 0.1)  # RH dalam %
        temperature = round((response[5] << 8 | response[6]) * 0.1)  # Suhu dalam °C
        conductivity = response[7] << 8 | response[8]  # Konduktivitas dalam us/cm
        ph = round((response[9] << 8 | response[10]) * 0.1)  # pH
        nitrogen = response[13] << 8 | response[14]  # Nitrogen dalam mg/L
        phosphorus = (6.88 / 16) * nitrogen
        potassium = (13.28 / 16) * nitrogen

        # Tampilkan hasil pembacaan
        sensor_data = {
            "Soil Humidity": humidity,
            "Soil Temperature": temperature,
            "Soil Conductivity": conductivity,
            "Soil pH": ph,
            "Nitrogen": nitrogen,
            "Phosphorus": round(phosphorus),
            "Potassium": round(potassium)
        }
        return sensor_data
    else:
        print("Failed to read data or incorrect data length.")
        return None

# Menghubungkan ke broker MQTT
client.connect(hostname, broker_port, 60)
client.loop_start()

# Loop untuk membaca semua sensor berulang kali dan mengirimkan hasil melalui MQTT
# while True:
print("############")
sensor_data = read_all_parameters()  # Membaca semua parameter
if sensor_data:
    # Menampilkan data sensor
    for key, value in sensor_data.items():
        print(f"{key}: {value}")

    # Kirim data sensor sebagai payload JSON melalui MQTT
    client.publish(topic, str(sensor_data))
else:
    print("Tidak ada data yang diterima.")

print("############")
# time.sleep(30)  # Tunggu 30 detik sebelum pembacaan berikutnyas

# Tutup komunikasi serial dan loop MQTT
client.loop_stop()
ser.close()
