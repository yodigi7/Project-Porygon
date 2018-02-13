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
def team_path(name, team_id):

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

    try:
        level = pokemon['level']
    except KeyError:
        level = DEFAULT_LEVEL

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


"""A function that calculates and returns the raw damage of a Pokémon attack

Parameters:
atk_level -- the level of the attacking Pokémon
atk_stats -- the stats of an attacking Pokémon as a dict
def_stats -- the stats of a defending Pokémon as a dict
attack -- the raw data for a Pokémon move
"""
def calcDamage(atk_level, atk_stats, def_stats, attack):

    #  Calculate damage
    #  I used Bulbapedia for the math. Hopefully it's correct!
    #
    #  The modifier consists of a ton of variables, like weather, STAB,
    #  type effectiveness, damage rolls, etc.
    #  For now, we'll keep it at 1, but it definitely needs attention later.
    modifier = 1

    #  useful variables that correspond to any given attack
    atk_dam_type = attack.damage_class.name
    atk_power = attack.power
    atk_acc = attack.accuracy

    #  get accuracy out of the way
    miss_chance = random.randrange(0,100)
    if miss_chance > atk_acc:
        return 0

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
    else:

        #  status moves will be implemented later
        damage = 0
    return int(damage)

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
