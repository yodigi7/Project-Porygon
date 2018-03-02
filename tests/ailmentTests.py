"""Some simple unit tests. I should probably be using pytest for this,
but doing it this way means no additional installs.
"""
import sys
sys.path.append('../')

import pokebase as pb
from server import pokeutils as pk

"""Tests the infliction of poison.
"""
def testPoison(atk_poke, def_poke):
    attack = pb.move(atk_poke['moves'][0])

    #  make sure it connects
    attack.accuracy = 100
    ailment = pk.applyStatus(atk_poke, def_poke, attack)

    #  if applyStatus did not return 'poison,' something's wrong
    if ailment != 'poison':
        raise ValueError('applyStatus didn\'t apply poison!')


"""Tests the infliction of toxic.
"""
def testToxic(atk_poke, def_poke):
    attack = pb.move(atk_poke['moves'][0])

    #  make sure it connects
    attack.accuracy = 100
    ailment = pk.applyStatus(atk_poke, def_poke, attack)

    #  if applyStatus did not return 'poison,' something's wrong
    if ailment != 'toxic':
        raise ValueError('applyStatus didn\'t apply toxic!')


"""Tests poison immunities.
"""
def testPoisonFail(atk_poke, def_poke):
    attack = pb.move(atk_poke['moves'][0])

    #  make sure it connects
    attack.accuracy = 100
    ailment = pk.applyStatus(atk_poke, def_poke, attack)

    #  if applyStatus returned anything, something's wrong
    if ailment != 'none':
        raise ValueError('applyStatus applies poison when it shouldn\'t!')


"""Tests the infliction of paralysis.
"""
def testParalysis(atk_poke, def_poke):
    attack = pb.move(atk_poke['moves'][0])

    #  make sure it connects
    attack.accuracy = 100
    ailment = pk.applyStatus(atk_poke, def_poke, attack)

    #  if applyStatus did not return 'paralysis,' something's wrong
    if ailment != 'paralysis':
        raise ValueError('applyStatus didn\'t apply paralysis!')


"""Tests paralysis immunities.
"""
def testParalysisFail(atk_poke, def_poke):
    attack = pb.move(atk_poke['moves'][0])

    #  make sure it connects
    attack.accuracy = 100
    ailment = pk.applyStatus(atk_poke, def_poke, attack)

    #  if applyStatus returned anything, something's wrong
    if ailment != 'none':
        raise ValueError('applyStatus applies paralysis when it shouldn\'t!')


"""Tests the infliction of burn.
"""
def testBurn(atk_poke, def_poke):
    attack = pb.move(atk_poke['moves'][0])

    #  make sure it connects
    attack.accuracy = 100
    ailment = pk.applyStatus(atk_poke, def_poke, attack)

    #  if applyStatus did not return 'burn,' something's wrong
    if ailment != 'burn':
        raise ValueError('applyStatus didn\'t apply burn!')


"""Tests burn immunities.
"""
def testBurnFail(atk_poke, def_poke):
    attack = pb.move(atk_poke['moves'][0])

    #  make sure it connects
    attack.accuracy = 100
    ailment = pk.applyStatus(atk_poke, def_poke, attack)

    #  if applyStatus returned anything, something's wrong
    if ailment != 'none':
        raise ValueError('applyStatus applies burn when it shouldn\'t!')


"""Tests the infliction of freeze.
"""
def testFreeze(atk_poke, def_poke):
    attack = pb.move(atk_poke['moves'][0])

    #  make sure it connects
    attack.accuracy = 100
    
    #  make sure it freezes
    attack.meta.ailment_chance = 100
    ailment = pk.applyStatus(atk_poke, def_poke, attack)

    #  if applyStatus did not return 'freeze,' something's wrong
    if ailment != 'freeze':
        raise ValueError('applyStatus didn\'t apply freeze!')


"""Tests freeze immunities.
"""
def testFreezeFail(atk_poke, def_poke):
    attack = pb.move(atk_poke['moves'][0])

    #  make sure it connects
    attack.accuracy = 100

    #  make sure it tries to freeze
    attack.meta.ailment_chance = 100
    ailment = pk.applyStatus(atk_poke, def_poke, attack)

    #  if applyStatus returned anything, something's wrong
    if ailment != 'none':
        raise ValueError('applyStatus applies freeze when it shouldn\'t!')


"""Tests the infliction of sleep.
"""
def testSleep(atk_poke, def_poke):
    attack = pb.move(atk_poke['moves'][0])

    #  make sure it connects
    attack.accuracy = 100
    ailment = pk.applyStatus(atk_poke, def_poke, attack)

    #  if applyStatus didn't return 'sleep,' something's wrong
    if ailment != 'sleep':
        raise ValueError('applyStatus didn\'t apply sleep!')


"""Tests the infliction of confusion.
"""
def testConfusion(atk_poke, def_poke):
    attack = pb.move(atk_poke['moves'][0])

    #  make sure it connects
    attack.accuracy = 100
    ailment = pk.applyStatus(atk_poke, def_poke, attack)

    #  if applyStatus did not return 'confusion,' something's wrong
    if ailment != 'confusion':
        raise ValueError('applyStatus didn\'t apply confusion!')


"""Run as a program to execute tests. This file will test the capabilities
of the applyStatus function.
"""
if __name__ == '__main__':

    #  these pokemon are not necessarily legal, but that shouldn't be
    #  an issue for these tests
    atk_poke = {
        "name": "slimy boy",
        "species": "grimer",
        "poke_id": "325cff49-3e69-4c23-9a63-b0552e2f4a87",
        "nature": "bold",
        "ability": "stench",
        "item": "eviolite",
        "level": 50,
        "ivalues": {
            "hp": 0,
            "attack": 17,
            "defense": 25,
            "special-attack": 31,
            "special-defense": 31,
            "speed": 28
        },
        "evalues": {
            "hp": 252,
            "defense": 128,
            "special-defense": 128
        },
        "moves": [
            "poison-gas"
        ]
    }

    def_poke = {
        "name": "cutie",
        "species": "caterpie",
        "poke_id": "a1c33278-c5f8-4c6a-b992-a162fd329b40",
        "nature": "bold",
        "ability": "shield-dust",
        "item": "eviolite",
        "level": 50,
        "ivalues": {
            "hp": 0,
            "attack": 17,
            "defense": 25,
            "special-attack": 31,
            "special-defense": 31,
            "speed": 28
        },
        "evalues": {
            "hp": 252,
            "defense": 128,
            "special-defense": 128
        },
        "moves": [
            "tackle"
        ]
    }


    """Test the infliction of status ailments."""

    #  test infliction of poison
    testPoison(atk_poke, def_poke)

    #  test steel and poision immunity
    def_poke['species'] = 'magnemite'
    testPoisonFail(atk_poke, def_poke)
    def_poke['species'] = 'grimer'
    testPoisonFail(atk_poke, def_poke)

    #  test infliction of toxic
    def_poke['species'] = 'eevee'
    atk_poke['moves'][0] = 'toxic'
    testToxic(atk_poke, def_poke)


    #  test infliction of paralysis
    atk_poke['moves'][0] = 'thunder-wave'
    testParalysis(atk_poke, def_poke)

    #  test electric immunity
    def_poke['species'] = 'pikachu'
    testParalysisFail(atk_poke, def_poke)


    #  test infliction of burn
    atk_poke['moves'][0] = 'will-o-wisp'
    testBurn(atk_poke, def_poke)

    #  test fire immunity
    def_poke['species'] = 'growlithe'
    testBurnFail(atk_poke, def_poke)


    #  test infliction of freeze
    atk_poke['moves'][0] = 'ice-beam'
    testFreeze(atk_poke, def_poke)

    #  test freeze immunity
    def_poke['species'] = 'lapras'
    testFreezeFail(atk_poke, def_poke)


    #  test infliction of sleep
    atk_poke['moves'][0] = 'hypnosis'
    testSleep(atk_poke, def_poke)


    #  test infliction of confusion
    atk_poke['moves'][0] = 'confuse-ray'
    testConfusion(atk_poke, def_poke)
