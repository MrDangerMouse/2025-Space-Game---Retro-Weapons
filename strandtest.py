import time
import space_api
from rpi_ws281x import *
import argparse
import RPi.GPIO as GPIO
from time import sleep

switch_pin = 20
fire_pin = 17
led_pin = 16

GPIO.setmode(GPIO.BCM)
GPIO.setup(switch_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(fire_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

ip = "172.20.10.2"
port = 9876
role = "weapons"
team = "retro"
weapon_id = 1

space_api.connect(role, team, ip, port)

# LED strip configuration:
LED_COUNT      = 38      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 65     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

# ---------- LED EFFECTS ---------- #

def colorWipe(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms/1000.0)

def small_win_effect(strip):
    print("YOU WIN")
    colorWipe(strip, Color(0,255,0), 10)
    colorWipe(strip, Color(0,0,0), 10)

def large_win_effect(strip, flashes=10, delay=0.12):
    print("SPECIAL EFFECT ACTIVATED")        
    num = strip.numPixels()
    
    for _ in range(flashes):
        for i in range(num):
            if i % 2 == 0:
                strip.setPixelColor(i, Color(0, 255, 0))
            else:
                strip.setPixelColor(i, Color(0, 0, 0))
        strip.show()
        time.sleep(delay)
        
        for i in range(num):
            if i % 2 == 1:
                strip.setPixelColor(i, Color(0, 255, 0))
            else:
                strip.setPixelColor(i, Color(0, 0, 0))
        strip.show()
        time.sleep(delay)

# ---------- LED LOOP ---------- #
win_count = 0
win_led = 37
last_trigger = time.time()
interval = 6

def run_loop(strip):
    global win_count
            
    for i in range(0, LED_COUNT):
        strip.setPixelColor(i, Color(255,0,0))
        strip.show()
        time.sleep(30/1000.0)
        
        if GPIO.input(fire_pin) == GPIO.LOW:
            print("SHOOT")
            space_api.shoot("laser")
        
        if GPIO.input(switch_pin) == GPIO.LOW:
            if i == win_led:
                win_count += 1
                if win_count != 3:
                    small_win_effect(strip)
            return i
        
                
    for i in range(LED_COUNT - 1, -1, -1):
        strip.setPixelColor(i, Color(0,0,0))
        strip.show()  
        time.sleep(30/1000.0)
        
        if GPIO.input(fire_pin) == GPIO.LOW:
            print("SHOOT")
            space_api.shoot("laser")
        
        if GPIO.input(switch_pin) == GPIO.LOW:
            if i == win_led:
                win_count += 1
                if win_count != 3:
                    small_win_effect(strip)
            return i
    
    return 0

# ---------- MAIN ---------- #

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
    args = parser.parse_args()
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    strip.begin()

    print ('Running -> Press Ctrl-C to quit.')
    if not args.clear:
        print('Use "-c" argument to clear LEDs on exit')

    try:
        while True:
            colorWipe(strip, Color(0,0,0), 10)
            result_led = run_loop(strip)
            print(f"LED: {result_led}")
            
            if win_count >= 3:
                large_win_effect(strip)
                win_count = 0


    except KeyboardInterrupt:
        if args.clear:
            colorWipe(strip, Color(0,0,0), 10)
