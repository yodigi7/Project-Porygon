"""This module contains several functions that emulate the logic 
for a Pokémon battle. In particular, it requires a strict adherence 
to a predefined JSON format. The entries in that JSON are as follows:

At the moment, Project Porygon only supports 2-player single battles.
"""
import json
import pokebase as pb
import pokeutils as pk


"""Updates the Battle JSON file.

Parameters:
battle_JSON -- the filepath to a Pokémon battle
updated_JSON -- the updated python dictionary representing the json battle
"""
def update_battle(battle_JSON, updated_JSON):
    with open(battle_JSON, 'w') as f:
        f.write(json.dumps(updated_JSON))


"""Performs an attack using the stats of the passed Pokémon.

Parameters:
battle_JSON -- the filepath to a Pokémon battle
atk_index -- a number from 0 to 3 that indicates the selected move
poke_id -- a stringified UUID representing the attacking Pokémon
"""
def attack(battle_JSON, atk_index, poke_id):
    battle_dict = pk.load_data(battle_JSON)

    #  Find the attacking and defending pokémon
    #  Currently, this only supports 2 player single battles
    if battle_dict['players'][0]['active_pokemon']['poke_id'] == poke_id:
        atk_player = battle_dict['players'][0]
        def_player = battle_dict['players'][1]
        atk_in, def_in = 0, 1
    else:
        atk_player = battle_dict['players'][1]
        def_player = battle_dict['players'][0]
        atk_in, def_in = 1, 0

    atk_team_path = pk.team_path(
    atk_player['account_name'],atk_player['team_id'])

    atk_stat_mods = atk_player['active_pokemon']['stat_modifiers']
    atk_hp_pct = atk_player['active_pokemon']['hp_percent']
    def_team_path = pk.team_path(
    def_player['account_name'],def_player['team_id'])

    def_poke_id = def_player['active_pokemon']['poke_id']
    def_stat_mods = def_player['active_pokemon']['stat_modifiers']
    def_hp_pct = def_player['active_pokemon']['hp_percent']

    #  Load the attacking Pokémon and calculate stats
    atk_team = pk.load_data(atk_team_path)
    for pokemon in atk_team['pokemon']:
        if pokemon['poke_id'] == poke_id:
            atk_stats = pk.calcStats(pokemon)

            #  Load the attack data
            attack = pb.move(pokemon['moves'][atk_index])

            #  The attacker's level is used in damage calcs
            atk_level = pokemon['level']

    #  Load the defending Pokémon and calculate stats
    def_team = pk.load_data(def_team_path)
    for pokemon in def_team['pokemon']:
        if pokemon['poke_id'] == def_poke_id:
            def_stats = pk.calcStats(pokemon)

    #  Apply stat modifiers (HP doesn't have a modifier)
    for key, value in atk_stats.items():
        if key != 'hp':
            atk_stats[key] = value*atk_stat_mods[key]
    for key, value in def_stats.items():
        if key != 'hp':
            def_stats[key] = value*def_stat_mods[key]

    #  Calculate the raw damage dealt
    raw_damage = pk.calcDamage(atk_level, atk_stats, def_stats, attack)

    #  Convert from an HP percentage to an HP amount and back again
    def_hp = int((def_hp_pct/100)*def_stats['hp'])
    def_hp -= raw_damage
    def_hp_pct -= (def_hp/def_stats['hp']*100)

    #  Write the new HP percentage to the dictionary
    battle_dict['players'][def_in]['active_pokemon']['hp_percent'] = def_hp_pct
    update_battle(battle_JSON, battle_dict)


"""Switches a Pokémon into the active slot for a team. It returns an error
if the Pokémon is already active.

Parameters:
battle_JSON -- the filepath to a Pokémon battle
team_id -- a stringified UUID representing a Pokémon team
poke_id -- a stringified UUID representing the switch-in
"""
def switch(battle_JSON, team_id, poke_id):
    battle_dict = pk.load_data(battle_JSON)

    # Determine which team is swapping
    if battle_dict["players"][0]["team_id"] == team_id:
        team_num = 0
    elif battle_dict["players"][1]["team_id"] == team_id:
        team_num = 1
    # Invalid team ID
    else:
        raise Exception("No team with team ID: {}".format(team_id))

    # Check if pokemon is in backup list
    valid = False
    # The place in the list the pokemon is
    place_list = 0
    for pokemon in battle_dict["players"][team_num]["backup_pokemon"]:
        if pokemon["poke_id"] == poke_id:
            valid = True
            break
        place_list += 1
    # Pokemon not in backup list
    if valid == False:
        raise Exception("No such pokemon in backup list")

    # Pokemon is already active
    if battle_dict["players"][team_num]["active_pokemon"]["poke_id"] == poke_id:
        raise Exception("Pokemon is already active")

    active_pokemon = battle_dict["players"][team_num]["active_pokemon"]
    # Delete unused attributes for inactive pokemon
    del active_pokemon["confused"]
    del active_pokemon["perish_song_turn_count"]
    del active_pokemon["stat_modifiers"]
 
    backup_pokemon = battle_dict["players"][team_num]["backup_pokemon"][place_list]
    # Set default attributes for new pokemon
    backup_pokemon["confused"] = 0
    backup_pokemon["perish_song_turn_count"] = 0
    backup_pokemon["stat_modifiers"] = {
                        "attack": 1,
                        "defense": 1,
                        "special-attack": 1,
                        "special-defense": 1,
                        "speed": 1 }
    # Do the swap
    battle_dict["players"][team_num]["active_pokemon"] = backup_pokemon
    battle_dict["players"][team_num]["backup_pokemon"][place_list] = active_pokemon
    
    update_battle(battle_JSON, battle_dict)
