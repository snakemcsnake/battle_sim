import random
import pandas as pd
import math
import os

def effective_weapon_damage(WeaponDamage, STR, DEX, LVL):
    if STR >= DEX:
        effective_weapon_damage = WeaponDamage + effective_stat_value(STR) + LVL
    else :
        effective_weapon_damage = WeaponDamage + effective_stat_value(DEX) + LVL
    return effective_weapon_damage

def effective_stat_value(raw_value):
    scale = 10 * math.log10(raw_value + 1) + 1
    return math.floor(max(scale,15))

def calculate_DR(attacker_level, defender_armor, defender_level):
    #effective_armor = defender_armor + effective_stat_value(defender_dex)  # Apply diminishing returns to DEX
    reduction = min((defender_armor*1.25 + defender_level + 15) / (3*attacker_level + defender_armor + 100), 0.75)
    return reduction


def simulate_combat(player_stats, enemy_stats, simulations=20):
    player_wins = 0
    rounds_list = []

    for _ in range(simulations):
        player_hp = player_stats['HP']
        enemy_hp = enemy_stats['HP']
        player_lvl = player_stats['Level']
        rounds = 0

        while player_hp > 0 and enemy_hp > 0:
            rounds += 1
            print(f"Round {rounds}: Player HP = {player_hp}, Player lvl = {player_lvl}, Enemy HP = {enemy_hp}, enemy strength = {enemy_stats['STR']}")
            if random.random() < player_stats['HitChance']:
                #enemy_damage_reduction = calculate_DR(enemy_stats['Level'], player_stats['DEF'], player_stats['Level'])
                player_damage = effective_weapon_damage(player_stats['WeaponDamage'], player_stats['STR'], player_stats['DEX'], player_stats['Level'])
                net_damage = player_damage
                enemy_hp -= net_damage
                print(f'Player dam = {net_damage}')
            # Enemy's turn
            if enemy_hp > 0:
                if random.random() < enemy_stats['HitChance']:
                    player_damage_reduction = calculate_DR(enemy_stats['Level'], player_stats['DEF'], player_stats['Level'])
                    enemy_damage = effective_weapon_damage(enemy_stats['WeaponDamage'], enemy_stats['STR'], enemy_stats['DEX'], enemy_stats['Level'])
                    net_damage = enemy_damage - (enemy_damage * player_damage_reduction)
                    net_damage = math.ceil(max(net_damage, 0)) #check for negative damage
                    player_hp -= net_damage
                    print(f'enemy dam = {net_damage} player reduct {player_damage_reduction}')
        if player_hp > 0:
            player_wins += 1
            rounds_list.append(rounds)
            print('WIN')
        else:
            print('LOSE')
        

    avg_rounds = sum(rounds_list) / len(rounds_list) if rounds_list else 0
    win_rate = player_wins / simulations
    return win_rate, avg_rounds

def calculate_damage(weapon_damage, strength, damage_scaling_factor=0.5):
    """
    Calculate damage based on weapon damage and strength.
    :param weapon_damage: Base weapon damage.
    :param strength: Strength stat value.
    :param damage_scaling_factor: Factor to scale strength to damage.
    :return: Total damage.
    """
    return weapon_damage + (strength * damage_scaling_factor)

def calculate_hp(base_hp, strength, hp_scaling_factor=0.02):
    """
    Calculate HP based on base HP and strength.
    :param base_hp: Base HP value.
    :param strength: Strength stat value.
    :param hp_scaling_factor: Factor to scale strength to HP.
    :return: Total HP.
    """
    return base_hp + (strength * hp_scaling_factor)

def calculate_hit_chance(base_hit_chance, dexterity, dex_scaling_factor=0.01):
    """
    Calculate hit chance based on dexterity.
    :param base_hit_chance: Base hit chance.
    :param dexterity: Dexterity stat value.
    :param dex_scaling_factor: Factor to scale dexterity to hit chance.
    :return: Total hit chance.
    """
    return min(base_hit_chance + (dexterity * dex_scaling_factor), 1.0)  # Cap hit chance at 100%

def calculate_dynamic_adjustment(current_win_rate, current_avg_rounds, target_win_rate, target_avg_rounds, base_adjustment=1, max_adjustment=5):
    """
    Calculate the dynamic adjustment magnitude based on the deviation from target metrics.

    :param current_win_rate: Current win rate observed.
    :param current_avg_rounds: Current average rounds observed.
    :param target_win_rate: Target win rate to achieve.
    :param target_avg_rounds: Target average rounds to achieve.
    :param base_adjustment: Base adjustment value.
    :param max_adjustment: Maximum possible adjustment value.
    :return: Calculated adjustment magnitude.
    """

    # Calculate the deviation from the target metrics
    win_rate_deviation = abs(current_win_rate - target_win_rate)
    avg_rounds_deviation = abs(current_avg_rounds - target_avg_rounds)

    # Calculate the adjustment factor based on the deviations
    adjustment_factor = (win_rate_deviation + avg_rounds_deviation) / 2

    # Calculate the final adjustment value
    # The more the deviation, the higher the adjustment, bounded by the max_adjustment
    adjustment = min(base_adjustment + adjustment_factor * base_adjustment, max_adjustment)

    return adjustment

def adjust_stat(enemy_stats, stat_to_adjust, adjustment, win_rate, avg_rounds, target_win_rate, target_avg_rounds,current_win_rate, current_avg_rounds, base_hp, base_weapon_damage, base_hit_chance, STR_CAP=62, DEX_CAP=62, win_rate_weight=0.5, avg_rounds_weight=0.5):
    """
    Adjust the specified stat of the enemy and manage the adjustment order. Also recalculate HP, damage, and hit chance based on STR and DEX.

    :param enemy_stats: Dictionary containing the enemy's stats.
    :param stat_to_adjust: The stat to be adjusted.
    :param adjustment: The amount by which to adjust the stat.
    :param win_rate: Current win rate observed.
    :param avg_rounds: Current average rounds observed.
    :param target_win_rate: Target win rate to achieve.
    :param target_avg_rounds: Target average rounds to achieve.
    :param STR_CAP: Cap for the Strength stat.
    :param DEX_CAP: Cap for the Dexterity stat.
    :param win_rate_weight: Weight for adjusting based on win rate deviation.
    :param avg_rounds_weight: Weight for adjusting based on average rounds deviation.
    :return: Updated enemy stats and a flag indicating if further adjustment is needed.
    """
    win_rate_deviation = abs(current_win_rate - target_win_rate)
    avg_rounds_deviation = abs(current_avg_rounds - target_avg_rounds)
    adjust_needed = True
    # Adjust the stat based on the weighted deviations
    if win_rate_deviation > avg_rounds_deviation:
        # Adjust more based on win rate
        if win_rate > target_win_rate:
            enemy_stats[stat_to_adjust] = max(1, enemy_stats[stat_to_adjust] - adjustment)
        else:
            enemy_stats[stat_to_adjust] = min(enemy_stats[stat_to_adjust] + adjustment, STR_CAP if stat_to_adjust == 'STR' else DEX_CAP if stat_to_adjust == 'DEX' else float('inf'))
    else:
        # Adjust more based on average rounds
        if avg_rounds > target_avg_rounds:
            enemy_stats[stat_to_adjust] = max(1, enemy_stats[stat_to_adjust] - adjustment)
        else:
            enemy_stats[stat_to_adjust] = min(enemy_stats[stat_to_adjust] + adjustment, STR_CAP if stat_to_adjust == 'STR' else DEX_CAP if stat_to_adjust == 'DEX' else float('inf'))

    # Recalculate HP, Damage, and Hit Chance based on STR and DEX
    if stat_to_adjust in ['STR', 'DEX']:
        enemy_stats['HP'] = calculate_hp(base_hp, enemy_stats['STR'])
        enemy_stats['WeaponDamage'] = calculate_damage(base_weapon_damage, enemy_stats['STR'])
        enemy_stats['HitChance'] = calculate_hit_chance(base_hit_chance, enemy_stats['DEX'])

    # Check if cap is reached for STR or DEX
    if (stat_to_adjust == 'STR' and enemy_stats['STR'] >= STR_CAP) or (stat_to_adjust == 'DEX' and enemy_stats['DEX'] >= DEX_CAP):
        adjust_needed = False

    return enemy_stats, adjust_needed




# Load the Excel file
file_path = 'C:/Users/snake/python_code/.conda/dylan_game/Prado RPG Character Stats.xlsx'
sheet_name = 'Stat Lvls'
player_stats_df = pd.read_excel(file_path, sheet_name=sheet_name)

# Prepare DataFrame to store player and enemy stats
combined_stats_df = pd.DataFrame()

target_win_rate = 0.8
target_avg_rounds = 10
rounds_tolerance = 1
adjustment = 0.25
num_enemies_per_player = 1

for index, row in player_stats_df.iterrows():
    player_stats = {
        'Type': 'Player',
        'Level': row['Level'],
        'HP': row['HP'] + effective_stat_value(row['Strength']),
        'STR': row['Strength'],
        'DEX': row['Dexterity'],
        'ATK': row['ATK'],
        'DEF': row['DEF'],
        'WeaponDamage': row['Wpn. Atk'],
        'TotalStat': row['Total Stat'],
        'HitChance': 0.8,
        'Avg_Rounds': None
    }

    # Add player stats to the DataFrame
    combined_stats_df = combined_stats_df._append(player_stats, ignore_index=True)

    for enemy_num in range(num_enemies_per_player):

        # Random initial enemy stats
        enemy_str = player_stats['STR']
        enemy_hp  = player_stats['HP']
        enemy_dex = player_stats['DEX']

        enemy_stats = {
            'Type': 'Enemy',
            'Level': row['Level'],
            'HP':  enemy_hp,
            'STR': enemy_str,
            'DEX': enemy_dex,
            'WeaponDamage': row['Wpn. Atk'],
            'HitChance': 0.8,
            'Avg_Rounds': None,
            'win_rate' : None
        }
        stat_adjustment_order = ['STR', 'DEX']  # Order of stats to adjust
        adjustment_index = 0  # To keep track of which stat to adjust
        STR_CAP = 62
        DEX_CAP = 62

        for enemy_num in range(num_enemies_per_player):
            # Reset the adjustment order for each enemy
            stat_adjustment_order = ['STR', 'DEX']
            adjustment_index = 0

            while len(stat_adjustment_order) > 0:
                win_rate, avg_rounds = simulate_combat(player_stats, enemy_stats)

                # Dynamic adjustment based on deviation from target
                adjustment = calculate_dynamic_adjustment(win_rate, avg_rounds, target_win_rate, target_avg_rounds)

                # Determine which stat to adjust
                stat_to_adjust = stat_adjustment_order[adjustment_index % len(stat_adjustment_order)]

                # Corrected function call with all required arguments
                enemy_stats, adjust_needed = adjust_stat(
                    enemy_stats, stat_to_adjust, adjustment, 
                    win_rate, avg_rounds, 
                    target_win_rate, target_avg_rounds, win_rate, avg_rounds,
                    enemy_stats['HP'], enemy_stats['WeaponDamage'], enemy_stats['HitChance']
                )

                # Remove the stat from adjustment order if no further adjustment is needed
                if not adjust_needed and stat_to_adjust in stat_adjustment_order:
                    stat_adjustment_order.remove(stat_to_adjust)

                adjustment_index += 1

                if abs(win_rate - target_win_rate) < 0.02 and abs(avg_rounds - target_avg_rounds) <= rounds_tolerance:
                    break


        enemy_stats['Avg_Rounds'] = avg_rounds
        enemy_stats['win_rate'] = win_rate
        combined_stats_df = combined_stats_df._append(enemy_stats, ignore_index=True)

# Save the combined stats to a new CSV file
output_directory = 'output dir path'
output_filename = 'combined_player_enemy_stats.csv'
output_path = os.path.join(output_directory, output_filename)

# Check if the directory exists, and create it if it doesn't
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# Save the DataFrame to CSV
combined_stats_df.to_csv(output_path, index=False)
print(f"Combined player and enemy stats saved to {output_path}")