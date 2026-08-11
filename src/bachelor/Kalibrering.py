from hiwonderbuslinker.lewansoul_servo_bus import ServoBusCommunication
import time

bus = ServoBusCommunication("/dev/ttyACM0")
servo = bus.get_servo(16)

servo.mode_write("servo")
time.sleep(0.2)

for target in [200, 300, 400, 500, 600, 700, 800]:
    print(f"\nSetter til {target}")
    servo.move_time_write(target, 1.0)
    time.sleep(1.2)

    try:
        pos = servo.pos_read()
        print("pos_read:", pos)
    except Exception as e:
        print("pos_read feil:", e)