import sys
import logging
from importlib import import_module

from collections import defaultdict
from mpyq import MPQArchive
# Import the latest protocol version to start
from heroprotocol import protocol46889 as protocol

from model.Replay import Replay
from model.Player import Player


class DataParser(object):

    def __init__(self):
        self._protocol = protocol
        logging.basicConfig(filename='data_parser_log.log', level=logging.INFO)
        logging.info("Data Parser created.")
        logging.info("--------------------")

    def parse_replay(self, filename):
        """
        Given a Heroes of the Storm replay file (mpq archive), parses the file
        and returns a Replay object.
        """
        try:
            logging.info("Attempting to parse replay: {}".format(filename))
            mpq = MPQArchive(filename)
            replay = Replay()
            return self._parse_replay(replay, mpq)
        except Exception, e:
            logging.error("Something went wrong with replay {}".format(filename))
            logging.error("{0}\n{1}".format(str(e),repr(e)))
            return None

    def _import_protocol(self, build_number):
        """
        Given a build, imports the correct protocol (if it hasn't been imported
        already), and sets as _protocol attribute.
        """
        module_name = 'heroprotocol.protocol{0}'.format(build_number)
        self._protocol = import_module(module_name)

    def _parse_replay(self, replay, mpq):
        """
        This does the actual parsing work.
        """
        # Get the HotS build and import the correct protocol
        header = self._protocol.decode_replay_header(mpq.header['user_data_header']['content'])
        replay.build = header['m_version']['m_baseBuild']
        self._import_protocol(replay.build)

        details = self._protocol.decode_replay_details(mpq.read_file('replay.details'))
        replay.map_name = details['m_title']
        replay.players = self._get_players(details)

        # -- TRACKER EVENTS --
        tracker_events = self._protocol.decode_replay_tracker_events(mpq.read_file('replay.tracker.events'))
        # TODO: In future, could create a list of town halls for teams 0 and 1
        #town_halls = {0:[], 1:[]}
        # Create a dict of {player_id -> [talent_choices]}
        talent_choices = defaultdict(list)
        for tracker_event in tracker_events:

            # Get the talent choices of the players (never used in this version)
            if tracker_event['_event'] == 'NNet.Replay.Tracker.SStatGameEvent':
                # TODO: This tracker event type is not present in all protocols
                if tracker_event['m_eventName'] == 'EndOfGameTalentChoices':
                    # We have to adjust players IDs by 1 for some reason
                    player_id = tracker_event['m_intData'][0]['m_value'] - 1
                    string_data = tracker_event['m_stringData']
                    for i in xrange(3,len(string_data)):
                        talent_choices[player_id].append(string_data[i]['m_value'])

            # Get town halls (forts and keeps), catapult minion
            elif tracker_event['_event'] == 'NNet.Replay.Tracker.SUnitBornEvent':
                if tracker_event['m_unitTypeName'] in ['TownTownHallL3', 'TownTownHallL2']:
                    pass  # TODO: May do something with this in later version

                # Get the time the first catapult spawns
                elif tracker_event['m_unitTypeName'] == 'CatapultMinion':
                    first_catapult_gameloop = tracker_event['_gameloop']
                    replay.first_catapult_time = first_catapult_gameloop / 16.0
                    # For some reason player control IDs are 11 and 12 now
                    if tracker_event['m_controlPlayerId'] == 12:
                        replay.first_catapult_team_id = 1
                    else:
                        replay.first_catapult_team_id = 0

            # TODO: May do something with this in later version
            # # Get info on when town halls were destroyed
            # elif tracker_event['_event'] == 'NNet.Replay.Tracker.SUnitDiedEvent':
            #     if tracker_event['m_unitTagIndex'] in town_hall_ids:
            #         pass

            game_loop = tracker_event['_gameloop']

        # Convert the length of the game into seconds
        match_length_game_loops = game_loop
        replay.match_length_seconds = match_length_game_loops / 16.0

        # -- GAME EVENTS --
        game_events = self._protocol.decode_replay_game_events(mpq.read_file('replay.game.events'))
        # We'll create a dict of {player_id -> [talent_times]}
        talent_times = defaultdict(list)
        for event in game_events:
            # Get talent selection times
            if event['_event'] == 'NNet.Game.SHeroTalentTreeSelectedEvent':
                player_id = event['_userid']['m_userId']
                selection_time = event['_gameloop'] / 16.0
                talent_times[player_id].append(selection_time)

        # There appears to be an issue where, in certain replays, the player
        # IDs of the talent selection events do not match the players IDs
        # themselves. In some these cases, only one ID is mismatched, in which
        # case we can easily deduce which player's talents are missing and do
        # a repair. However, if more than one player's talents are missing, it's
        # much more difficult to do this, so for now we're just going to bail
        # on parsing such replays.
        #
        # My guess is that this is due to the presence of observers in the game,
        # but I'm not sure of the exact cause.
        player_ids = set([player.id for player in replay.players])
        talent_ids = set(talent_times.keys())
        p_ids_missing = player_ids - talent_ids
        t_ids_missing = talent_ids - player_ids
        if len(p_ids_missing) == 1:
            logging.info("\tWe have an ID mismatch between Player IDs and Talent Selection IDs.")
            logging.info("\tAttempting repair...")
            talent_id = next(iter(t_ids_missing))
            player_id = next(iter(p_ids_missing))
            talent_times[player_id] = talent_times.pop(talent_id)
            logging.info("\tdone")
        elif len(p_ids_missing)> 1:
            logging.error("\tThere is a talent ID mismatch with 2 or more players!")
            logging.error("\t(Cannot repair, returning None)")
            return None

        for player_id in talent_times.iterkeys():
            player = next(player for player in replay.players if player_id == player.id)
            talents = []
            for time in talent_times[player_id]:
                # We no longer have the actual talent choice (id issue)
                talents.append((None,time))
            # If they didn't get to level 20, just append None
            while len(talents) < 7:
                talents.append((None,None))
            player.set_talents(talents)

        return replay

    def _get_players(self, details):
        """
        Get all of the player names, heroes, IDs, team affiliation, and win/loss.
        """
        parsed_players = []
        players = details['m_playerList']
        for player in players:
            name = player['m_name']
            hero = player['m_hero']
            team_id = player['m_teamId']
            working_slot_id = player['m_workingSetSlotId']
            result = player['m_result']
            parsed_player = Player(
                name=name,
                hero=hero,
                team=team_id,
                id=working_slot_id,
                winner=(result==1),
            )
            parsed_players.append(parsed_player)
        return parsed_players
