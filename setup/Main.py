from numpy import broadcast

from hiwonderbuslinker.lewansoul_servo_bus import ServoBusCommunication
from leg import Leg
import time

PORT = "/dev/ttyACM0"
BROADCAST_ID = 254

Min = 100
Nøytral = 500
Max = 700

def start_all(broadcast):
    broadcast.move_start()


def main():
    bus = ServoBusCommunication(PORT, timeout=0.05, discard_echo=False)
    broadcast = bus.get_servo(BROADCAST_ID)

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
        print("Start")
        for leg in legs:
            leg.start1()
        start_all(broadcast)
        time.sleep(5.2)
        for leg in legs:
            leg.start2()
        start_all(broadcast)
        time.sleep(5)

        print("Altererende tetrapod-gange")

        print("Sitt")
        for leg in legs:
            leg.sitt()
               
        start_all(broadcast)
        time.sleep(10.2)

        broadcast.move_stop()
        print("God Natt")

        pos1 = legs[0].read_coxa(), legs[0].read_femur(), legs[0].read_tibia()
        pos2 = legs[1].read_coxa(), legs[1].read_femur(), legs[1].read_tibia()
        pos3 = legs[2].read_coxa(), legs[2].read_femur(), legs[2].read_tibia()
        pos4 = legs[3].read_coxa(), legs[3].read_femur(), legs[3].read_tibia()
        pos5 = legs[4].read_coxa(), legs[4].read_femur(), legs[4].read_tibia()
        pos6 = legs[5].read_coxa(), legs[5].read_femur(), legs[5].read_tibia()          
        Pos7 = legs[6].read_coxa(), legs[6].read_femur(), legs[6].read_tibia()
        print(f"Posisjon: 1{pos1}, 2{pos2}, 3{pos3}, 4{pos4}, 5{pos5}, 6{pos6}, 7{Pos7}")

    except KeyboardInterrupt:
        print("Avbrutt manuelt.")
        broadcast.move_stop()
    except Exception as e:
        print(f"En feil oppstod: {e}")
        broadcast.move_stop()


if __name__ == "__main__":
    main()