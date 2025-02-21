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
# output_ser = None
# Fungsi untuk mengambil interface dari database
def get_sensor_interface(device_id, tanaman_no):
    try:
        print("Getting Interface Data From device_id: " + str(device_id) + ", tanaman_no: " + str(tanaman_no))
        response = requests.get(f"http://192.168.1.2:8000/api/sensor?device_id={device_id}&tanaman_no={tanaman_no}")
        if response.status_code == 200:
            sensor_data = response.json().get("data", [])
            if sensor_data:
                return sensor_data[0]['interface']  # Ambil nilai interface dari data sensor
        print("Gagal mengambil data interface dari database")
        return None
    except Exception as e:
        print(f"Error mengambil data interface: {str(e)}")
        return None

# Fungsi untuk membuka koneksi serial berdasarkan interface
def open_serial_connection(interface):
    print("Open Conncetion From Interface " + interface)
    try:
        ser = serial.Serial(
            port=interface,
            baudrate=4800,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=2
        )
        return ser
    except Exception as e:
        print(f"Gagal membuka koneksi serial pada {interface}: {str(e)}")
        return None

def control_pumps(moisture, temperature, tanaman_no, tanaman_name):
    try:
        # Ambil parameter dari tabel pump_params berdasarkan tanaman_no
        response = requests.get(f"http://192.168.1.2:8000/api/pump_params?tanaman_no={tanaman_no}")
        if response.status_code != 200:
            print("Gagal mengambil data pump_params")
            return
        
        pump_params = response.json()
        if not pump_params:
            print("Data pump_params tidak ditemukan")
            return
        
        # Ambil nilai hmin, hmax, tmin, tmax
        hmin = pump_params[0]['h_min']
        hmax = pump_params[0]['h_max']
        tmin = pump_params[0]['t_min']
        tmax = pump_params[0]['t_max']
        water_duration = pump_params[0]['water_duration']
        water_volume = pump_params[0]['water_volume']
        nutri_duration = pump_params[0]['nutri_duration']
        nutri_volume = pump_params[0]['nutri_volume']
        
        print(f"Parameter: Hmin={hmin}, Hmax={hmax}, Tmin={tmin}, Tmax={tmax}")
        
        # Logika kontrol pompa
        if moisture < hmin or temperature > tmax:
            pump_type = "water" 
            # pump_type = "water" if moisture < hmin else "nutrition"
            # duration =   # Durasi get from db
            # volume = 100.0  # Volume air/pupuk (dalam mililiter)
            
            # Nyalakan motor berdasarkan pump_type
            # if pump_type == "water":
            motor_endpoint = "http://192.168.9.59:5000/motor2"
            motor_off_endpoint = "http://192.168.9.59:5000/motor2/off"
            # else:
            #     motor_endpoint = "http://192.168.9.59:5000/motor1"
            #     motor_off_endpoint = "http://192.168.9.59:5000/motor1/off"
            
            try:
                # Nyalakan motor
                response = requests.post(motor_endpoint, json={"direction": "forward", "speed": 90})
                print(f"Pompa {pump_type} dinyalakan:", response.status_code)
                time.sleep(duration)
                
                # Matikan motor
                response = requests.post(motor_off_endpoint)
                print(f"Pompa {pump_type} dimatikan:", response.status_code)
                
                # Simpan history ke database
                history_data = {
                    "tanaman": tanaman_name,
                    "tanaman_no": tanaman_no,
                    "pump_type": pump_type,
                    "method": "auto",
                    "duration": duration,
                    "volume": volume
                }
                response = requests.post("http://192.168.1.2:8000/api/pump_history", json=history_data)
                if response.status_code == 201:
                    print("History pompa berhasil disimpan")
                else:
                    print("Gagal menyimpan history pompa:", response.text)
            except Exception as e:
                print("Gagal mengontrol pompa:", str(e))
        else:
            print("Kondisi tanah optimal, tidak perlu menyalakan pompa.")
    except Exception as e:
        print("Error dalam kontrol pompa:", str(e))

def read_all_parameters(device_id, plant_name, plant_id):
    # Ambil interface dari database
    interface = get_sensor_interface(device_id, plant_id)
    if not interface:
        print("Interface tidak ditemukan untuk device_id dan tanaman_no ini")
        return None
    
    # Buka koneksi serial berdasarkan interface
    sensor_ser = open_serial_connection(interface)
    if not sensor_ser:
        return None
    
    # Kirim query dan baca respons
    sensor_ser.write(query_all)
    time.sleep(0.1)
    response = sensor_ser.read(17)
    sensor_ser.close()  # Tutup koneksi serial setelah selesai

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

        # Panggil fungsi kontrol pompa
        control_pumps(humidity, temperature, plant_id, plant_name)

        return sensor_data_json
    else:
        print("Failed to read data or incorrect data length.")
        return None

try:
    data = requests.get("http://192.168.1.2:8000/api/tanaman").json().get("data", [])
    for item in data:
        print("#####" + "soil_sensor_id: " + str(item["soil_sensor_id"]) + "tanaman: " + item["tanaman"] + "tanaman_no: " + str(item["tanaman_no"]) + "#####")
        
        sensor_data = read_all_parameters(item["soil_sensor_id"], item["tanaman"], item["tanaman_no"])
        print("Data get:", sensor_data)

        if sensor_data:
            # Kirim data sensor sebagai payload JSON melalui API
            try:
                response = requests.post("http://127.0.0.1:8000/api/add_data", json=sensor_data)
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
# output_ser.close()  # Tutup port untuk mengirim data