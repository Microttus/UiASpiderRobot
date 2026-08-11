import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("walkinglog.csv")

# Plot coxa for alle bein
coxa = df[df["joint"] == "coxa"]

plt.figure()
for leg in sorted(coxa["leg"].unique()):
    data = coxa[coxa["leg"] == leg]
    plt.plot(data["time_s"], data["actual_tick"], label=f"Bein {leg}")

plt.xlabel("Tid [s]")
plt.ylabel("Coxa-posisjon [ticks]")
plt.title("Coxa-posisjon under gange")
plt.legend()
plt.grid()
plt.show()

# Plot posisjonsfeil for coxa
plt.figure()
for leg in sorted(coxa["leg"].unique()):
    data = coxa[coxa["leg"] == leg]
    plt.plot(data["time_s"], data["error_tick"], label=f"Bein {leg}")

plt.xlabel("Tid [s]")
plt.ylabel("Feil [ticks]")
plt.title("Coxa posisjonsfeil under gange")
plt.legend()
plt.grid()
plt.show()