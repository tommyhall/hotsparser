import os
import pandas as pd
from hotsparser.DataParser import DataParser
from hotsparser.Enums import TalentChoice


# Create a pandas dataframe that we're going to fill out
columns = [
    'replay',
    'build',
    'map',
    'team_0',
    'team_1',
    'winner',
    'first_catapult',
    'tier_1','tier_2','tier_3','tier_4','tier_5','tier_6',
]
df = pd.DataFrame(columns=columns)

# Get the list of replays we're going to be mining
replays_path = os.path.join(os.getcwd(),'replays')
replays = []
for (dirpath, dirnames, filenames) in os.walk(replays_path):
    replays.extend(filenames)
    break

data_parser = DataParser()

for replay in replays:
    filename = os.path.join(replays_path, replay)

    print "\nAttempting to parse \'{0}\'".format(replay)
    replay = data_parser.parse_replay(filename)

    if not replay:
        print "Error! (moving on)"
        continue

    winner_id = replay.get_winning_team_id()
    loser_id = replay.get_losing_team_id()

    # The first team to gain a catapult (destroy a keep)
    first_catapult_team_id = replay.first_catapult_team_id

    # Get the two teams as well as who won/lost
    winning_team = replay.get_winning_team()
    losing_team = replay.get_losing_team()
    team_0 = [p.hero for p in replay.get_team_0()]
    team_1 = [p.hero for p in replay.get_team_1()]

    # Find which team was first to each talent tier, save in dict
    first_to_tier_dict = {}
    talent_tiers = [1,2,3,4,5,6]  # these correspond to levels 4,7,10,13,16,20
    for tier in talent_tiers:
        losing_t = min(p.get_talents()[tier][TalentChoice.TIME] for p in losing_team)
        winning_t = min(p.get_talents()[tier][TalentChoice.TIME] for p in winning_team)
        # If neither team reached this tier, return None (NaN)
        if losing_t is None and winning_t is None:
            first_to_tier_dict[tier] = None
        else:
            first_to_tier = winner_id if (winning_t < losing_t) else loser_id
            first_to_tier_dict[tier] = first_to_tier

    # Append what we've learned to our dataframe
    df = df.append({
        'replay': os.path.basename(filename),
        'build': str(replay.build),
        'map': replay.map_name,
        'team_0': team_0,
        'team_1': team_1,
        'winner': winner_id,
        'first_catapult': first_catapult_team_id,
        'tier_1': first_to_tier_dict[1],
        'tier_2': first_to_tier_dict[2],
        'tier_3': first_to_tier_dict[3],
        'tier_4': first_to_tier_dict[4],
        'tier_5': first_to_tier_dict[5],
        'tier_6': first_to_tier_dict[6]
        }, ignore_index=True)

    print "Done!"

# Write to disk
filepath = os.path.join(os.getcwd(),'replay_output.csv')
df.to_csv(filepath, sep=';')
