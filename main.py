import time
import sys
import yaml
import RPi.GPIO as GPIO

# Docs describe 275 or 375 microseconds, but we found found that 375 didn't work....
# Possibly due to python timing shortcomings
short_delay = 300 * 10**-6
long_delay = 3 * short_delay
extended_delay = 10 * long_delay


class KakuRF:
    """
    Klik aan klik uit RF class for setting up pins, creating messages and sending them.
    """

    def create_kaku_message(self, unit, state):
        """
        Creates a bit string (string not bit array) message.
        Primary source: https://www.circuitsonline.net/forum/view/message/1181410

        :param unit: Single unit number, see init
        :param state: See init
        
        :returns: String that can be used by transmit_code_new.
        """
        return "B{name:026b}{group}{state}{unit:04b}E".format(
            name=self.name, group=self.group, state=state, unit=unit
        )

    def gpio_setup(self):
        """
        Sets up GPIO for sending messages.
        """
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.transmit_pin, GPIO.OUT)

    def gpio_cleanup(self):
        """
        Cleanup GPIO settings
        """
        GPIO.cleanup() 

    def transmit_code_new(self, code):
        '''Transmits a chosen klik-aan-klik uit bitstring using the GPIO transmitter
        
        :param code: Bitstring in string format (i.e., not byte array). 
            Also added support for B and E symbols which are meant for the Begin and End pulses.
        '''
        print(code)
        for t in range(self.num_attempts):
            for i in code:
                if i == 'B':
                    GPIO.output(self.transmit_pin, 1)
                    time.sleep(short_delay)
                    GPIO.output(self.transmit_pin, 0)
                    time.sleep(9 * short_delay)
                if i == 'E':
                    GPIO.output(self.transmit_pin, 1)
                    time.sleep(short_delay)
                    GPIO.output(self.transmit_pin, 0)
                if i == '0':
                    GPIO.output(self.transmit_pin, 1)
                    time.sleep(short_delay)
                    GPIO.output(self.transmit_pin, 0)
                    time.sleep(short_delay)
                    GPIO.output(self.transmit_pin, 1)
                    time.sleep(short_delay)
                    GPIO.output(self.transmit_pin, 0)
                    time.sleep(long_delay)
                elif i == '1':
                    GPIO.output(self.transmit_pin, 1)
                    time.sleep(short_delay)
                    GPIO.output(self.transmit_pin, 0)
                    time.sleep(long_delay)
                    GPIO.output(self.transmit_pin, 1)
                    time.sleep(short_delay)
                    GPIO.output(self.transmit_pin, 0)
                    time.sleep(short_delay)
                else:
                    continue
            GPIO.output(self.transmit_pin, 0)
            time.sleep(2 * extended_delay)

    def main(self, state):
        """
        Main function for class
        :param state: 1 for on, 0 for off.
        """
        for unit in self.unit:
            code = self.create_kaku_message(self.unit[unit], state)
            self.transmit_code_new(code)

    def __init__(self, name, group, unit, transmit_pin=18, num_attempts=20):
        """
        :param name: the code associated with the remote. You'll have to extract this from the signal, unless you have a configurable one. We used: https://www.instructables.com/Super-Simple-Raspberry-Pi-433MHz-Home-Automation/
        :param group: group id, can have multiple devices. We don't use this.
        :param state: 1 for on, 0 for off.
        :param unit: corresponds with the seperate buttons on the remote, this can be used to add multiple receivers
            Also note that it's possible to assign multiple unit codes to the same receiver
            Can be both a list or singular here
        """
        self.name = name
        self.group = group
        if not isinstance(unit, list):
            self.unit = [unit]
        else:
            self.unit = unit

        self.transmit_pin = transmit_pin
        self.num_attempts = num_attempts
        self.gpio_setup()


if __name__ == '__main__':
    with open("./config.yaml", "r") as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    state = 1
    if (len(sys.argv) > 1):
        state = sys.argv[1]

    try:
        obj = KakuRF(config["name"], config["group"], config["unit"], config["transmit_pin"], config["num_attempts"])
        obj.main(state)
    except:
        raise
    finally:
        obj.gpio_cleanup()
  