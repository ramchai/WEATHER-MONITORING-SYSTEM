import time
import board
import adafruit_dht
import RPi.GPIO as GPIO
import Adafruit_BMP.BMP085 as BMP085
from RPLCD.i2c import CharLCD

# ======================================
# DHT22 (GPIO18 - Physical Pin 12)
# ======================================
dht = adafruit_dht.DHT22(board.D18, use_pulseio=False)

# ======================================
# BMP180
# ======================================
bmp = BMP085.BMP085()

# ======================================
# Rain Sensor (GPIO17 - Physical Pin 11)
# ======================================
RAIN_PIN = 17

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(RAIN_PIN, GPIO.IN)

# ======================================
# LCD (I2C 0x27)
# ======================================
lcd = CharLCD(
    i2c_expander='PCF8574',
    address=0x27,
    port=1,
    cols=16,
    rows=2,
    charmap='A00'
)

lcd.clear()

print("Weather Station Started...")
print("--------------------------")

try:

    while True:

        # ==========================
        # DHT22
        # ==========================
        try:
            dht_temp = dht.temperature
            humidity = dht.humidity
        except RuntimeError as e:
            print("DHT22 Error:", e)
            dht_temp = None
            humidity = None

        # ==========================
        # BMP180
        # ==========================
        bmp_temp = bmp.read_temperature()
        pressure = bmp.read_pressure() / 100.0   # hPa
        altitude = bmp.read_altitude()

        # ==========================
        # Rain Sensor
        # ==========================
        rain = GPIO.input(RAIN_PIN)

        if rain == 0:
            rain_status = "RAIN"
        else:
            rain_status = "NO RAIN"

        # ==========================
        # Terminal Output
        # ==========================
        print("\n==============================")

        if dht_temp is not None:
            print("DHT Temp : {:.1f} C".format(dht_temp))
            print("Humidity : {:.1f} %".format(humidity))
        else:
            print("DHT22 : Read Failed")

        print("BMP Temp : {:.1f} C".format(bmp_temp))
        print("Pressure : {:.2f} hPa".format(pressure))
        print("Altitude : {:.2f} m".format(altitude))
        print("Rain     :", rain_status)

        # ==========================
        # LCD PAGE 1
        # ==========================
        lcd.clear()

        if dht_temp is not None:
            lcd.write_string("T:{:.1f}C".format(dht_temp))
            lcd.cursor_pos = (1, 0)
            lcd.write_string("H:{:.1f}%".format(humidity))
        else:
            lcd.write_string("DHT22 ERROR")

        time.sleep(3)

        # ==========================
        # LCD PAGE 2
        # ==========================
        lcd.clear()
        lcd.write_string("P:{:.0f}hPa".format(pressure))
        lcd.cursor_pos = (1, 0)
        lcd.write_string("Alt:{:.1f}m".format(altitude))

        time.sleep(3)

        # ==========================
        # LCD PAGE 3
        # ==========================
        lcd.clear()
        lcd.write_string("BMP:{:.1f}C".format(bmp_temp))
        lcd.cursor_pos = (1, 0)
        lcd.write_string(rain_status)

        time.sleep(3)

except KeyboardInterrupt:

    print("\nProgram Stopped")

finally:

    lcd.clear()
    GPIO.cleanup()

    try:
        dht.exit()
    except:
        pass