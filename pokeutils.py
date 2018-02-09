"""This module will contain several utility functions that are used
by other modules in Project Porygon.
"""
import json
import pokebase as pb

DEFAULT_LEVEL = 50
DEFAULT_EV = 0
POS_NATURE_MOD = 1.1
NEG_NATURE_MOD = 0.9
POKEMON_STATS = [
    'hp', 'attack', 'defense', 'special-attack', 'special-defense', 'speed'
]


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

    for current_stat in POKEMON_STATS:
        iv = pokemon['ivalues'][current_stat]

        try:
            ev = pokemon['evalues'][current_stat]
        except KeyError:
            ev = DEFAULT_EV

        try:
            level = pokemon['level']
        except KeyError:
            level = DEFAULT_LEVEL

        #  retrieve the corresponding base stat from PokéAPI
        for base in base_stats:
            if base.stat.name == current_stat:
                base_stat = base.base_stat

        if current_stat == 'hp':
            stats[current_stat] = (
                (((2*base_stat)+iv+(ev/4))*level)/100)+level+10
        else:
            stats[current_stat] = (
                ((((2*base_stat)+iv+(ev/4))*level)/100)+5)

        stats[current_stat] = int(stats[current_stat])

        if current_stat == bad_stat:
            stats[current_stat] *= NEG_NATURE_MOD
        elif current_stat == good_stat:
            stats[current_stat] *= POS_NATURE_MOD

        stats[current_stat] = int(stats[current_stat])

    return stats


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
