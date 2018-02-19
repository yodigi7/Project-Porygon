"""Some unit tests to make sure stat modifiers are updating correctly.
Again, I should probably look into pytest.
"""
import pokebase as pb
import pokeutils as pk


"""Tests raising the user's stats.
"""
def testRaiseStats():
    atk_mods = {
        'attack': 1,
        'defense': 1,
        'special-attack': 1,
        'special-defense': 1,
        'speed': 1
    }

    def_mods = {}

    attack = pb.move('work-up')
    atk_mods, def_mods = changeStats(atk_mods, def_mods, attack)

    #  make sure stat modifiers are updated appropriately
    if atk_mods['attack'] != 1.5 or atk_mods['special-attack'] != 1.5:
        raise ValueError('stats weren\'t raised correctly!')

    attack = pb.move('swords-dance')
    atk_mods, def_mods = changeStats(atk_mods, def_mods, attack)

    #  make sure stat modifiers are updated appropriately
    if atk_mods['attack'] != 2.5 or atk_mods['special-attack'] != 1.5:
        raise ValueError('stats weren\'t raised correctly!')


"""Tests failing to raise the user's stats.
"""
def testRaiseStatsFail():
    atk_mods = {
        'attack': 4,
        'defense': 1,
        'special-attack': 4,
        'special-defense': 1,
        'speed': 1
    }

    def_mods = {}

    attack = pb.move('work-up')
    atk_mods, def_mods = changeStats(atk_mods, def_mods, attack)

    #  make sure stat modifiers do not go beyond 4x
    if atk_mods['attack'] != 4 or atk_mods['special-attack'] != 4:
        raise ValueError('stats can\'t be raised past 4x!')


"""Tests lowering the opponent's stats.
"""
def testLowerStats():
    def_mods = {
        'attack': 1,
        'defense': 1,
        'special-attack': 1,
        'special-defense': 1,
        'speed': 1
    }

    atk_mods = {}

    attack = pb.move('tail-whip')
    atk_mods, def_mods = changeStats(atk_mods, def_mods, attack)

    #  make sure stat modifiers are updated appropriately
    if def_mods['defense'] != 0.67
        raise ValueError('stats weren\'t lowered correctly!')

    attack = pb.move('screech')
    atk_mods, def_mods = changeStats(atk_mods, def_mods, attack)

    #  make sure stat modifiers are updated appropriately
    if def_mods['defense'] != 0.4
        raise ValueError('stats weren\'t lowered correctly!')


"""Tests failing to lower the opponent's stats.
"""
def testLowerStatsFail():
    def_mods = {
        'attack': 1,
        'defense': 0.25,
        'special-attack': 1,
        'special-defense': 1,
        'speed': 1
    }

    atk_mods = {}

    attack = pb.move('tail-whip')
    atk_mods, def_mods = changeStats(atk_mods, def_mods, attack)

    #  make sure stat modifiers do not go beyond 4x
    if def_mods['defense'] != 0.25:
        raise ValueError('stats can\'t be lowered past 0.25x!')


"""Run as a program to execute tests. This file will test the capabilities
of the changeStats function.
"""
if __name__ == '__main__':

    #  test raising the user's stats
    testRaiseStats()

    #  test failing to raise the user's stats
    testRaiseStatsFail()

    #  test lowering the opponent's stats
    testLowerStats()

    #  test failing to lower the opponent's stats
    testLowerStatsFail()
