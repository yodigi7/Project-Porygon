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


"""Performs an attack using the stats of the passed Pokémon.

For now, we only need to care about attacks that deal damage.
Don't worry about status effects, effect chances, etc.

General outline:
Given the UUID of the Pokémon, find the UUID of the team it belongs 
to, then load the appropriate team JSON, find the corresponding 
attack name, look up the attack data with Pokébase as well as the 
attacking/defending Pokémon data and then calculate damage dealt. 
Don't forget to take accuracy into account, don't forget to 
convert the HP to a percentage and don't forget to add the used 
move to the 'used_moves' list in the JSON file. Phew.

Parameters:
atk_index -- a number from 0 to 3 that indicates the selected move
poke_id -- a UUID representing the attacking Pokémon
"""
def attack(atk_index, poke_id):
    pass


"""Switches a Pokémon into the active slot for a team.

General outline:
This one should be easy; just swap the values between the 
designated backup Pokémon and the current active Pokémon.
Remember that a freshly swapped-in Pokémon is not confused, 
does not have any Perish Song counts, and has no stat modifiers.

This one should return an error if the Pokémon with the corresponding 
poke_id is already active.

Parameters:
team_id, poke_id -- strings representing UUIDs used to identify teams/Pokémon
"""
def switch(team_id, poke_id):
    pass
