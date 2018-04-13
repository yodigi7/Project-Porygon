"""This module will contain several utility functions that are used
by other modules in Project Porygon.
"""
import json
import random
import pokebase as pb
import uuid
import os

MAX_POKEMON_ID = 151
USER_TEAMS_DIR = "teams/{}/"    # Path to directory containing teams. <username>
TEAM_PATH = "teams/{}/{}.json"  # Path to a team file. <username> <teamname>
DEFAULT_LEVEL = 50
DEFAULT_EV = 0
POS_NATURE_MOD = 1.1
NEG_NATURE_MOD = 0.9
POKEMON_STATS = [
    'hp', 'attack', 'defense', 'special-attack', 'special-defense', 'speed'
]


def new_default_team(username, teamname):
    return {
        'team_name': teamname,
        'account_name': username,
        'pokemon': [None for _ in range(6)]
    }


def new_default_pokemon(pkid, pkname):
    return {
        "id": pkid,
        "species": pkname,
        "poke_id": uuid.uuid4().hex,
        "nickname": "",
        "gender": "male",
        "nature": "bold",
        "ability": "shed-skin",
        "item": "-NONE-",
        "level": DEFAULT_LEVEL,
        "ivalues": {
            "hp": 16,
            "attack": 16,
            "defense": 16,
            "special-attack": 16,
            "special-defense": 16,
            "speed": 16
        },
        "evalues": {
            "hp": 100,
            "defense": 100,
            "special-defense": 100
        },
        "moves": [
            "-NONE-",
            "-NONE-",
            "-NONE-",
            "-NONE-",
        ]
    }


def display_name_of(name):
    return name.replace('-', ' ').title()


def save_to_file(data, filepath):
    """ Saves JSON from 'data' to a file at 'filepath'. """
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)


def load_from_file(filepath):
    """ Returns a JSON structure loaded from 'filepath'. """
    if os.path.isfile(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    return {}


"""Initializes the battle dictionary and returns it.

Parameters:
team_one, team_two -- dictionaries representing the battling Pokemon teams
(you get these by using pokeutils.load_from_file on the team JSON files)
"""
def initBattle(team_one, team_two):
    battle_dict = {}
    players = []

    #  add pokemon info to player list
    players.append(formatTeamAsBattle(team_one))
    players.append(formatTeamAsBattle(team_two))

    #  add to dict and return
    battle_dict['loser'] = 'none'
    battle_dict['loss_reason'] = 'none'
    battle_dict['weather'] = 'none'
    battle_dict['terrain'] = 'none'
    battle_dict['must_switch'] = []
    battle_dict['players'] = players
    return battle_dict


def delete_empty_slots(team):
    i = 0
    slot = 0
    while i < 6:
        if team['pokemon'][slot] is None:
            del team['pokemon'][slot]
        else:
            slot += 1
        i += 1


"""Converts a Pokemon team into battle format and returns the dictionary.

Parameters:
team -- a dictionary representing a Pokemon team dumped from a team JSON
"""
def formatTeamAsBattle(team):
    player_dict = {}

    #  add metadata to dictionary
    player_dict['account_name'] = team['account_name']
    delete_empty_slots(team)

    #  remove spaces
    player_dict['account_name'] = player_dict['account_name'].replace(' ','')

    #  default values for the active pokemon
    active_pokemon = {
        'hp_percent': 100,
        'used_moves': [],
        'status_condition': 'none',
        'confused': 0,
        'perish_song_turn_count': 0,
        'cursed': 0,
        'seeded': 0,
        'infatuated': 0,
        'trapped': 0,
        'stat_modifiers': {
            'attack': 1,
            'defense': 1,
            'special-attack': 1,
            'special-defense': 1,
            'speed': 1,
            'accuracy': 1,
            'evasion': 1
        }
    }

    backup_pokemon = []
    backup_pokemon_dict = {
        'hp_percent': 100,
        'used_moves': [],
        'status_condition': 'none'
    }

    poke_list = team['pokemon']
    first_poke = poke_list[0]

    #  the first pokemon is the default active pokemon
    active_pokemon['nickname'] = first_poke['nickname']
    active_pokemon['species'] = first_poke['species']
    active_pokemon['gender'] = first_poke['gender']
    active_pokemon['poke_id'] = first_poke['poke_id']

    #  the rest of them are stored as backup pokemon
    for pokemon in poke_list[1:]:
        backup_pokemon_dict['nickname'] = pokemon['nickname']
        backup_pokemon_dict['species'] = pokemon['species']
        backup_pokemon_dict['gender'] = pokemon['gender']
        backup_pokemon_dict['poke_id'] = pokemon['poke_id']

        #  add the dict to the backup_pokemon list
        backup_pokemon.append(backup_pokemon_dict)

    #  add pokemon to player_dict and return
    player_dict['active_pokemon'] = active_pokemon
    player_dict['backup_pokemon'] = backup_pokemon
    return player_dict


"""A function that calculates and returns the base stats
(not including in-battle modifiers) and returns a dict.

Parameters:
pokemon -- a list of info that constitutes a Pokemon (see the team JSONs)
"""
def calcStats(pokemon):
    stats = {}
    base_stats = pb.pokemon(pokemon['species']).stats

    nature = pb.nature(pokemon['nature'])
    bad_stat = nature.decreased_stat.name
    good_stat = nature.increased_stat.name

    level = pokemon['level']

    for current_stat in POKEMON_STATS:
        iv = pokemon['ivalues'][current_stat]

        #  store the effort value for the current stat
        try:
            ev = pokemon['evalues'][current_stat]
        except KeyError:
            ev = DEFAULT_EV

        #  retrieve the corresponding base stat from PokeAPI
        for base in base_stats:
            if base.stat.name == current_stat:
                base_stat = base.base_stat

        #  HP is calculated slightly differently than other stats
        if current_stat == 'hp':
            stats[current_stat] = (
                (((2*base_stat)+iv+(ev/4))*level)/100)+level+10
        else:
            stats[current_stat] = (
                ((((2*base_stat)+iv+(ev/4))*level)/100)+5)

        #  round the stat down
        stats[current_stat] = int(stats[current_stat])

        #  apply nature modifiers
        if current_stat == bad_stat:
            stats[current_stat] *= NEG_NATURE_MOD
        elif current_stat == good_stat:
            stats[current_stat] *= POS_NATURE_MOD

        #  round the stat down again
        stats[current_stat] = int(stats[current_stat])
    return stats


"""A function that calculates and returns the raw damage of a Pokemon attack.

Parameters:
combatants -- a dict containing the current pokemon in battle
raw_stats -- a dict containing the unmodified stats of each poke
modded_stats -- a dict containing the modified stats of each poke
attack -- the raw data for a pokemon attack
battle_dict -- a dictionary containing a Pokemon battle
"""
def calcDamage(combatants, raw_stats, modded_stats, attack, battle_dict):

    #  represents team data for each Pokemon (nature, IVs, EVs, etc)
    atk_poke = combatants['atk_poke_private']
    def_poke = combatants['def_poke_private']

    #  represents battle data for each Pokemon (status, modifiers, etc)
    atk_poke_public = combatants['atk_poke_public']
    def_poke_public = combatants['def_poke_public']
    
    #  useful variables that correspond to any given attack
    atk_dam_type = attack.damage_class.name
    atk_power = attack.power
    
    # Attacks do a different amount of damage based on type matchups.
    type_effective = 1
    attack_type = attack.type.name
    for def_type in pb.pokemon(def_poke['species']).types:
        for immunity in pb.type_(def_type.type.name).damage_relations.no_damage_from:
            if immunity['name'] == attack_type:
                return 0 # move doesn't effect foe, so no damage is dealt
        for resistance in pb.type_(def_type.type.name).damage_relations.half_damage_from:
            if resistance['name'] == attack_type:
                type_effective = type_effective / 2 # move is resisted by this type, so half the factor
        for weakness in pb.type_(def_type.type.name).damage_relations.double_damage_from:
            if weakness['name'] == attack_type:
                type_effective = type_effective * 2 # move is a weakness of this type, so double the factor
            
    
    #  the level of the attacker is used in damage calcs
    atk_level = atk_poke['level']
    
    #  the moves Seismic Toss (id = 69) and Night Shade (id = 101) deal fixed damage based on the level of the attacker
    if attack.id == 69 or attack.id == 101:
        return atk_level
    #  the move Dragon Rage (id = 82) always deals 40 damage
    elif attack.id == 82:
        return 40
    #  the move Sonic Boom (id = 49) always deals 20 damage:
    elif attack.id == 49:
        return 20
    
    #  The modifier consists of a ton of variables, like weather, STAB,
    #  type effectiveness, damage rolls, etc.
    #  Some of it has been implemented, but it still needs more attention later
    #  The weather boosts the power of the move if it is fire type and sunny by 1.5x,
    #  It boosts the power of the move if it is water type and rainy by 1.5x,
    #  It reduces the power of the move if it is fire type and rainy by 0.5x,
    #  It reduces the power of the move if it is water type and sunny by 0.5x,
    #  And it is 1 otherwise. Until weather is implemented, it will remain 1.
    weather_modifier = 1
    # Get the weather from the battle_dict
    weather_condition = battle_dict['weather']
    # Water attacks are boosted in the rain and reduced in the sun
    if attack_type == 'water':
        # If the weather is rain, the attack does 1.5x damage
        if weather_condition == 'rain':
            weather_modifier = 1.5
        # If the weather is sun, the attack does 0.5x damage
        elif weather_condition == 'sun':
            weather_modifier = 0.5
    # Fire attacks are boosted in the sun and reduced in the rain
    elif attack_type == 'fire':
        # If the weather is sun, the attack does 1.5x damage
        if weather_condition == 'sun':
            weather_modifier = 1.5
        # If the weather is rain, the attack does 0.5x damage
        elif weather_condition == 'rain':
            weather_modifier = 0.5
    
    # Each move has a chance to be a critical hit and deal 1.5x damage.
    # Most moves have a 1 in 24 chance to be a critical hit, but some have higher odds.
    crit = False
    # Determine the critical hit stage of the attack. This is based on multiple factors, but for now it will depend only on the move used
    crit_stage = attack.meta.crit_rate
    # Check if the move will be a critical hit. The critical hit is guaranteed if the critical hit stage is at least 3
    crit_chance = 0 # will stay at 0 for guaranteed critical hit if the stage is above 2
    crit_mod = 1  #  stays at 1 unless we score a crit
    if crit_stage == 0: # No crit modification, 1 in 24 chance to crit
        crit_chance = random.randrange(0, 24)
    elif crit_stage == 1: # +1 crit modifier, 1 in 8 chance to crit
        crit_chance = random.randrange(0, 8)
    elif crit_stage == 2: # +2 crit modifier, 1 in 2 chance to crit
        crit_chance = random.randrange(0, 2)
    if crit_chance == 0:
        crit = True
        crit_mod = 1.5
    
    # Each attack has a random range multiplier from  0.85 to 1.00
    random_mult = random.randrange(85, 101) / 100
    
    # An attack gets a boost if the Pokemon using the attack shares a type with it.
    # The boost is 1.5x normally, but is increased to 2x if the user has the ability Adaptability.
    stab = 1
    for atk_type in pb.pokemon(atk_poke['species']).types:
        if atk_type.type.name == attack.type.name:
            stab = 1.5
            if atk_poke['ability'] == 'adaptability':
                stab = 2
    
    
    
    # The power of an attack is halved if the attacker is burned, the attack is physical,
    # the attack is not Facade, and the attacker's ability is not guts.
    # Currently, abilities are not connected to these functions, so Guts is not implemented.
    burn_modifier = 1
    if attack.id != 263 and atk_poke_public['status_condition'] == 'burn' and atk_dam_type == 'physical':
        burn_modifier = 0.5
    
    # There is an other modifier that varies based on other factors, which are yet to be
    # implemented. This modifier will be 1 for now.
    other_modifier = 1
    
    # The overall modifier
    modifier = weather_modifier * crit_mod * random_mult * stab * type_effective * burn_modifier * other_modifier


    #  get relevant stat dictionaries
    atk_stats = modded_stats['atk_stats']
    def_stats = modded_stats['def_stats']
    #  in the case of a crit, we use the defender's unmodified stats if those are lower than the modified stats
    if crit and atk_dam_type == 'physical' and raw_stats['def_stats']['defense'] < def_stats['defense']:
        def_stats = raw_stats['def_stats']
    elif crit and atk_dam_type == 'special' and raw_stats['def_stats']['special-defense'] < def_stats['special-defense']:
        def_stats = raw_stats['def_stats']
    # in the case of a crit, we use the attacker's unmodified stats if those are higher than the modified stats
    if crit and atk_dam_type == 'physical' and raw_stats['atk_stats']['attack'] > atk_stats['attack']:
        atk_stats = raw_stats['atk_stats']
    elif crit and atk_dam_type == 'special' and raw_stats['atk_stats']['special-attack'] > atk_stats['special-attack']:
        atk_stats = raw_stats['atk_stats']

    #  calcs vary based on physical versus special attacks, although the moves Psyshock (id = 473),
    #  Secret Sword (id = 548), and Psystrike (id = 540) deal physical damage off of the attacker's special attack stat
    if atk_dam_type == 'physical':
        damage_unrounded = (
            (((((2*atk_level)/5)+2)*atk_power
            *(atk_stats['attack']/def_stats['defense']))/50)+2)*modifier
    elif attack.id == 473 or attack.id == 548 or attack.id == 540:
        damage_unrounded = (
            (((((2*atk_level)/5)+2)*atk_power
            *(atk_stats['special-attack']/def_stats['defense']))
            /50)+2)*modifier
    elif atk_dam_type == 'special':
        # Check to see if the special defense is boosted by sandstorm
        sand_boost = 1
        if weather_condition == 'sand':
            # Check if the defending Pokémon is a rock type
            for def_type in pb.pokemon(def_poke['species']).types:
                if def_type.name == 'rock':
                    # Special defense is boosted by 1.5x for rock types in sandstorm
                    sand_boost = 1.5
        damage_unrounded = (
            (((((2*atk_level)/5)+2)*atk_power
            *(atk_stats['special-attack']/(def_stats['special-defense'] * sand_boost)))
            /50)+2)*modifier
    #  round the damage dealt to a whole number
    damage = int(damage_unrounded)
    #  if no damage would be dealt, the minimum damage of 1 is dealt instead
    if damage == 0:
        damage = 1
    
    return damage


"""A function that attempts to apply a status ailment to a Pokemon.

This function should determine what status ailment should be applied,
then determine if it could be applied (taking percent chances and
accuracy into account), then return a string representing the ailment
('poison' for poison, 'burn' for burn, and so on). We'll need to keep track
of 'toxic' as a separate ailment from 'poison.'

Parameters:
combatants -- a dict that contains all the information for the battling Pokemon
attack -- the raw data for a pokemon attack

Returns a string corresponding to the ailment inflicted
('poison', 'confusion', 'paralysis', etc).
"""
def applyStatus(combatants, attack):
    atk_poke = combatants['atk_poke_private']
    def_poke = combatants['def_poke_private']

    # check what status the attack can inflict
    atk_status = attack.meta.ailment.name
    
    # the status to be inflicted, which is set to none in case no status is inflicted
    status_inflicted = 'none'
    
    # if the attack can inflict a status, check to see if it will inflict a status
    if atk_status != 'none':

        # chance that the attack can leave a status condition
        status_prob = attack.meta.ailment_chance
        
        # if the attacking Pokemon has the ability Serene Grace, the chance to implement a status is doubled
        if atk_poke['ability'] == 'serene-grace':
            status_prob = status_prob * 2

        # check if status is inflicted, it will be inflicted if a random number generated is less than
        # the percent chance to inflict that status
        status_chance = random.randrange(0,100)
        if status_chance < status_prob or status_prob == 0:
            status_inflicted = atk_status

            # case for Tri Attack inflicting a status, as it has a 20% to inflict either
            # paralysis, burn, or freeze with equal probability of ~6.67%.
            if attack.id == 161:
                status_id = random.randrange(0,3)
                if status_id == 0:
                    status_inflicted = 'burn'
                elif status_id == 1:
                    status_inflicted = 'paralysis'
                else:
                    status_inflicted = 'freeze'
            # The attacks Toxic and Poison Fang inflict Bad Poison rather than regular poison,
            # but the API does not distinguish between bad poison and regular poison; these
            # attacks have internal ids of 92 and 305 in the API
            elif attack.id == 92 or attack.id == 305:
                status_inflicted = 'toxic'

            # proceed to check if the status can be inflicted on the defending Pokemon
            # Poison and steel types cannot be poisoned, nor can Pokemon with the ability Immunity
            if status_inflicted == 'poison' or status_inflicted == 'toxic':
                for type_name in pb.pokemon(def_poke['species']).types:
                    if type_name.type.name == 'poison' or type_name.type.name == 'steel':
                        status_inflicted = 'none'
                if def_poke['ability'] == 'immunity':
                    status_inflicted = 'none'
            # Fire types cannot be burned, nor can Pokemon with the ability Water Veil
            elif status_inflicted == 'burn':
                for type_name in pb.pokemon(def_poke['species']).types:
                    if type_name.type.name == 'fire':
                        status_inflicted = 'none'
                if def_poke['ability'] == 'water-veil':
                    status_inflicted = 'none'
            # Electric types cannot be paralyzed, nor can Pokemon with the ability Limber
            elif status_inflicted == 'paralysis':
                for type_name in pb.pokemon(def_poke['species']).types:
                    if type_name.type.name == 'electric':
                        status_inflicted = 'none'
                if def_poke['ability'] == 'limber':
                    status_inflicted = 'none'
            # Ice types cannot be frozen, nor can Pokemon with the ability Magma Armor
            elif status_inflicted == 'freeze':
                for type_name in pb.pokemon(def_poke['species']).types:
                    if type_name.type.name == 'ice':
                        status_inflicted = 'none'
                if def_poke['ability'] == 'magma-armor':
                    status_inflicted = 'none'
            # Pokemon with the abilities Insomnia and Vital Spirit cannot be put to sleep
            elif status_inflicted == 'sleep':
                if def_poke['ability'] == 'insomnia' or def_poke['ability'] == 'vital-spirit':
                    status_inflicted = 'none'
            # Pokemon with the ability Own Tempo cannot be confused
            elif status_inflicted == 'confusion' and def_poke['ability'] == 'own-tempo':
                status_inflicted = 'none'
            # Grass types cannot be affected by Leech Seed
            elif status_inflicted == 'leech-seed':
                for type_name in pb.pokemon(def_poke['species']).types:
                    if type_name.type.name == 'grass':
                        status_inflicted = 'none'
            # Genderless Pokemon cannot be attracted, nor can Pokemon with the ability Oblivious or Pokemon of the same gender
            elif status_inflicted == 'infatuation':
                if atk_poke['gender'] == 'genderless' or def_poke['gender'] == 'genderless' or atk_poke['gender'] == def_poke['gender'] or def_poke['ability'] == 'oblivious':
                    status_inflicted = 'none'
            # Grass types cannot be affected by powder moves, nor can Pokemon with the ability Overcoat
            # Powder moves that inflict status are Stun Spore, Spore, Sleep Powder, and Poison Powder
            # These attacks have ids of 78, 147, 79, and 77
            if attack.id == 77 or attack.id == 78 or attack.id == 79 or attack.id == 147:
                for type_name in pb.pokemon(def_poke['species']).types:
                    if type_name.type.name == 'grass':
                        status_inflicted = 'none'
                if def_poke['ability'] == 'overcoat':
                    status_inflicted = 'none'
    # Case for curse, as status is listed as 'none' in PokeAPI
    # Curse applies a curse effect if the user is ghost type, curse has internal id of 174
    # No Pokemon is innately immune to curse
    elif attack.id == 174:
        for type_name in pb.pokemon(atk_poke['species']).types:
            if type_name.type.name == 'ghost':
                status_inflicted = 'curse'
    # Case for taunt, as status is listed as 'none' in API
    # Pokemon with the ability Oblivious are immune to the effects of taunt
    # Taunt has an id of 269
    elif attack.id == 269 and def_poke['ability'] != 'oblivious':
        status_inflicted = 'taunt'
    return status_inflicted


"""A function that attempts to change the stats of a Pokemon.

This function should return two dictionaries representing the stats of each
battling Pokemon. If the attack only affects the user's stats, you don't need
to bother changing the def_stat_mods, and vice-versa. Return them in attacker,
defender order. Remember that no stat modifier can go below -6 or above +6.

Parameters:
atk_poke -- the attacking pokemon as a dict
def_poke -- the defending pokemon as a dict
atk_stat_mods -- the attacker's stat modifiers as a dict
def_stat_mods -- the defender's stat modifiers as a dict
attack -- the raw data for a pokemon attack
"""
#def changeStats(atk_poke, def_poke, atk_stat_mods, def_stat_mods, attack):
def changeStats(combatants, attack):
    atk_poke = combatants['atk_poke_private']
    def_poke = combatants['def_poke_private']
    atk_stat_mods = combatants['atk_poke_public']['stat_modifiers']
    def_stat_mods = combatants['def_poke_public']['stat_modifiers']

    stage_to_mod = {-6: 0.25, -5: 0.29, -4: 0.33, -3: 0.4, -2: 0.5, -1: 0.67, 0: 1, 1: 1.5, 2: 2, 3: 2.5, 4: 3, 5: 3.5, 6: 4}
    mod_to_stage = {0.25: -6, 0.29: -5, 0.33: -4, 0.4: -3, 0.5: -2, 0.67: -1, 1: 0, 1.5: 1, 2: 2, 2.5: 3, 3: 4, 3.5: 5, 4: 6}
    stat_chance = attack.meta.stat_chance
    # Double the chance of causing a stat change if the attacker has Serene Grace
    if atk_poke['ability'] == 'serene-grace':
        stat_chance = stat_chance * 2
    stat_changed_prob = random.randrange(0,100)
    if stat_changed_prob < stat_chance or stat_chance == 0:
        # Figure out which Pokemon's stats will be changed
        poke_effected = ''
        if attack.meta.category.name == 'damage+lower' or attack.meta.category.name == 'swagger':
            poke_effected = 'def_poke'
        elif attack.meta.category.name == 'damage+raise':
            poke_effected = 'atk_poke'
        elif attack.meta.category.name == 'net-good-stats':
            if attack.stat_changes[0].change > 0:
                poke_effected = 'atk_poke'
            else:
                poke_effected = 'def_poke'
        # check each stat that will be changed and try to change it
        for stat in attack.stat_changes:
            stat_changed = stat.stat.name
            change = stat.change
            if poke_effected == 'atk_poke':
                if stat_changed == 'attack':
                    stat_stage = mod_to_stage[atk_stat_mods['attack']]
                    stat_stage = stat_stage + change
                    if stat_stage > 6:
                        stat_stage = 6
                    elif stat_stage < -6:
                        stat_stage = -6
                    atk_stat_mods['attack'] = stage_to_mod[stat_stage]
                if stat_changed == 'defense':
                    stat_stage = mod_to_stage[atk_stat_mods['defense']]
                    stat_stage = stat_stage + change
                    if stat_stage > 6:
                        stat_stage = 6
                    elif stat_stage < -6:
                        stat_stage = -6
                    atk_stat_mods['defense'] = stage_to_mod[stat_stage]
                if stat_changed == 'special-attack':
                    stat_stage = mod_to_stage[atk_stat_mods['special-attack']]
                    stat_stage = stat_stage + change
                    if stat_stage > 6:
                        stat_stage = 6
                    elif stat_stage < -6:
                        stat_stage = -6
                    atk_stat_mods['special-attack'] = stage_to_mod[stat_stage]
                if stat_changed == 'special-defense':
                    stat_stage = mod_to_stage[atk_stat_mods['special-defense']]
                    stat_stage = stat_stage + change
                    if stat_stage > 6:
                        stat_stage = 6
                    elif stat_stage < -6:
                        stat_stage = -6
                    atk_stat_mods['special-defense'] = stage_to_mod[stat_stage]
                if stat_changed == 'speed':
                    stat_stage = mod_to_stage[atk_stat_mods['speed']]
                    stat_stage = stat_stage + change
                    if stat_stage > 6:
                        stat_stage = 6
                    elif stat_stage < -6:
                        stat_stage = -6
                    atk_stat_mods['speed'] = stage_to_mod[stat_stage]
                if stat_changed == 'accuracy':
                    atk_stat_mods['accuracy'] = atk_stat_mods['accuracy'] + change
                    if atk_stat_mods['accuracy'] > 6:
                        atk_stat_mods['accuracy'] = 6
                    elif atk_stat_mods['accuracy'] < -6:
                        atk_stat_mods['accuracy'] = -6
                if stat_changed == 'evasion':
                    atk_stat_mods['evasion'] = atk_stat_mods['evasion'] + change
                    if atk_stat_mods['evasion'] > 6:
                        atk_stat_mods['evasion'] = 6
                    elif atk_stat_mods['evasion'] < -6:
                        atk_stat_mods['evasion'] = -6
            else:
                if stat_changed == 'attack':
                    # the abilities hyper-cutter and clear body prevent opponents from lowering the Pokemon's attack
                    # the ability Mold Breaker ignores this
                    if (def_poke['ability'] == 'hyper-cutter' or def_poke['ability'] == 'clear-body') and atk_poke['ability'] != 'mold-breaker' and change < 0:
                        pass
                    else:
                        stat_stage = mod_to_stage[def_stat_mods['attack']]
                        stat_stage = stat_stage + change
                        if change < 0 and def_poke['ability'] == 'defiant' and (stat_stage - change > -6):
                            # If the attack stat was lowered, raise it by 2 stages if the defending mon has defiant
                            stat_stage = stat_stage + 2
                        elif change < 0 and def_poke['ability'] == 'competitive' and (stat_stage - change > -6):
                            # If a stat was lowered and the defending mon has competitive, increase special attack by 2 stages
                            sp_atk_stage = mod_to_stage[def_stat_mods['special-attack']] + 2
                            if sp_atk_stage > 6:
                                sp_atk_stage = 6
                            def_stat_mods['special-attack'] = stage_to_mod[sp_atk_stage]
                        if stat_stage > 6:
                            stat_stage = 6
                        elif stat_stage < -6:
                            stat_stage = -6
                        def_stat_mods['attack'] = stage_to_mod[stat_stage]
                if stat_changed == 'defense':
                    # the abilities big pecks and clear body prevent opponents from lowering the Pokemon's defense
                    # the ability Mold Breaker ignores this
                    if (def_poke['ability'] == 'big-pecks' or def_poke['ability'] == 'clear-body') and atk_poke['ability'] != 'mold-breaker' and change < 0:
                        pass
                    else:
                        stat_stage = mod_to_stage[def_stat_mods['defense']]
                        stat_stage = stat_stage + change
                        if change < 0 and def_poke['ability'] == 'defiant' and (stat_stage - change > -6):
                            # If a stat was lowered and the defending mon has defiant, increase attack by 2 stages
                            atk_stage = mod_to_stage[def_stat_mods['attack']] + 2
                            if atk_stage > 6:
                                atk_stage = 6
                            def_stat_mods['attack'] = stage_to_mod[atk_stage]
                        elif change < 0 and def_poke['ability'] == 'competitive' and (stat_stage - change > -6):
                            # If a stat was lowered and the defending mon has competitive, increase special attack by 2 stages
                            sp_atk_stage = mod_to_stage[def_stat_mods['special-attack']] + 2
                            if sp_atk_stage > 6:
                                sp_atk_stage = 6
                            def_stat_mods['special-attack'] = stage_to_mod[sp_atk_stage]
                        if stat_stage > 6:
                            stat_stage = 6
                        elif stat_stage < -6:
                            stat_stage = -6
                        def_stat_mods['defense'] = stage_to_mod[stat_stage]
                if stat_changed == 'special-attack':
                    # The ability clear body prevents opponents from lowering special attack
                    # The ability mold breaker ignores this
                    if def_poke['ability'] == 'clear-body' and atk_poke['ability'] != 'mold-breaker' and change < 0:
                        pass
                    else:
                        stat_stage = mod_to_stage[def_stat_mods['special-attack']]
                        stat_stage = stat_stage + change
                        if change < 0 and def_poke['ability'] == 'defiant' and (stat_stage - change > -6):
                            # If a stat was lowered and the defending mon has defiant, increase attack by 2 stages
                            atk_stage = mod_to_stage[def_stat_mods['attack']] + 2
                            if atk_stage > 6:
                                atk_stage = 6
                            def_stat_mods['attack'] = stage_to_mod[atk_stage]
                        elif change < 0 and def_poke['ability'] == 'competitive' and (stat_stage - change > -6):
                            # If a stat was lowered and the defending mon has competitive, increase special attack by 2 stages
                            stat_stage = stat_stage + 2
                        if stat_stage > 6:
                            stat_stage = 6
                        elif stat_stage < -6:
                            stat_stage = -6
                        def_stat_mods['special-attack'] = stage_to_mod[stat_stage]
                if stat_changed == 'special-defense':
                    # The ability clear body prevents opponents from lowering special defense
                    # The ability mold breaker ignores this
                    if def_poke['ability'] == 'clear-body' and atk_poke['ability'] != 'mold-breaker' and change < 0:
                        pass
                    else:
                        stat_stage = mod_to_stage[def_stat_mods['special-defense']]
                        stat_stage = stat_stage + change
                        if change < 0 and def_poke['ability'] == 'defiant' and (stat_stage - change > -6):
                            # If a stat was lowered and the defending mon has defiant, increase attack by 2 stages
                            atk_stage = mod_to_stage[def_stat_mods['attack']] + 2
                            if atk_stage > 6:
                                atk_stage = 6
                            def_stat_mods['attack'] = stage_to_mod[atk_stage]
                        elif change < 0 and def_poke['ability'] == 'competitive' and (stat_stage - change > -6):
                            # If a stat was lowered and the defending mon has competitive, increase special attack by 2 stages
                            sp_atk_stage = mod_to_stage[def_stat_mods['special-attack']] + 2
                            if sp_atk_stage > 6:
                                sp_atk_stage = 6
                            def_stat_mods['special-attack'] = stage_to_mod[sp_atk_stage]
                        if stat_stage > 6:
                            stat_stage = 6
                        elif stat_stage < -6:
                            stat_stage = -6
                        def_stat_mods['special-defense'] = stage_to_mod[stat_stage]
                if stat_changed == 'speed':
                    # The ability clear body prevents opponents from lowering speed
                    # The ability mold breaker ignores this
                    if def_poke['ability'] == 'clear-body' and atk_poke['ability'] != 'mold-breaker' and change < 0:
                        pass
                    else:
                        stat_stage = mod_to_stage[def_stat_mods['speed']]
                        stat_stage = stat_stage + change
                        if change < 0 and def_poke['ability'] == 'defiant' and (stat_stage - change > -6):
                            # If a stat was lowered and the defending mon has defiant, increase attack by 2 stages
                            atk_stage = mod_to_stage[def_stat_mods['attack']] + 2
                            if atk_stage > 6:
                                atk_stage = 6
                            def_stat_mods['attack'] = stage_to_mod[atk_stage]
                        elif change < 0 and def_poke['ability'] == 'competitive' and (stat_stage - change > -6):
                            # If a stat was lowered and the defending mon has competitive, increase special attack by 2 stages
                            sp_atk_stage = mod_to_stage[def_stat_mods['special-attack']] + 2
                            if sp_atk_stage > 6:
                                sp_atk_stage = 6
                            def_stat_mods['special-attack'] = stage_to_mod[sp_atk_stage]
                        if stat_stage > 6:
                            stat_stage = 6
                        elif stat_stage < -6:
                            stat_stage = -6
                        def_stat_mods['speed'] = stage_to_mod[stat_stage]
                if stat_changed == 'accuracy':
                    # the abilities keen eye and clear body prevent opponents from lowering the Pokemon's accuracy
                    # the ability Mold Breaker ignores this
                    if (def_poke['ability'] == 'keen-eye' or def_poke['ability'] == 'clear-body') and atk_poke['ability'] != 'mold-breaker' and change < 0:
                        pass
                    else:
                        def_stat_mods['accuracy'] = def_stat_mods['accuracy'] + change
                        if change < 0 and def_poke['ability'] == 'defiant' and (stat_stage - change > -6):
                            # If a stat was lowered and the defending mon has defiant, increase attack by 2 stages
                            atk_stage = mod_to_stage[def_stat_mods['attack']] + 2
                            if atk_stage > 6:
                                atk_stage = 6
                            def_stat_mods['attack'] = stage_to_mod[atk_stage]
                        elif change < 0 and def_poke['ability'] == 'competitive' and (stat_stage - change > -6):
                            # If a stat was lowered and the defending mon has competitive, increase special attack by 2 stages
                            sp_atk_stage = mod_to_stage[def_stat_mods['special-attack']] + 2
                            if sp_atk_stage > 6:
                                sp_atk_stage = 6
                            def_stat_mods['special-attack'] = stage_to_mod[sp_atk_stage]
                        if def_stat_mods['accuracy'] > 6:
                            def_stat_mods['accuracy'] = 6
                        elif def_stat_mods['accuracy'] < -6:
                            def_stat_mods['accuracy'] = -6
                if stat_changed == 'evasion':
                    # The ability clear body prevents opponents from lowering evasion
                    # The ability mold breaker ignores this
                    if def_poke['ability'] == 'clear-body' and atk_poke['ability'] != 'mold-breaker' and change < 0:
                        pass
                    else:
                        def_stat_mods['evasion'] = def_stat_mods['evasion'] + change
                        if change < 0 and def_poke['ability'] == 'defiant' and (stat_stage - change > -6):
                            # If a stat was lowered and the defending mon has defiant, increase attack by 2 stages
                            atk_stage = mod_to_stage[def_stat_mods['attack']] + 2
                            if atk_stage > 6:
                                atk_stage = 6
                            def_stat_mods['attack'] = stage_to_mod[atk_stage]
                        elif change < 0 and def_poke['ability'] == 'competitive' and (stat_stage - change > -6):
                            # If a stat was lowered and the defending mon has competitive, increase special attack by 2 stages
                            sp_atk_stage = mod_to_stage[def_stat_mods['special-attack']] + 2
                            if sp_atk_stage > 6:
                                sp_atk_stage = 6
                            def_stat_mods['special-attack'] = stage_to_mod[sp_atk_stage]
                        if def_stat_mods['evasion'] > 6:
                            def_stat_mods['evasion'] = 6
                        elif def_stat_mods['evasion'] < -6:
                            def_stat_mods['evasion'] = -6
    return [atk_stat_mods, def_stat_mods]


"""A function that determines the legality of a Pokemon team.

Parameters:
pathToTeam -- the file path of a JSON document containing a Pokemon team
"""
def verify(pathToTeam):
    try:
        with open(pathToTeam) as team:
            for member in json.load(team)["pokemon"]:

                # make sure the pokemon exists
                try:
                    pokemon = pb.pokemon(member['species'])
                except ValueError:
                    print(member['species'] + ' is not a real Pokemon!')
                    return False

                # make sure the nature exists
                try:
                    nature = pb.nature(member['nature'])
                except ValueError:
                    print(member['nature'] + ' is not a valid nature!')
                    return False

                # make sure the item exists
                try:
                    item = pb.item(member['item'])
                except ValueError:
                    print(member['item'] + ' is not a valid item!')
                    return False

                # make sure the ability exists and belongs to this pokemon
                for value in pokemon.abilities:
                    if value.ability.name == member['ability']:
                        break
                else:
                    print(
                    member['name'] + ' can\'t have ' + member['ability']
                    + '!')
                    return False

                # make sure the individual values make sense
                for key, value in member['ivalues'].items():
                    if value < 0 or value > 31:
                        print(str(value) + ' is not a valid IV!')
                        return False

                # make sure the effort values are valid and
                # are applied to stats
                sumEV = 0
                for key, value in member['evalues'].items():
                    if key not in POKEMON_STATS:
                        print(key + ' is not a valid stat!')
                        return False
                    if value > 252:
                        print(str(value) + ' is too high of an EV!')
                        return False
                    if value < 0:
                        print(str(value) + ' is too low of an EV!')
                        return False
                    sumEV += value
                    if sumEV > 510:
                        print(member['name'] + ' has too many EVs!')
                        return False

                # make sure the moveset is valid
                parsedMoves = []
                for value in member['moves']:
                    if value in parsedMoves:
                        print(
                        member['name'] + ' has two of the same move!')
                        return False
                    for move in pokemon.moves:
                        if value == move.move.name:
                            break
                    else:
                        print(
                        value + ' is not a valid move for ' + member['name']
                        + '!')
                        return False
                    parsedMoves.append(value)
    except FileNotFoundError:
        print(pathToTeam + ' doesn\'t exist!')
        return False
