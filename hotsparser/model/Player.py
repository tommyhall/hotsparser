

class Player(object):

    def __init__(self, name, hero, team, id, winner):
        self._name = name
        self._hero = hero
        self._team = team
        self._id = id
        self._talents = None
        self._winner = winner

    def __str__(self):
        return """{0} {1} {2} {3} {4}""".format(
            self._name,
            self._hero,
            self._team,
            self._id,
            self._winner
        )

    @property
    def name(self):
        return self._name

    @property
    def hero(self):
        return self._hero

    @property
    def team(self):
        return self._team

    @property
    def id(self):
        return self._id

    @property
    def winner(self):
        return self._winner

    def set_talents(self, talents):
        self._talents = list(talents)

    def get_talents(self):
        return self._talents
