import socket
from machine import Pin
from wifi_connect import connect_wifi

led = Pin(2, Pin.OUT)  # LED bawaan ESP32
wlan = connect_wifi()

if wlan and wlan.isconnected():
    ip = wlan.ifconfig()[0]
    print(f"Web server berjalan di http://{ip}")

    # Membuat socket server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 80))
    s.listen(5)

    while True:
        conn, addr = s.accept()
        print("Koneksi dari", addr)
        request = conn.recv(1024)
        request = str(request)

        # Deteksi URL
        if '/on' in request:
            led.value(1)
        elif '/off' in request:
            led.value(0)

        # HTML respons
        html = f"""HTTP/1.1 200 OK

<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>ESP32 Web Server</title>
  <style>
    body {{ text-align: center; font-family: Arial; background: #f2f2f2; }}
    h1 {{ color: #333; }}
    button {{
      font-size: 20px; padding: 15px 30px; margin: 10px;
      border: none; border-radius: 8px; cursor: pointer;
    }}
    .on {{ background-color: #4CAF50; color: white; }}
    .off {{ background-color: #f44336; color: white; }}
  </style>
</head>
<body>
  <h1>ESP32 Web Server</h1>
  <p>LED Status: {"ON" if led.value() else "OFF"}</p>
  <p>
    <a href="/on"><button class="on">Turn ON</button></a>
    <a href="/off"><button class="off">Turn OFF</button></a>
  </p>
</body>
</html>
"""
        conn.send(html)
        conn.close()
else:
    print("Tidak dapat konek Wi-Fi, server tidak dijalankan.")
