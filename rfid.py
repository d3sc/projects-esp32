from machine import Pin, SPI
from mfrc522 import MFRC522
import time

# --- Setup SPI dan MFRC522 ---
spi = SPI(2, baudrate=1000000, polarity=0, phase=0,
          sck=Pin(19), mosi=Pin(5), miso=Pin(18))
rdr = MFRC522(spi=spi, gpio_rst=Pin(16), gpio_cs=Pin(17))

last_uid = None

while True:
    # Mencari kartu yang berada di dekat reader
    (stat, tag_type) = rdr.request(rdr.REQIDL)
    
    if stat == rdr.OK:
        # Kartu ditemukan, ambil UID
        (stat2, raw_uid) = rdr.anticoll()
        if stat2 == rdr.OK:
            uid = "".join("{:02X}".format(x) for x in raw_uid)
            if uid != last_uid:
                last_uid = uid
                print(f"💳 UID Kartu: {uid}")
        else:
            print("❌ Gagal membaca UID")
    else:
        print("❌ Tidak ada kartu terdeteksi")
    
    time.sleep(1)
