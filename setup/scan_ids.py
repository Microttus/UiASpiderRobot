from hiwonderbuslinker.lewansoul_servo_bus import ServoBusCommunication
import time

CENTER = 500
MOVE_TIME_S = 1

bus = ServoBusCommunication("/dev/ttyACM0")

for servo_id in range(10, 25):
    try:
        servo = bus.get_servo(servo_id)

        try:
            servo.mode_write("servo")
            time.sleep(0.05)
            # Les ny posisjon
        except Exception:
            pass

        #servo.move_time_write(CENTER, MOVE_TIME_S)
        #print(f"ID {servo_id}: sendt til {CENTER}")
        #time.sleep(0.05)

        # Les ny posisjon                                                                                                                                                                       
        new_pos = servo.pos_read()
        print(f"  Posisjon = {servo_id}: {new_pos}")

    except Exception as e:
        print(f"ID {servo_id}: ingen respons ({e})")