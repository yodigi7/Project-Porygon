"""
Unit Tests for Abilities
"""
import sys
sys.path.append('../')

import pokebase as pb
import pokeutils as pk

"""Test Serene Grace
"""
def test_Serene_Grace(atk_poke, def_poke):
    atk_mods = {
        'attack': 1,
        'defense': 1,
        'special-attack': 1,
        'special-defense': 1,
        'speed': 1,
        'accuracy': 0,
        'evasion': 0
    }

    def_mods = {
        'attack': 1,
        'defense': 1,
        'special-attack': 1,
        'special-defense': 1,
        'speed': 1,
        'accuracy': 0,
        'evasion': 0
    }

    # Make sure Serene Grace guarantees a defense drop from rock smash
    attack = pb.move('rock-smash')
    atk_mods, def_mods = pk.changeStats(atk_poke, def_poke, atk_mods, def_mods, attack)
    if def_mods['defense'] != 0.67:
        raise ValueError('Defense not lowered!')
    # Make sure Serene Grace guarantees a burn from Sacred Fire
    attack = pb.move('sacred-fire')
    attack.accuracy = 100
    ailment = pk.applyStatus(atk_poke, def_poke, attack)
    if ailment != 'burn':
        raise ValueError('Burn not inflicted!')
    # Make sure Serene Grace guarantees a special attack boost from charge beam
    attack = pb.move('charge-beam')
    atk_mods, def_mods = pk.changeStats(atk_poke, def_poke, atk_mods, def_mods, attack)
    if atk_mods['special-attack'] != 1.5:
        raise ValueError('Special attack not raised!')

"""Test Hyper Cutter
"""
def test_Hyper_Cutter(atk_poke, def_poke):
    atk_mods = {
        'attack': 1,
        'defense': 1,
        'special-attack': 1,
        'special-defense': 1,
        'speed': 1,
        'accuracy': 0,
        'evasion': 0
    }

    def_mods = {
        'attack': 1,
        'defense': 1,
        'special-attack': 1,
        'special-defense': 1,
        'speed': 1,
        'accuracy': 0,
        'evasion': 0
    }

    attack = pb.move('feather-dance')
    atk_mods, def_mods = pk.changeStats(atk_poke, def_poke, atk_mods, def_mods, attack)
    if def_mods['attack'] != 1:
        raise ValueError('Hyper cutter should prevent attack drops!')

"""Test Big Pecks
"""
def test_Big_Pecks(atk_poke, def_poke):
    atk_mods = {
        'attack': 1,
        'defense': 1,
        'special-attack': 1,
        'special-defense': 1,
        'speed': 1,
        'accuracy': 0,
        'evasion': 0
    }

    def_mods = {
        'attack': 1,
        'defense': 1,
        'special-attack': 1,
        'special-defense': 1,
        'speed': 1,
        'accuracy': 0,
        'evasion': 0
    }

    attack = pb.move('leer')
    atk_mods, def_mods = pk.changeStats(atk_poke, def_poke, atk_mods, def_mods, attack)
    if def_mods['defense'] != 1:
        raise ValueError('Big Pecks should prevent defense drops!')

"""Test Keen Eye
"""
def test_Keen_Eye(atk_poke, def_poke):
    atk_mods = {
        'attack': 1,
        'defense': 1,
        'special-attack': 1,
        'special-defense': 1,
        'speed': 1,
        'accuracy': 0,
        'evasion': 0
    }

    def_mods = {
        'attack': 1,
        'defense': 1,
        'special-attack': 1,
        'special-defense': 1,
        'speed': 1,
        'accuracy': 0,
        'evasion': 0
    }

    attack = pb.move('sand-attack')
    atk_mods, def_mods = pk.changeStats(atk_poke, def_poke, atk_mods, def_mods, attack)
    if def_mods['accuracy'] != 0:
        raise ValueError('Keen Eye should prevent accuracy drops!')

"""Test Clear Body
"""
def test_Clear_Body(atk_poke, def_poke):
    atk_mods = {
        'attack': 1,
        'defense': 1,
        'special-attack': 1,
        'special-defense': 1,
        'speed': 1,
        'accuracy': 0,
        'evasion': 0
    }

    def_mods = {
        'attack': 1,
        'defense': 1,
        'special-attack': 1,
        'special-defense': 1,
        'speed': 1,
        'accuracy': 0,
        'evasion': 0
    }

    attack = pb.move('growl')
    atk_mods, def_mods = pk.changeStats(atk_poke, def_poke, atk_mods, def_mods, attack)
    if def_mods['attack'] != 1:
        raise ValueError('Clear Body should prevent attack drops!')

    attack = pb.move('leer')
    atk_mods, def_mods = pk.changeStats(atk_poke, def_poke, atk_mods, def_mods, attack)
    if def_mods['defense'] != 1:
        raise ValueError('Clear Body should prevent defense drops!')

    attack = pb.move('confide')
    atk_mods, def_mods = pk.changeStats(atk_poke, def_poke, atk_mods, def_mods, attack)
    if def_mods['special-attack'] != 1:
        raise ValueError('Clear Body should prevent special attack drops!')

    attack = pb.move('metal-sound')
    atk_mods, def_mods = pk.changeStats(atk_poke, def_poke, atk_mods, def_mods, attack)
    if def_mods['special-defense'] != 1:
        raise ValueError('Clear Body should prevent special defense drops!')

    attack = pb.move('scary-face')
    atk_mods, def_mods = pk.changeStats(atk_poke, def_poke, atk_mods, def_mods, attack)
    if def_mods['speed'] != 1:
        raise ValueError('Clear Body should prevent speed drops!')

    attack = pb.move('sand-attack')
    atk_mods, def_mods = pk.changeStats(atk_poke, def_poke, atk_mods, def_mods, attack)
    if def_mods['accuracy'] != 0:
        raise ValueError('Clear Body should prevent accuracy drops!')

    attack = pb.move('sweet-scent')
    atk_mods, def_mods = pk.changeStats(atk_poke, def_poke, atk_mods, def_mods, attack)
    if def_mods['evasion'] != 0:
        raise ValueError('Clear Body should prevent evasion drops!')

"""Test Defiant
"""
def test_Defiant(atk_poke, def_poke):
    atk_mods = {
        'attack': 1,
        'defense': 1,
        'special-attack': 1,
        'special-defense': 1,
        'speed': 1,
        'accuracy': 0,
        'evasion': 0
    }

    def_mods = {
        'attack': 2,
        'defense': 1,
        'special-attack': 1,
        'special-defense': 1,
        'speed': 0.25,
        'accuracy': 0,
        'evasion': 0
    }

    attack = pb.move('feather-dance')
    atk_mods, def_mods = pk.changeStats(atk_poke, def_poke, atk_mods, def_mods, attack)
    if def_mods['attack'] != 2:
        raise ValueError('Defiant should raise attack by 2 stages after it is lowered!')

    attack = pb.move('parting-shot')
    atk_mods, def_mods = pk.changeStats(atk_poke, def_poke, atk_mods, def_mods, attack)
    if def_mods['attack'] != 3.5:
        raise ValueError('Defiant should raise attack by 2 stages for each stat lowered!')

    attack = pb.move('string-shot')
    atk_mods, def_mods = pk.changeStats(atk_poke, def_poke, atk_mods, def_mods, attack)
    if def_mods['attack'] != 3.5:
        raise ValueError('Defiant should not raise attack if a stat can\'t be lowered!')

    attack = pb.move('confide')
    atk_mods, def_mods = pk.changeStats(atk_poke, def_poke, atk_mods, def_mods, attack)
    if def_mods['attack'] != 4:
        raise ValueError('Defiant should not raise attack past 4x!')

"""Test Competitive
"""
def test_Competitive(atk_poke, def_poke):
    atk_mods = {
        'attack': 1,
        'defense': 1,
        'special-attack': 1,
        'special-defense': 1,
        'speed': 1,
        'accuracy': 0,
        'evasion': 0
    }

    def_mods = {
        'attack': 1,
        'defense': 1,
        'special-attack': 2,
        'special-defense': 1,
        'speed': 0.25,
        'accuracy': 0,
        'evasion': 0
    }

    attack = pb.move('eerie-impulse')
    atk_mods, def_mods = pk.changeStats(atk_poke, def_poke, atk_mods, def_mods, attack)
    if def_mods['special-attack'] != 2:
        raise ValueError('Competitive should raise special attack by 2 stages after it is lowered!')

    attack = pb.move('parting-shot')
    atk_mods, def_mods = pk.changeStats(atk_poke, def_poke, atk_mods, def_mods, attack)
    if def_mods['special-attack'] != 3.5:
        raise ValueError('Competitive should raise special attack by 2 stages for each stat lowered!')

    attack = pb.move('string-shot')
    atk_mods, def_mods = pk.changeStats(atk_poke, def_poke, atk_mods, def_mods, attack)
    if def_mods['special-attack'] != 3.5:
        raise ValueError('Competitive should not raise special attack if a stat can\'t be lowered!')

    attack = pb.move('growl')
    atk_mods, def_mods = pk.changeStats(atk_poke, def_poke, atk_mods, def_mods, attack)
    if def_mods['special-attack'] != 4:
        raise ValueError('Competitive should not raise special attack past 4x!')

"""Test Immunity
"""
def test_Immunity(atk_poke, def_poke):
    attack = pb.move('toxic')
    ailment = pk.applyStatus(atk_poke, def_poke, attack)
    if ailment != 'none':
        raise ValueError('Immunity should prevent poison!')

"""Test Water Veil
"""
def test_Water_Veil(atk_poke, def_poke):
    attack = pb.move('will-o-wisp')
    ailment = pk.applyStatus(atk_poke, def_poke, attack)
    if ailment != 'none':
        raise ValueError('Water Veil should prevent burn!')

"""Test Limber
"""
def test_Limber(atk_poke, def_poke):
    attack = pb.move('glare')
    ailment = pk.applyStatus(atk_poke, def_poke, attack)
    if ailment != 'none':
        raise ValueError('Limber should prevent paralysis!')

"""Test Magma Armor
"""
def test_Magma_Armor(atk_poke, def_poke):
    attack = pb.move('ice-beam')
    attack.meta.ailment_chance = 100
    ailment = pk.applyStatus(atk_poke, def_poke, attack)
    if ailment != 'none':
        raise ValueError('Magma Armor should prevent freeze!')

"""Test Insomnia
"""
def test_Insomnia(atk_poke, def_poke):
    attack = pb.move('spore')
    ailment = pk.applyStatus(atk_poke, def_poke, attack)
    if ailment != 'none':
        raise ValueError('Insomnia should prevent sleep!')

""" Test Vital Spirit
"""
def test_Vital_Spirit(atk_poke, def_poke):
    attack = pb.move('spore')
    ailment = pk.applyStatus(atk_poke, def_poke, attack)
    if ailment != 'none':
        raise ValueError('Vital Spirit should prevent sleep!')

""" Test Own Tempo
"""
def test_Own_Tempo(atk_poke, def_poke):
    attack = pb.move('confuse-ray')
    ailment = pk.applyStatus(atk_poke, def_poke, attack)
    if ailment != 'none':
        raise ValueError('Own Tempo should prevent confusion!')

""" Test Overcoat
"""
def test_Overcoat(atk_poke, def_poke):
    attack = pb.move('spore')
    ailment = pk.applyStatus(atk_poke, def_poke, attack)
    if ailment != 'none':
        raise ValueError('Overcoat should prevent status from powder moves!')

    attack = pb.move('stun-spore')
    ailment = pk.applyStatus(atk_poke, def_poke, attack)
    if ailment != 'none':
        raise ValueError('Overcoat should prevent status from powder moves!')

    attack = pb.move('sleep-powder')
    ailment = pk.applyStatus(atk_poke, def_poke, attack)
    if ailment != 'none':
        raise ValueError('Overcoat should prevent status from powder moves!')

    attack = pb.move('poison-powder')
    ailment = pk.applyStatus(atk_poke, def_poke, attack)
    if ailment != 'none':
        raise ValueError('Overcoat should prevent status from powder moves!')


"""Run as a program to execute tests. This file will test the capabilities
of the applyStatus function.
"""
if __name__ == '__main__':

    #  these pokemon are not necessarily legal, but that shouldn't be
    #  an issue for these tests
    atk_poke = {
        "name": "wishy",
        "species": "jirachi",
        "poke_id": "325cff49-3e69-4c23-9a63-b0552e2f4a87",
        "nature": "bold",
        "ability": "serene-grace",
        "item": "eviolite",
        "level": 50,
        "ivalues": {
            "hp": 31,
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
            "rock-smash",
            "charge-beam",
            "sacred-fire"
        ]
    }

    def_poke = {
        "name": "smogon",
        "species": "koffing",
        "poke_id": "a1c33278-c5f8-4c6a-b992-a162fd329b40",
        "nature": "bold",
        "ability": "levitate",
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
            "explosion"
        ]
    }

    test_Serene_Grace(atk_poke, def_poke)

    def_poke['ability'] = 'hyper-cutter'
    test_Hyper_Cutter(atk_poke, def_poke)

    def_poke['ability'] = 'big-pecks'
    test_Big_Pecks(atk_poke, def_poke)

    def_poke['ability'] = 'keen-eye'
    test_Keen_Eye(atk_poke, def_poke)

    def_poke['ability'] = 'clear-body'
    test_Clear_Body(atk_poke, def_poke)

    def_poke['ability'] = 'defiant'
    test_Defiant(atk_poke, def_poke)

    def_poke['ability'] = 'competitive'
    test_Competitive(atk_poke, def_poke)

    def_poke['species'] = 'snorlax'
    def_poke['ability'] = 'immunity'
    test_Immunity(atk_poke, def_poke)

    def_poke['ability'] = 'water-veil'
    test_Water_Veil(atk_poke, def_poke)

    def_poke['ability'] = 'limber'
    test_Limber(atk_poke, def_poke)

    def_poke['ability'] = 'magma-armor'
    test_Magma_Armor(atk_poke, def_poke)

    def_poke['ability'] = 'insomnia'
    test_Insomnia(atk_poke, def_poke)

    def_poke['ability'] = 'vital-spirit'
    test_Vital_Spirit(atk_poke, def_poke)

    def_poke['ability'] = 'own-tempo'
    test_Own_Tempo(atk_poke, def_poke)

    def_poke['ability'] = 'overcoat'
    test_Overcoat(atk_poke, def_poke)
