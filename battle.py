"""This module contains several functions that emulate the logic 
for a Pokémon battle. In particular, it requires a strict adherence 
to a predefined JSON format. The entries in that JSON are as follows:

players -- a list of players involved in the battle

account_name -- the name of the corresponding player's account
team_id -- a UUID that corresponds to the player's current team
active_pokemon -- a dictionary containing battle information for the 
currently active Pokémon

name -- the nickname of the Pokémon
species -- the species of the Pokémon
poke_id -- a UUID that represents a Pokémon; used mostly to look up 
the ivalues/evalues/nature/moveset of the Pokémon for calculations
hp_percent -- the percentage of the Pokémon's remaining HP
used_moves -- a list of moves that have been used by the Pokémon 
in the current battle
status_condition -- the Pokémon's status condition
confused -- a boolean that represents confusion
perish_song_turn_count -- a count that represents how many turns 
the Pokémon has been under Perish Song. When it reaches 3, the 
Pokémon faints.
stat_modifiers -- a list of stat modifiers (HP is excluded)

backup_Pokémon -- a list of the Pokémon on a team that are not 
currently active
"""
import json
import random
import pokebase as pb
import pokeutils as pk


"""Performs an attack using the stats of the passed Pokémon.

Parameters:
battle_JSON -- the filepath to a Pokémon battle
atk_index -- a number from 0 to 3 that indicates the selected move
poke_id -- a stringified UUID representing the attacking Pokémon
"""
def attack(battle_JSON, atk_index, poke_id):
    pass


"""Switches a Pokémon into the active slot for a team. It returns an error
if the Pokémon is already active.

Parameters:
battle_JSON -- the filepath to a Pokémon battle
team_id -- a stringified UUID representing a Pokémon team
poke_id -- a stringified UUID representing the switch-in
"""
def switch(battle_JSON, team_id, poke_id):
    battle_dict = load_battle(battle_JSON)
    
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
    backup_pokemon["stat_modifiers"] = [{
                        "attack": 0,
                        "defense": 0,
                        "special-attack": 0,
                        "special-defense": 0,
                        "speed": 0}]
    # Do the swap
    battle_dict["players"][team_num]["active_pokemon"] = backup_pokemon
    battle_dict["players"][team_num]["backup_pokemon"][place_list] = active_pokemon
    
    update_battle(battle_JSON, battle_dict)
