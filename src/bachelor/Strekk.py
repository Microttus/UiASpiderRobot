from hiwonderbuslinker.lewansoul_servo_bus import ServoBusCommunication
from leg import Leg
import time

PORT = "/dev/ttyACM0"
BROADCAST_ID = 254
bus = ServoBusCommunication(PORT, timeout=0.05, discard_echo=False)
broadcast = bus.get_servo(BROADCAST_ID)


def start_all(broadcast):
    broadcast.move_start()

legs = [
    Leg(bus, 1, 2, 3),
    Leg(bus, 4, 5, 6),
    Leg(bus, 7, 8, 9),
    Leg(bus, 10, 11, 12),
    Leg(bus, 13, 14, 15),
    Leg(bus, 16, 17, 18),
    Leg(bus, 19, 20, 21),
    Leg(bus, 22, 23, 24),
]

try:
    print("Sitt")
    for leg in legs:
        leg.sitt()

    start_all(broadcast)
    time.sleep(10.2)

    print("Reis deg")
    for leg in legs:
        leg.High()

    start_all(broadcast)
    time.sleep(10.2)

    print("Sitt")
    for leg in legs:
        leg.sitt()
    
    start_all(broadcast)
    time.sleep(5.2)

    broadcast.move_stop()

except KeyboardInterrupt:
    print("Avbrutt manuelt.")
    broadcast.move_stop()
except Exception as e:
    print(f"En feil oppstod: {e}")
    broadcast.move_stop()