import numpy as np
import matplotlib.pyplot as plt
import math

def effective_stat_value(raw_value):
    log_value = 10 * math.log10(raw_value + 1) + 1
    return math.floor(min(log_value, 15))

# Range of raw values
raw_values = np.linspace(0, 62, 400)

# Calculate effective stat values
effective_values = [effective_stat_value(x) for x in raw_values]

# Plotting
plt.figure(figsize=(10, 6))
plt.plot(raw_values, effective_values)
plt.title('Effective Stat Value Function')
plt.xlabel('Raw Value')
plt.ylabel('Effective Stat Value')
plt.grid(True)
plt.show()
