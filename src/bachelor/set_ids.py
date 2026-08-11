from hiwonderbuslinker.lewansoul_servo_bus import ServoBusCommunication
import time

PORT = "/dev/ttyACM0"
OLD_ID = 24         # endre hvis servoen har annen nåværende ID
NEW_ID = 1        # sett ønsket ny ID her

TEST_POS_1 = 300    # 0-1000
TEST_POS_2 = 700
TEST_TIME = 0.8     # sekunder


def main():
    bus = ServoBusCommunication(PORT)

    print(f"Koblet til {PORT}")
    print(f"Setter servo-ID fra {OLD_ID} til {NEW_ID}...")

    # Sett ny ID
    bus.id_write(OLD_ID, NEW_ID)
    time.sleep(0.2)

    # Les tilbake ny ID
    try:
        returned_id = bus.id_read(NEW_ID)
        print(f"id_read({NEW_ID}) -> {returned_id}")
    except Exception as e:
        print(f"Kunne ikke lese tilbake ny ID: {e}")
        print("Prøver likevel bevegelsestest...")

    # Hent servo med ny ID og test bevegelse
    servo = bus.get_servo(NEW_ID)

    print("Tester bevegelse...")
    servo.move_time_write(TEST_POS_1, TEST_TIME)
    time.sleep(TEST_TIME + 0.5)

    servo.move_time_write(TEST_POS_2, TEST_TIME)
    time.sleep(TEST_TIME + 0.5)

    servo.move_time_write(500, TEST_TIME)
    time.sleep(TEST_TIME + 0.5)

    print(f"Ferdig. Servo skal nå ha ID {NEW_ID}.")


if __name__ == "__main__":
    main()