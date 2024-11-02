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

# Fungsi untuk menulis nilai ke register tertentu
def write_register(register, value):
    query = append_crc(bytes([0x01, 0x06, (register >> 8) & 0xFF, register & 0xFF, (value >> 8) & 0xFF, value & 0xFF]))
    ser.write(query)  # Kirim query ke sensor
    time.sleep(0.1)  # Tunggu sebentar untuk respon

    response = ser.read(8)  # Membaca 8 byte respons
    if response == query:
        print(f"Successfully wrote {value} to register {hex(register)}.")
    else:
        print(f"Failed to write {value} to register {hex(register)}. Response: {response}")

# Membuka komunikasi serial dengan konverter RS485 to USB
ser = serial.Serial(
    port='/dev/ttyUSB0',  # Sesuaikan dengan port USB pada Raspberry Pi
    baudrate=4800,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=2  # Timeout 2 detik untuk menunggu data
)

# Menulis nilai ke register masing-masing
write_register(0x0004, 0)  # Menulis 32 ke Nitrogen
# write_register(0x0005, 88)  # Menulis 88 ke Phosphorus
# write_register(0x0006, 104) # Menulis 104 ke Potassium

# Tutup komunikasi serial
ser.close()
