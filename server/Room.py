class Player:
    def __init__(self, sid, username, team):
        self.sid = sid
        self.username = username
        self.team = team
        self.actionUsed = False

class Room:
    def __init__(self):
        self.players = []
        self.battle = {}

    def get_player_names(self):
        return [n.username for n in self.players]

    def is_full(self):
        return len(self.players) == 2
