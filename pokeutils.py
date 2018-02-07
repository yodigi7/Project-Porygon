"""This module will contain several utility functions that are used
by other modules in Project Porygon.
"""
import json
import pokebase as pb


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
                    #
                    # the json file can have more than 6 ivs per pokemon, but
                    # we'll only check/apply the first six
                    for value in range(0, 6):
                        iv = member['ivalues'][value]
                        if iv < 0 or iv > 31:
                            print(str(iv) + ' is not a valid IV!')
                            return False

                    # make sure the effort values are valid and
                    # are applied to stats
                    sumEV = 0
                    stats = ['hp', 'atk', 'def', 'satk', 'sdef', 'spe']
                    for key, value in member['evalues'].items():
                        if key not in stats:
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
