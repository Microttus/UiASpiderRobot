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
    1: "HPos1",
    2: "HPos2",
    3: "HPos3",
    4: "HPos4",
}

Kjerne = {
    1: "HPos1",
    2: "HPos2",
    3: "Pos3",
    4: "Pos4",
}

sekvens = {
    0: [1, 4, 2, 3],  # Bein1
    1: [4, 2, 3, 1],  # Bein2
    2: [3, 1, 4, 2],  # Bein3
    3: [2, 3, 1, 4],  # Bein4
    4: [1, 3, 2, 4],  # Bein5
    5: [3, 2, 4, 1],  # Bein6
    6: [4, 1, 3, 2],  # Bein7
    7: [2, 4, 1, 3],  # Bein8
}

HJØRNE_BEIN = {0, 3, 4, 7}   # Bein 1, 4, 5, 8
MOVE_TIME = 0.5
PHASE_DELAY = 0.6   # litt mer enn move_time


def apply_phase(phase_index):
    for i, leg in enumerate(legs):
        pose_number = sekvens[i][phase_index]

        if i in HJØRNE_BEIN:
            method_name = Hjørne[pose_number]
        else:
            method_name = Kjerne[pose_number]

        getattr(leg, method_name)()

    start_all(broadcast)


try:
    print("Start")
    for leg in legs[0], legs[3], legs[4], legs[7]:
        leg.start2()
    for leg in legs[1], legs[6]:
        leg.Pos4()
    for leg in legs[2], legs[5]:
        leg.Pos3()

    start_all(broadcast)
    time.sleep(10.2)

    print("Altererende tetrapod-gange")

    while True:
        for phase in range(4):
            print(f"Fase {phase + 1}")
            apply_phase(phase)
            time.sleep(PHASE_DELAY)

except KeyboardInterrupt:
    print("Avbrutt manuelt.")
    broadcast.move_stop()
except Exception as e:
    print(f"En feil oppstod: {e}")
    broadcast.move_stop()