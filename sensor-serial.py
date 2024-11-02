import serial
import time

# Konfigurasi komunikasi serial untuk membaca dari sensor
sensor_ser = serial.Serial(
    port='/dev/ttyUSB0',  # Port USB untuk membaca dari sensor
    baudrate=4800,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=2  # Timeout 2 detik untuk menunggu data
)

# Konfigurasi komunikasi serial untuk mengirim data
output_ser = serial.Serial(
    port='/dev/ttyS0',  # Port serial untuk mengirim data
    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=2  # Timeout 2 detik untuk menunggu data
)

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

# Query untuk berbagai sensor
queries = {
    'humi': append_crc(bytes([0x01, 0x03, 0x00, 0x00, 0x00, 0x01])),
    'temp': append_crc(bytes([0x01, 0x03, 0x00, 0x01, 0x00, 0x01])),
    'cond': append_crc(bytes([0x01, 0x03, 0x00, 0x02, 0x00, 0x01])),
    'phph': append_crc(bytes([0x01, 0x03, 0x00, 0x03, 0x00, 0x01])),
    'nitro': append_crc(bytes([0x01, 0x03, 0x00, 0x04, 0x00, 0x01])),
    'phos': append_crc(bytes([0x01, 0x03, 0x00, 0x05, 0x00, 0x01])),
    'pota': append_crc(bytes([0x01, 0x03, 0x00, 0x06, 0x00, 0x01])),
    'sali': append_crc(bytes([0x01, 0x03, 0x00, 0x07, 0x00, 0x01])),
    'tds': append_crc(bytes([0x01, 0x03, 0x00, 0x08, 0x00, 0x01])),
}

def read_sensor(query_name, query_data):
    sensor_ser.write(query_data)  # Kirim query ke sensor
    time.sleep(0.1)  # Tunggu sebentar untuk respon

    response = sensor_ser.read(7)  # Membaca 7 byte respon (sesuaikan jika perlu)
    if len(response) == 7:
        # Menggabungkan byte menjadi nilai 16-bit
        value = (response[3] << 8) + response[4]

        # Format hasil sesuai sensor
        if query_name == 'humi':
            value = round(value * 0.1, 1)  # Kelembapan (%)
        elif query_name == 'temp':
            value = round(value * 0.1, 1)  # Suhu (°C)
        elif query_name == 'cond':
            value = value  # Konduktivitas
        elif query_name == 'phph':
            value = round(value * 0.1, 1)  # pH
        elif query_name in ['nitro', 'phos', 'pota']:
            value = value  # Nitrogen, Fosfor, Kalium (nilai sesuai spesifikasi sensor)

        return value
    else:
        return None

# Loop untuk membaca semua sensor berulang kali dan mengirimkan hasil melalui serial
try:
    while True:
        print("############")
        sensor_data = {}  # Untuk menyimpan data sensor sebelum dikirim
        for query_name, query_data in queries.items():
            value = read_sensor(query_name, query_data)
            if value is not None:
                sensor_data[query_name] = value  # Simpan data sensor
                print(f"{query_name.capitalize()}: {value}")
            else:
                print(f"Timeout waiting for data: {query_name}")
        
        # Kirim data sensor sebagai payload JSON melalui port serial output
        serial_data = str(sensor_data).encode('utf-8')
        output_ser.write(serial_data)
        
        print("Data sent:", sensor_data)
        print("############")
        time.sleep(10)  # Tunggu 10 detik sebelum pembacaan berikutnya

except KeyboardInterrupt:
    print("Program dihentikan.")
finally:
    # Tutup komunikasi serial
    sensor_ser.close()  # Tutup port untuk membaca dari sensor
    output_ser.close()  # Tutup port untuk mengirim data
    print("Port serial ditutup.")
