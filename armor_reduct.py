import matplotlib.pyplot as plt
import numpy as np
import matplotlib.cm as cm

# Define parameters
effective_armor_range = np.arange(0, 121)  # 0 to 120
attacker_level_range = np.arange(0, 61, 5)  # Plot every 5th level from 0 to 60
defender_level = 0  # Assumed constant defender level
colors = cm.viridis(np.linspace(0, 1, len(attacker_level_range)))  # Color map

# Initialize plot with increased figure size
plt.figure(figsize=(15, 10))

# Plot DR for each selected attacker level
for i, attacker_level in enumerate(attacker_level_range):
    dr_values = [min((effective_armor*1.25 + defender_level + 15) / (3*attacker_level + effective_armor + 100), 0.75)
                 for effective_armor in effective_armor_range]
    plt.plot(effective_armor_range, dr_values, label=f'Level {attacker_level}', color=colors[i])

# Configure plot
plt.xlabel('Effective Armor')
plt.ylabel('Damage Reduction (DR)')
plt.title('Damage Reduction vs Effective Armor for Various Attacker Levels')
plt.legend(title='Attacker Level', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(True)

# Increase y-axis resolution
plt.yticks(np.arange(0, 1.05, 0.05))  # Set y-ticks at intervals of 0.05

plt.show()
