"""This module will contain several utility functions that are used
by other modules in Project Porygon.
"""
import json
import random
import pokebase as pb

TEAM_DIR = 'examples/'
DEFAULT_LEVEL = 50
DEFAULT_EV = 0
POS_NATURE_MOD = 1.1
NEG_NATURE_MOD = 0.9
POKEMON_STATS = [
    'hp', 'attack', 'defense', 'special-attack', 'special-defense', 'speed'
]


"""A function that loads a JSON file as a python dict and returns it.

Parameters:
path_to_JSON -- the filepath to a JSON
"""
def load_data(path_to_JSON):
    with open(path_to_JSON) as json_data:
        return json.load(json_data)


"""A function that returns the filepath to a team JSON.

Parameters:
name -- the account name of the team owner
team_id -- the UUID of the team
"""
def get_team_path(name, team_id):

    #  convert to lowercase and remove spaces
    name = name.lower()
    name = name.replace(' ','')
    return TEAM_DIR + name + '/' + team_id + '.json'


"""A function that calculates and returns the stats of a Pokémon as a dict.

Parameters:
pokemon -- a list of info that constitutes a Pokémon (see the team JSONs)
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

        #  retrieve the corresponding base stat from PokéAPI
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


"""A function that calculates and returns the raw damage of a Pokémon attack.

Parameters:
atk_poke -- the attacking pokemon as a dict
def_poke -- the defending pokemon as a dict
effective_stats -- a dict containing the current, in-battle stats of each poke
attack -- the raw data for a pokemon attack
"""
def calcDamage(atk_poke, def_poke, effective_stats, attack):

    #  Calculate damage
    #  I used Bulbapedia for the math. Hopefully it's correct!
    
    #  get accuracy out of the way unless one of the Pokémon has No Guard,
    #  in which case it will always hit
    if atk_poke('ability') != 'no-guard' and def_poke('ability') != 'no-guard':
        miss_chance = random.randrange(0,100)
        if miss_chance > atk_acc:
            return 0
    
    #  The modifier consists of a ton of variables, like weather, STAB,
    #  type effectiveness, damage rolls, etc.
    #  Some of it has been implemented, but it still needs more attention later
    #  The weather boosts the power of the move if it is fire type and sunny by 1.5x,
    #  It boosts the power of the move if it is water type and rainy by 1.5x,
    #  It reduces the power of the move if it is fire type and rainy by 0.5x,
    #  It reduces the power of the move if it is water type and sunny by 0.5x,
    #  And it is 1 otherwise. Until weather is implemented, it will remain 1.
    weather_modifier = 1
    
    # Each move has a chance to be a critical hit and deal 1.5x damage.
    # Most moves have a 4.17% chance to be a critical hit, but some have higher odds.
    # For now, each move will have a 4.17% chance to be a critical hit.
    critical = 1
    crit_chance = random.randrange(0, 10000)
    if crit_chance < 417:
        critical = 1.5
    
    # Each attack has a random range multiplier from  0.85 to 1.00
    random_mult = random.randrange(85, 101) / 100
    
    # An attack gets a boost if the Pokémon using the attack shares a type with it.
    # The boost is 1.5x normally, but is increased to 2x if the user has the ability Adaptability.
    # Currently, the function does not include the type of the attack user, so it is
    # set to 1 for now.
    stab = 1
    for atk_type in pb.pokemon(atk_poke['species']).types:
        if atk_type.type.name == attack.type.name:
            stab = 1.5
            if atk_poke('ability') == 'adaptability':
                stab = 2
    
    # Attacks do a different amount of damage based on type matchups. Currently, the types
    # of the defending Pokémon are not implemented, so this modifier is set to 1.
    type_effective = 1
    
    # The power of an attack is halved if the attacker is burned, the attack is physical,
    # the attack is not Facade, and the attacker's ability is not guts.
    # Currently, status and abilities are not implemented, so this value is set to 1.
    burn_modifier = 1
    
    # There is an other modifier that varies based on other factors, which are yet to be
    # implemented. This modifier will be 1 for now.
    other_modifier = 1
    
    # The overall modifier
    modifier = weather_modifier * critical * random_mult * stab * type_effective * burn_modifier * other_modifier

    #  useful variables that correspond to any given attack
    atk_dam_type = attack.damage_class.name
    atk_power = attack.power
    atk_acc = attack.accuracy

    #  the level of the attacker is used in damage calcs
    atk_level = atk_poke['level']

    #  get relevant dictionaries out of effective_stats
    atk_stats = effective_stats['atk_stats']
    def_stats = effective_stats['def_stats']

    #  calcs vary based on physical versus special attacks
    if atk_dam_type == 'physical':
        damage = (
            (((((2*atk_level)/5)+2)*atk_power
            *(atk_stats['attack']/def_stats['defense']))/50)+2)*modifier
    elif atk_dam_type == 'special':
        damage = (
            (((((2*atk_level)/5)+2)*atk_power
            *(atk_stats['special_attck']/def_stats['special_defense']))
            /50)+2)*modifier

    return int(damage)


"""A function that attempts to apply a status ailment to a Pokemon.

This function should determine what status ailment should be applied,
then determine if it could be applied (taking percent chances and
accuracy into account), then return a string representing the ailment
('poison' for poison, 'burn' for burn, and so on). We'll need to keep track
of 'toxic' as a separate ailment from 'poison.'

Parameters:
atk_poke -- the attacking pokemon as a dict
def_poke -- the defending pokemon as a dict
attack -- the raw data for a pokemon attack

Returns a string corresponding to the ailment inflicted
('poison', 'confusion', 'paralysis', etc).
"""
def applyStatus(atk_poke, def_poke, attack):
    # check what status the attack can inflict
    atk_status = attack.meta.ailment.name
    
    # the status to be inflicted, which is set to none in case no status is inflicted
    status_inflicted = 'none'
    
    # if the attack can inflict a status, check to see if it will inflict a status
    if atk_status != 'none':

        # chance that the attack can leave a status condition
        status_prob = attack.meta.ailment_chance

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
            if attack.id == 92 or attack.id == 305:
                status_inflicted = 'toxic'

            # proceed to check if the status can be inflicted on the defending Pokémon
            # Poison and steel types cannot be poisoned, nor can Pokémon with the ability Immunity
            if status_inflicted == 'poison' or status_inflicted == 'toxic':
                for type_name in pb.pokemon(def_poke['species']).types:
                    if type_name.type.name == 'poison' or type_name.type.name == 'steel':
                        status_inflicted = 'none'
                if def_poke['ability'] == 'immunity':
                    status_inflicted = 'none'

            # Fire types cannot be burned, nor can Pokémon with the ability Water Veil
            if status_inflicted == 'burn':
                for type_name in pb.pokemon(def_poke['species']).types:
                    if type_name.type.name == 'fire':
                        status_inflicted = 'none'
                if def_poke['ability'] == 'water-veil':
                    status_inflicted = 'none'

            # Electric types cannot be paralyzed, nor can Pokémon with the ability Limber
            if status_inflicted == 'paralysis':
                for type_name in pb.pokemon(def_poke['species']).types:
                    if type_name.type.name == 'electric':
                        status_inflicted = 'none'
                if def_poke['ability'] == 'limber':
                    status_inflicted = 'none'

            # Ice types cannot be frozen, nor can Pokémon with the ability Magma Armor
            if status_inflicted == 'freeze':
                for type_name in pb.pokemon(def_poke['species']).types:
                    if type_name.type.name == 'ice':
                        status_inflicted = 'none'
                if def_poke['ability'] == 'magma-armor':
                    status_inflicted = 'none'

            # Pokémon with the abilities Insomnia and Vital Spirit cannot be put to sleep
            if status_inflicted == 'sleep':
                if def_poke['ability'] == 'insomnia' or def_poke['ability'] == 'vital-spirit':
                    status_inflicted = 'none'

            # Pokémon with the ability Own Tempo cannot be confused
            if status_inflicted == 'confusion' and def_poke['ability'] == 'own-tempo':
                status_inflicted = 'none'
    return status_inflicted


"""A function that attempts to change the stats of a Pokemon.

This function should return two dictionaries representing the stats of each
battling Pokemon. If the attack only affects the user's stats, you don't need
to bother changing the def_stat_mods, and vice-versa. Return them in attacker,
defender order. Remember that no stat modifier can go below -6 or above +6.

Parameters:
atk_stat_mods -- the attacker's stat modifiers as a dict
def_stat_mods -- the defender's stat modifiers as a dict
attack -- the raw data for a pokemon attack
"""
def changeStats(atk_stat_mods, def_stat_mods, attack):
    pass


"""A function that determines the legality of a Pokémon team.

Parameters:
pathToTeam -- the file path of a JSON document containing a Pokémon team
"""
def verify(pathToTeam):
    try:
        with open(pathToTeam) as team:
            for member in json.load(team)["pokemon"]:

                # make sure the pokemon exists
                try:
                    pokemon = pb.pokemon(member['species'])
                except ValueError:
                    print(member['species'] + ' is not a real Pokémon!')
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
