import pandas as pd
import matplotlib.pyplot as plt

CSV_FILE = "walking_log.csv"


def plot_joint_position(df, joint_name):
    joint_data = df[df["joint"] == joint_name]

    plt.figure()
    for leg in sorted(joint_data["leg"].unique()):
        data = joint_data[joint_data["leg"] == leg]
        plt.plot(data["time_s"], data["actual_tick"], label=f"Bein {leg}")

    plt.xlabel("Tid [s]")
    plt.ylabel(f"{joint_name} posisjon [ticks]")
    plt.title(f"{joint_name} posisjon under gange")
    plt.legend()
    plt.grid()
    plt.show()


def plot_joint_target_vs_actual(df, leg_number, joint_name):
    data = df[(df["leg"] == leg_number) & (df["joint"] == joint_name)]

    plt.figure()
    plt.plot(data["time_s"], data["target_tick"], label="Target")
    plt.plot(data["time_s"], data["actual_tick"], label="Faktisk")

    plt.xlabel("Tid [s]")
    plt.ylabel("Posisjon [ticks]")
    plt.title(f"Bein {leg_number} {joint_name}: target vs faktisk")
    plt.legend()
    plt.grid()
    plt.show()


def plot_joint_error(df, joint_name):
    joint_data = df[df["joint"] == joint_name]

    plt.figure()
    for leg in sorted(joint_data["leg"].unique()):
        data = joint_data[joint_data["leg"] == leg]
        plt.plot(data["time_s"], data["error_tick"], label=f"Bein {leg}")

    plt.xlabel("Tid [s]")
    plt.ylabel("Feil [ticks]")
    plt.title(f"{joint_name} posisjonsfeil")
    plt.legend()
    plt.grid()
    plt.show()


def plot_joint_velocity(df, joint_name):
    if "velocity_tick_s" not in df.columns:
        print("CSV-filen har ikke velocity_tick_s. Hopper over hastighetsplot.")
        return

    joint_data = df[df["joint"] == joint_name]

    plt.figure()
    for leg in sorted(joint_data["leg"].unique()):
        data = joint_data[joint_data["leg"] == leg]
        plt.plot(data["time_s"], data["velocity_tick_s"], label=f"Bein {leg}")

    plt.xlabel("Tid [s]")
    plt.ylabel("Hastighet [ticks/s]")
    plt.title(f"{joint_name} hastighet")
    plt.legend()
    plt.grid()
    plt.show()


def main():
    df = pd.read_csv(CSV_FILE)

    required_columns = {
        "time_s",
        "leg",
        "joint",
        "target_tick",
        "actual_tick",
        "angle_deg",
        "error_tick",
    }

    missing = required_columns - set(df.columns)
    if missing:
        print(f"Mangler kolonner i CSV: {missing}")
        return

    plot_joint_position(df, "coxa")
    plot_joint_position(df, "femur")
    plot_joint_position(df, "tibia")

    plot_joint_error(df, "coxa")
    plot_joint_error(df, "femur")
    plot_joint_error(df, "tibia")

    plot_joint_target_vs_actual(df, leg_number=1, joint_name="coxa")
    plot_joint_target_vs_actual(df, leg_number=5, joint_name="coxa")

    plot_joint_velocity(df, "coxa")


if __name__ == "__main__":
    main()