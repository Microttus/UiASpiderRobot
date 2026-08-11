import time
from hiwonderbuslinker.lewansoul_servo_bus import ServoBusCommunication


class ServoGroup1to3:
    def __init__(self):
        # Initialize servo controller
        self.servo = ServoBusCommunication()

    def move_servo_1_one_rotation(self):
        """
        Moves servo with ID 1 one full rotation.
        """
        servo_id = 1

        # Typical servo range is 0–1000 (Hiwonder style)
        # We'll simulate one rotation by going min → max → min

        print("Moving servo 1...")

        # Move to one extreme
        self.servo.set_position(servo_id, 0, 1000)
        time.sleep(2)

        # Move to the other extreme
        self.servo.set_position(servo_id, 1000, 1000)
        time.sleep(2)

        # Return to center (optional)
        self.servo.set_position(servo_id, 500, 1000)
        time.sleep(2)

        print("Done.")