from hiwonderbuslinker.lewansoul_servo_bus import ServoBusCommunication
import time

bus = ServoBusCommunication("/dev/ttyACM0")
servo = bus.get_servo(1)

while True:
    servo.move_time_write(1000, 0.5)
    time.sleep(0.6)

    servo.move_time_write(0, 0.5)
    time.sleep(0.6)