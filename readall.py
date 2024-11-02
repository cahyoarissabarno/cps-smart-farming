import serial
import time

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
        humidity = (response[3] << 8 | response[4]) * 0.1  # RH dalam %
        temperature = (response[5] << 8 | response[6]) * 0.1  # Suhu dalam °C
        conductivity = response[7] << 8 | response[8]  # Konduktivitas dalam us/cm
        ph = (response[9] << 8 | response[10]) * 0.1  # pH
        # nitrogen = response[11] << 8 | response[12]  # Nitrogen dalam mg/L awal
        nitrogen = response[13] << 8 | response[14]  # Nitrogen dalam mg/L
        # phosphorus = response[13] << 8 | response[14]  # Fosfor dalam mg/L awal
        # phosphorus = response[11] << 8 | response[12]  # Fosfor dalam mg/L
        # potassium = response[15] << 8 | response[16]  # Kalium dalam mg/L
        # Menghitung nilai P dan K
        phosphorus = (6.88 / 16) * nitrogen
        potassium = (13.28 / 16) * nitrogen

        # Tampilkan hasil pembacaan
        print(f"Soil Humidity: {humidity}%")
        print(f"Soil Temperature: {temperature}°C")
        print(f"Soil Conductivity: {conductivity} us/cm")
        print(f"Soil pH: {ph}")
        print(f"Nitrogen: {nitrogen} mg/L")
        print(f"Phosphorus: {phosphorus} mg/L")
        print(f"Potassium: {potassium} mg/L")
    else:
        print("Failed to read data or incorrect data length.")

# Panggil fungsi untuk membaca semua parameter
read_all_parameters()

# Tutup komunikasi serial
ser.close()
