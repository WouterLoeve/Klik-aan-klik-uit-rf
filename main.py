import time
import sys
import yaml
import RPi.GPIO as GPIO

# Docs describe 275 or 375 microseconds, but we found found that 375 didn't work....
# Possibly due to python timing shortcomings
short_delay = 300 * 10**-6
long_delay = 3 * short_delay
extended_delay = 10 * long_delay

NUM_ATTEMPTS = 20
TRANSMIT_PIN = 18

def gpio_setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(TRANSMIT_PIN, GPIO.OUT)

def transmit_code_new(code):
    '''Transmits a chosen klik-aan-klik uit bitstring using the GPIO transmitter
    
    :param code: Bitstring in string format (i.e., not byte array). 
        Also added support for B and E symbols which are meant for the Begin and End pulses.
    '''
    gpio_setup()
    print(code)

    for t in range(NUM_ATTEMPTS):
        for i in code:
            if i == 'B':
                GPIO.output(TRANSMIT_PIN, 1)
                time.sleep(short_delay)
                GPIO.output(TRANSMIT_PIN, 0)
                time.sleep(9 * short_delay)
            if i == 'E':
                GPIO.output(TRANSMIT_PIN, 1)
                time.sleep(short_delay)
                GPIO.output(TRANSMIT_PIN, 0)
            if i == '0':
                GPIO.output(TRANSMIT_PIN, 1)
                time.sleep(short_delay)
                GPIO.output(TRANSMIT_PIN, 0)
                time.sleep(short_delay)
                GPIO.output(TRANSMIT_PIN, 1)
                time.sleep(short_delay)
                GPIO.output(TRANSMIT_PIN, 0)
                time.sleep(long_delay)
            elif i == '1':
                GPIO.output(TRANSMIT_PIN, 1)
                time.sleep(short_delay)
                GPIO.output(TRANSMIT_PIN, 0)
                time.sleep(long_delay)
                GPIO.output(TRANSMIT_PIN, 1)
                time.sleep(short_delay)
                GPIO.output(TRANSMIT_PIN, 0)
                time.sleep(short_delay)
            else:
                continue
        GPIO.output(TRANSMIT_PIN, 0)
        time.sleep(2* extended_delay)
    GPIO.cleanup() 

if __name__ == '__main__':
    with open("./config.yaml", "r") as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    if "transmit_pin" in config:
        TRANSMIT_PIN = config["transmit_pin"]

    if "num_attempts" in config:
        NUM_ATTEMPTS = config["num_attempts"]

    state = 1
    if (len(sys.argv) > 1):
        state = sys.argv[1]

    # Main source: https://www.circuitsonline.net/forum/view/message/1181410
    # name is the code associated with the remote. You'll have to extract this from the signal, unless you have a configurable one.
    # We used: https://www.instructables.com/Super-Simple-Raspberry-Pi-433MHz-Home-Automation/
    # group is the group id, can have multiple devices. We don't use this.
    # unit corresponds with the seperate buttons on the remote, this can be used to add multiple receivers
    # Also note that it's possible to assign multiple unit codes to the same receiver
    argument = "B{name:026b}{group}{state}{unit:04b}E".format(name=config.name, group=config.group, state=state, unit=config.unit)
    transmit_code_new(str(argument))