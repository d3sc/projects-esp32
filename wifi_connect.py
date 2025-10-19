import network
import time

SSID = "Testing"
PASSWORD = "testing01"

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(False)   # <-- tambahkan baris ini
    time.sleep(1)
    wlan.active(True)
    
    if not wlan.isconnected():
        print("Menghubungkan ke jaringan Wi-Fi...")
        wlan.connect(SSID, PASSWORD)
        start = time.time()
        while not wlan.isconnected():
            if time.time() - start > 15:
                print("Gagal konek ke Wi-Fi.")
                return None
            time.sleep(1)
    print("Tersambung ke Wi-Fi:", wlan.ifconfig())
    return wlan

if __name__ == "__main__":
    connect_wifi()
