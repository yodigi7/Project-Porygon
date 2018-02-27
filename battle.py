"""This module contains several functions that emulate the logic 
for a Pokémon battle. In particular, it requires a strict adherence 
to a predefined JSON format. See the examples folder for details.

At the moment, Project Porygon only supports 2-player single battles.
"""
import json
import pokebase as pb
import pokeutils as pk


"""Updates the battle JSON file.

Parameters:
battle_JSON -- the filepath to a Pokémon battle JSON
updated_JSON -- the updated python dictionary representing the battle
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

    #  determine the attacking and defending pokémon
    #  currently, this only supports 2 player single battles
    if battle_dict['players'][0]['active_pokemon']['poke_id'] == poke_id:
        atk_player = battle_dict['players'][0]
        def_player = battle_dict['players'][1]
        atk_in, def_in = 0, 1
    else:
        atk_player = battle_dict['players'][1]
        def_player = battle_dict['players'][0]
        atk_in, def_in = 1, 0

    #  grab the ID for the defending pokémon
    def_poke_id = def_player['active_pokemon']['poke_id']

    #  get the path to each player's team
    atk_team_path = pk.get_team_path(
    atk_player['account_name'],atk_player['team_id'])
    def_team_path = pk.get_team_path(
    def_player['account_name'],def_player['team_id'])

    #  load stat modifiers and HP percentages
    atk_stat_mods = atk_player['active_pokemon']['stat_modifiers']
    atk_hp_pct = atk_player['active_pokemon']['hp_percent']
    def_stat_mods = def_player['active_pokemon']['stat_modifiers']
    def_hp_pct = def_player['active_pokemon']['hp_percent']

    #  dictionaries to keep utils parameters organized
    raw_stats = {}
    modified_stats = {}
    combatants = {}

    #  Load the attacking Pokémon and calculate effective stats
    atk_team = pk.load_data(atk_team_path)
    for pokemon in atk_team['pokemon']:
        if pokemon['poke_id'] == poke_id:

            #  calculate stats and apply modifiers, then store in a dict
            raw_stats['atk_stats'] = pk.calcStats(pokemon)
            for key, value in raw_stats['atk_stats'].items():
                if key != 'hp':
                    modded_stats['atk_stats'][key] = value*atk_stat_mods[key]

            #  Load the attack data
            attack = pb.move(pokemon['moves'][atk_index])

            #  store the pokemon, pass it to functions later
            combatants['atk_poke'] = pokemon

    #  Load the defending Pokémon and calculate effective stats
    def_team = pk.load_data(def_team_path)
    for pokemon in def_team['pokemon']:
        if pokemon['poke_id'] == def_poke_id:

            #  calculate stats and apply modifiers, then store in a dict
            raw_stats['def_stats'] = pk.calcStats(pokemon)
            for key, value in raw_stats['def_stats'].items():
                if key != 'hp':
                    modded_stats['atk_stats'][key] = value*atk_stat_mods[key]

            #  store the pokemon, pass it to functions later
            combatants['def_poke'] = pokemon


    """The meat of the attack function. This is where the attack is actually
    performed and the results are written to the battle dictionary.
    """
    atk_category = attack.meta.category.name
    if 'damage' in atk_category:
        raw_damage = pk.calcDamage(combatants, raw_stats, modded_stats, attack)

        #  Convert from an HP percentage to an HP amount and back again
        def_hp = int((def_hp_pct/100)*def_stats['hp'])
        def_hp -= raw_damage
        def_hp_pct = int(def_hp/def_stats['hp']*100)

        #  Write the new HP percentage to the dictionary
        battle_dict['players'][def_in]['active_pokemon']['hp_percent'] = def_hp_pct

    #  if the attack inflicts an ailment, try to inflict the ailment
    def_poke_status = def_player['active_pokemon']['status_condition']
    def_poke_confused = def_player['active_pokemon']['confused']
    if 'ailment' in atk_category:
        status = pk.applyStatus(combatants, attack)

        #  confusion is separate from status conditions
        #  we'll have to make an exception for 'curse' too
        #  and leech seed, oh god there's so many
        if status == 'confusion' and def_poke_confused == 0:
            battle_dict['players'][def_in]['active_pokemon']['confused'] = random.randrange(1, 5)
        elif status == 'curse':
            battle_dict['players'][def_in]['active_pokemon']['curse'] = True
        elif status == 'leech-seed':
            battle_dict['players'][def_in]['active_pokemon']['leech-seed'] = True
        elif status == 'infatuation':
            battle_dict['players'][def_in]['active_pokemon']['infatuation'] = True
        elif status == 'perish-song':
            if battle_dict['players'][def_in]['active_pokemon']['perish_song_turn_count'] == 0:
                battle_dict['players'][def_in]['active_pokemon']['perish_song_turn_count'] = 4
            if battle_dict['players'][atk_in]['active_pokemon']['perish_song_turn_count'] == 0:
                battle_dict['players'][atk_in]['active_pokemon']['perish_song_turn_count'] = 4
        elif def_poke_status == 'none':
            battle_dict['players'][def_in]['active_pokemon']['status_condition'] = status

    #  if the attack tries to change stats, try to change stats
    if 'stats' in atk_category:
        atk_stat_mods, def_stat_mods = pk.changeStats(atk_stat_mods, def_stat_mods, attack)
        battle_dict['players'][atk_in]['active_pokemon']['stat_modifiers'] = atk_stat_mods
        battle_dict['players'][def_in]['active_pokemon']['stat_modifiers'] = def_stat_mods

    return battle_dict


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
                        "speed": 1,
                        "accuracy": 0,
                        "evasion": 0 }
    # Do the swap
    battle_dict["players"][team_num]["active_pokemon"] = backup_pokemon
    battle_dict["players"][team_num]["backup_pokemon"][place_list] = active_pokemon
    
    update_battle(battle_JSON, battle_dict)
