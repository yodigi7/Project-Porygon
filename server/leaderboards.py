import pokeutils as pk

DEFUALT_WIN = 0
DEFAULT_LOSS = 0
DATA_FILE = "leaderboardData.json"
L = pk.load_from_file(DATA_FILE)


def add_user(username):
    if username not in L:
        L[username] = {'wins': 0, 'losses': 0}
        pk.save_to_file(L, DATA_FILE)
    return True

def on_win(username):
    if username in L:
        L[username]['wins'] += 1
        pk.save_to_file(L, DATA_FILE)
        update_ranks()

def on_loss(username):
    if username in L:
        L[username]['losses'] += 1
        pk.save_to_file(L, DATA_FILE)
        update_ranks()


#Wins/(Wins+Losses)
def rank_formula(username):
    if username in L:
        return round(L[username]['wins']/(L[username]['wins'] + L[username]['losses']), 2)

#Sorts the json by rank
def update_ranks():
    #Ranks start at 1
    counter = 1

    #Sorted by rank_formula
    for username in sorted(L, key=lambda x: rank_formula(x), reverse=True):
        L[username]['rank'] = counter
        counter += 1

    #Updates the file
    pk.save_to_file(L, DATA_FILE)