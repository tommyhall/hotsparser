

class Replay(object):

    def __init__(self):
        self._build = None
        self._map_name = None
        self._players = None
        self._match_length_seconds = None
        self._first_catapult_time = None  # the time (s) of the first catapult
        self._first_catapult_team_id = None  # the team with the first catapult

    @property
    def build(self):
        return self._build

    @build.setter
    def build(self, build):
        self._build = build

    @property
    def map_name(self):
        return self._map_name

    @map_name.setter
    def map_name(self, map_name):
        self._map_name = map_name

    @property
    def players(self):
        return self._players

    @players.setter
    def players(self, players):
        self._players = list(players)

    @property
    def match_length_seconds(self):
        return self._match_length_seconds

    @match_length_seconds.setter
    def match_length_seconds(self, match_length_seconds):
        self._match_length_seconds = match_length_seconds

    @property
    def first_catapult_time(self):
        return self._first_catapult_time

    @first_catapult_time.setter
    def first_catapult_time(self, first_catapult_time):
        self._first_catapult_time = first_catapult_time

    @property
    def first_catapult_team_id(self):
        return self._first_catapult_team_id

    @first_catapult_team_id.setter
    def first_catapult_team_id(self, first_catapult_team_id):
        self._first_catapult_team_id = first_catapult_team_id

    def print_replay(self):
        print """
    Build: {0}
    Map: {1}
    Match length (s): {2}
    First catapult (s): {3}
    Players: {4}
    Winning team ID: {5}
    First catapult team ID: {6}
        """.format(self._build,
            self._map_name,
            self._match_length_seconds,
            self._first_catapult_time,
            '\n\t'.join(map(str,self._players)),
            self.get_winning_team_id(),
            self._first_catapult_team_id)

    def get_winning_team(self):
        """ Get the team that won. Returns a list of Player objects. """
        if hasattr(self, '_winning_team'):
            return self._winning_team
        self._winning_team = [player for player in self._players if player.winner is True]
        return self._winning_team

    def get_losing_team(self):
        """ Get the team that lost. Returns a list of Player objects. """
        if hasattr(self, '_losing_team'):
            return self._losing_team
        self._losing_team = [player for player in self._players if player.winner is False]
        return self._losing_team

    def get_winning_team_id(self):
        if hasattr(self, '_winning_team_id'):
            return self._winning_team_id
        player = next(player for player in self._players if player.winner is True)
        self._winning_team_id = player.team
        return self._winning_team_id

    def get_losing_team_id(self):
        if hasattr(self, '_losing_team_id'):
            return self._losing_team_id
        player = next(player for player in self._players if player.winner is False)
        self._losing_team_id = player.team
        return self._losing_team_id

    def get_team_0(self):
        """ Return the team with id=0 """
        team_0 = [player for player in self._players if player.team == 0]
        return team_0

    def get_team_1(self):
        """ Return the team with id=1 """
        team_1 = [player for player in self._players if player.team == 1]
        return team_1
