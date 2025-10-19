from machine import Pin, SPI
from mfrc522 import MFRC522
from umqtt.simple import MQTTClient
import network
import time
import json

# ===============================
# KONFIGURASI WIFI & MQTT
# ===============================
WIFI_SSID = "Ikbar"
WIFI_PASS = "keluargaekko6"
BROKER = "192.168.1.14"
CLIENT_ID = "esp32_rfid"
TOPIC_PUB = b"esp32/server"
TOPIC_SUB = b"server/esp32"

# ===============================
# SETUP WIFI
# ===============================
print("🔌 Menghubungkan ke WiFi...")
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(WIFI_SSID, WIFI_PASS)
while not wlan.isconnected():
    time.sleep(0.5)
print("✅ WiFi terhubung:", wlan.ifconfig())

# ===============================
# VARIABEL GLOBAL
# ===============================
current_mode = "read"
client = None
reader = None
led = Pin(2, Pin.OUT)

# ===============================
# CALLBACK SAAT MENERIMA PESAN DARI SERVER
# ===============================
def on_message(topic, msg):
    global current_mode
    print(f"📩 Pesan diterima dari {topic}: {msg}")
    try:
        data = json.loads(msg)
        if "mode" in data:
            current_mode = data["mode"]
            print(f"🔁 Mode diubah ke: {current_mode}")
    except Exception as e:
        print("⚠️ Gagal parse pesan:", e)

# ===============================
# INISIALISASI RFID
# ===============================
def setup_rfid():
    spi = SPI(2, baudrate=1000000, polarity=0, phase=0, sck=Pin(19), mosi=Pin(5), miso=Pin(18))
    rdr = MFRC522(spi=spi, gpio_rst=Pin(16), gpio_cs=Pin(17))
    return rdr

# ===============================
# KONEKSI MQTT
# ===============================
def setup_mqtt():
    client = MQTTClient(CLIENT_ID, BROKER)
    client.set_callback(on_message)
    client.connect()
    client.subscribe(TOPIC_SUB)
    print("✅ Terhubung ke MQTT broker")
    client.publish(TOPIC_PUB, json.dumps({"type": "esp_connect"}))
    return client

# ===============================
# LOOP RFID
# ===============================
def loop():
    global reader, client, current_mode
    print("🚀 Siap membaca kartu RFID...")
    last_uid = None

    while True:
        client.check_msg()

        if(current_mode == "register"):
            led.value(1)
        else:
            led.value(0)

        (stat, tag_type) = reader.request(reader.REQIDL)
        if stat == reader.OK:
            (stat, raw_uid) = reader.anticoll()
            if stat == reader.OK:
                uid = "".join("{:02X}".format(x) for x in raw_uid)

                last_uid = uid
                print(f"💳 Kartu terbaca: {uid}")
                client.publish(TOPIC_PUB, json.dumps({"type": "absen", "uid": uid, "mode": current_mode}))
                if(current_mode == "register"):
                    led.value(0)
                else:
                    led.value(1)
                time.sleep(1)
                if(current_mode == "register"):
                    led.value(1)
                else:
                    led.value(0)

# ===============================
# MAIN PROGRAM
# ===============================
try:
    reader = setup_rfid()
    client = setup_mqtt()
    loop()
except Exception as e:
    print("❌ Error utama:", e)
finally:
    if client:
        client.disconnect()
        print("🔌 MQTT terputus")
