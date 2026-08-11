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

Hjørne = {
    1: "SixSevenV1",
    2: "SixSevenV2",
    3: "SixSevenH1",
    4: "SixSevenH2",
}

sequences = {
    0: [1, 4, 2, 3],  # Bein1
    3: [2, 3, 1, 4],  # Bein4
}

sixseven_sequence = [
    (legs[7].SixSevenV1, legs[0].SixSevenH1),
    (legs[7].SixSevenV2, legs[0].SixSevenH2),
]

HJØRNE_BEIN = {0, 3}   # Bein 1, 4, 5, 8
MOVE_TIME = 1.5
PHASE_DELAY = 1.6   # litt mer enn move_time


try:
    print("Start")
    for leg in legs[0], legs[4], legs[3], legs[7]:
        leg.start2()
    for leg in legs[1], legs[2]:
        leg.prepare_all(600, 500, 500, 5)
    for leg in legs[5], legs[6]:
        leg.prepare_all(400, 500, 500, 5)

    start_all(broadcast)
    time.sleep(5.2)

    start_all(broadcast)
    time.sleep(5.2)

    print("SixSeven")

    while True:
        for leg0_move, leg3_move in sixseven_sequence:
            leg0_move()
            leg3_move()
            start_all(broadcast)
            time.sleep(0.2)


except KeyboardInterrupt:
    print("Avbrutt manuelt.")
    broadcast.move_stop()
except Exception as e:
    print(f"En feil oppstod: {e}")
    broadcast.move_stop()