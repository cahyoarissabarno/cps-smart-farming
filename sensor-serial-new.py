import serial
import time
import paho.mqtt.client as mqtt
import Adafruit_DHT
import requests  # Import the requests library

DHT = Adafruit_DHT.DHT11
DHT_PIN = 23  

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
sensor_ser_1 = serial.Serial(port='/dev/ttyUSB0',baudrate=4800,parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE,bytesize=serial.EIGHTBITS,timeout=2)
# sensor_ser_2 = serial.Serial(port='/dev/ttyUSB1',baudrate=4800,parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE,bytesize=serial.EIGHTBITS,timeout=2)
# sensor_ser_3 = serial.Serial(port='/dev/ttyUSB2',baudrate=4800,parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE,bytesize=serial.EIGHTBITS,timeout=2)
# sensor_ser_4 = serial.Serial(port='/dev/ttyUSB3',baudrate=4800,parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE,bytesize=serial.EIGHTBITS,timeout=2)

# Konfigurasi komunikasi serial untuk mengirim data
output_ser = serial.Serial(port='/dev/ttyS0',baudrate=9600,parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE,bytesize=serial.EIGHTBITS,timeout=2)

def control_pumps(moisture, temperature):
    Hmin, Hmax = 40.0, 60.0  # Batas kelembapan tanah optimal
    Tmin, Tmax = 18.0, 30.0  # Batas suhu tanah optimal
    print("checking pump ....")
    
    if moisture < Hmin or temperature > Tmax:
        try:
            # Nyalakan motor1 selama 10 detik
            response = requests.post("http://192.168.9.59:5000/motor1", json={"direction": "forward", "speed": 90})
            print("Pompa air dinyalakan:", response.status_code)
            time.sleep(10)
            
            # Matikan motor1
            response = requests.post("http://192.168.9.59:5000/motor1/off")
            print("Pompa air dimatikan:", response.status_code)
            
            # Nyalakan motor2 selama 10 detik
            response = requests.post("http://192.168.9.59:5000/motor2", json={"direction": "forward", "speed": 90})
            print("Pompa pupuk dinyalakan:", response.status_code)
            time.sleep(10)
            
            # Matikan motor2
            response = requests.post("http://192.168.9.59:5000/motor2/off")
            print("Pompa pupuk dimatikan:", response.status_code)
        except Exception as e:
            print("Gagal mengontrol pompa:", str(e))
    else:
        print("Kondisi tanah optimal, tidak perlu menyalakan pompa.")

def read_all_parameters(device_id, plant_name, plant_id):
    if device_id == 1:
        print("get data via sensor 1")
        sensor_ser_1.write(query_all)
        time.sleep(0.1)
        response = sensor_ser_1.read(17)
    # elif device_id == 2:
    #     sensor_ser_2.write(query_all)
    #     time.sleep(0.1)
    #     response = sensor_ser_2.read(17)
    # elif device_id == 3:
    #     sensor_ser_3.write(query_all)
    #     time.sleep(0.1)
    #     response = sensor_ser_3.read(17)
    # elif device_id == 4:
    #     sensor_ser_4.write(query_all)
    #     time.sleep(0.1)
    #     response = sensor_ser_4.read(17)
    else:
        raise ValueError("Invalid device ID")

    if len(response) == 17:
        # Parsing data dari respons
        humidity = round((response[3] << 8 | response[4]) * 0.1) if response[3] != None else 0
        temperature = round((response[5] << 8 | response[6]) * 0.1) if response[5] != None else 0
        conductivity = response[7] << 8 | response[8] if response[7] != None else 0
        ph = round((response[9] << 8 | response[10]) * 0.1) if response[9] != None else 0
        nitrogen = response[13] << 8 | response[14] if response[13] != None else 0
        phosphorus = (6.88 / 16) * nitrogen
        potassium = (13.28 / 16) * nitrogen

        # Retry membaca DHT sensor jika gagal
        MAX_RETRY = 3
        air_hum, air_temp = None, None
        for _ in range(MAX_RETRY):
            print("retry read DHT")
            air_hum, air_temp = Adafruit_DHT.read(DHT, DHT_PIN)
            if air_hum is not None and air_temp is not None:
                break
            time.sleep(1)

        # Gunakan nilai default jika pembacaan DHT gagal
        if air_hum is None:
            air_hum = 0
        if air_temp is None:
            air_temp = 0

        # Tampilkan hasil pembacaan dengan satuan
        sensor_data_print = {
            "Soil Humidity (%)": f"{humidity} %",
            "Soil Temperature (°C)": f"{temperature} °C",
            "Soil Conductivity (us/cm)": f"{conductivity} us/cm",
            "Soil pH": f"{ph}",
            "Nitrogen (mg/L)": f"{nitrogen} mg/L",
            "Phosphorus (mg/L)": f"{round(phosphorus)} mg/L",
            "Potassium (mg/L)": f"{round(potassium)} mg/L",
            "Air_Temp (C)": f"{round(air_temp)} C",
            "Air_Hum (%)": f"{round(air_hum)} %"
        }
        print(sensor_data_print)

        sensor_data_json = {
            "soil_hum": humidity,
            "soil_temp": temperature,
            "soil_cond": conductivity,
            "soil_ph": ph,
            "soil_nitrogen": nitrogen,
            "soil_phosphorus": round(phosphorus),
            "soil_potassium": round(potassium),
            "air_temp": round(air_temp),
            "air_hum": round(air_hum),
            "tanaman": plant_name,
            "tanaman_no": plant_id,
            "soil_sensor_id": device_id
        }

        control_pumps(humidity, temperature)

        return sensor_data_json
    else:
        print("Failed to read data or incorrect data length.")
        return None

try:
    data = requests.get("http://192.168.1.2:8000/api/tanaman").json().get("data", [])
    for item in data:
        # Loop untuk membaca semua sensor berulang kali dan mengirimkan hasil melalui Serial
        print("#####" + str(item["soil_sensor_id"]) + item["tanaman"] + str(item["tanaman_no"]) + "#####")
        
        data_sensor = requests.get("http://192.168.1.2:8000/api/sensor?tanaman_no=" + str(item["tanaman_no"]) + "&device_id=" + str(item["soil_sensor_id"])).json().get("data", [])
        print("tanaman_no=" + str(item["tanaman_no"]) + "&device_id=" + str(item["soil_sensor_id"]))
        
        # sensor_data = read_all_parameters(1, "cabai", 1)  # Membaca semua parameter
        sensor_data = read_all_parameters(item["soil_sensor_id"], item["tanaman"], item["tanaman_no"])
        # sensor_data = {"test":"testing"}
        print("Data get:", sensor_data)

        if sensor_data:
            # Menampilkan data sensor
            for key, value in sensor_data.items():
                print(f"{key}: {value}")

            # Kirim data sensor sebagai payload JSON melalui port serial output
            serial_data = str(sensor_data).encode('utf-8')
            output_ser.write(serial_data)
            print("Data sent to serial:", sensor_data)

            # Kirim data sensor sebagai payload JSON melalui API
            try:
                response = requests.post("http://127.0.0.1:8000/api/add_data", json=sensor_data)  # Kirim data ke API
                if response.status_code == 201:
                    print("Data sent to DB via API successfully!")
                else:
                    print(f"Failed to send data to API: {response.status_code}, {response.text}")
            except Exception as e:
                print(f"Error sending data to API: {str(e)}")
        else:
            print("Tidak ada data yang diterima.")

        print("###### END #####")

except requests.exceptions.RequestException as e:
    print(f"Error: {e}")


# Tutup komunikasi serial dan loop MQTT
output_ser.close()  # Tutup port untuk mengirim data
sensor_ser_1.close()

