# Dokumentasi Penggunaan MPRemote dengan ESP32

MPRemote adalah tool dari **MicroPython** untuk mengelola ESP32. Dengan MPRemote, kamu bisa **mengirim file**, **menjalankan script**, **masuk ke terminal REPL**, dan **mengelola filesystem**.

---

## 📦 Persiapan

1. Pastikan ESP32 terhubung ke komputer via USB.
2. Install MPRemote:
   ```bash
   pip install mpremote


mpremote connect /dev/ttyUSB0 run main.py


mpremote connect /dev/ttyUSB0 cp main.py :main.py


mpremote connect /dev/ttyUSB0 repl


mpremote connect /dev/ttyUSB0 exec "print('Hello ESP32')"


mpremote connect /dev/ttyUSB0 fs ls


mpremote connect /dev/ttyUSB0 fs rm main.py
