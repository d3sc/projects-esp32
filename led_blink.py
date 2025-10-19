from machine import Pin
from time import sleep

# GPIO2 biasanya terhubung ke LED bawaan di banyak board ESP32
led = Pin(2, Pin.OUT)

while True:
    led.value(1)   # Nyalakan LED
    sleep(1)       # Tunggu 1 detik
    led.value(0)   # Matikan LED
    sleep(1)       # Tunggu 1 detik
