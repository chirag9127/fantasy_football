import csv
import json


team_conversion = {
    'SF': 'SFO',
    'TB': 'TBB',
    'SD': 'SDC',
    'LA': 'LAR',
    'KC': 'KCC',
    'GB': 'GBP',
    'NO': 'NOS',
    'NE': 'NEP'
}


def load_projections(week, player_type):
    projections = {}
    fantasy_pros_projections = load_fantasy_pros_projections(
        week, player_type)
    with open(
            '../resources/{0}/fanduel_{1}.csv'.format(week, player_type)) as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = '{0}_{1}'.format(
                row['player'].replace(' ', '_'), row['team'])
            projections[key] = row
            if key in fantasy_pros_projections:
                projections[key]['fantasy_pros'] = \
                    fantasy_pros_projections[key]
    return projections


def load_fantasy_pros_projections(week, player_type):
    projections = {}
    with open(
            '../resources/{0}/fantasy_pros/{1}.csv'.format(
                week, player_type)) as f:
        reader = csv.DictReader(f)
        for row in reader:
            player = row['Player ']
            player = player.split('(')
            player_name = player[0].strip()
            team = player[1].split('-')[0].strip()
            if team in team_conversion:
                team = team_conversion[team]
            key = '{0}_{1}'.format(
                player_name.replace(' ', '_'), team)
            projections[key] = row
    return projections


def load_consistency_projections(week):
    consistency_projections = {}
    with open('../resources/{0}/fanduel_consistency.csv'.format(week)) as f:
        for line in f:
            rows = json.loads(line.strip())
            break
    for row in rows:
        key = '{0}_{1}'.format(
            row['player'].replace(' ', '_'), row['team'])
        if row['gp'] <= 2:
            row['floor'] = 0
        consistency_projections[key] = row
    return consistency_projections


def load_all_projections(week):
    all_projections = {}
    all_projections.update(load_projections(week, player_type='qb'))
    all_projections.update(load_projections(week, player_type='rb'))
    all_projections.update(load_projections(week, player_type='wr'))
    all_projections.update(load_projections(week, player_type='te'))
    all_projections.update(load_projections(week, player_type='kicker'))
    all_projections.update(load_projections(week, player_type='defense'))

    consistency_projections = load_consistency_projections(week)
    for key, item in all_projections.iteritems():
        if key in consistency_projections:
            all_projections[key]['consistency'] = consistency_projections[key]

    return all_projections


def load_eligible_players_for_slate(week, slatefile):
    eligible_players = {}
    with open('../resources/{0}/{1}'.format(week, slatefile)) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['Team'] in team_conversion:
                row['Team'] = team_conversion[row['Team']]
            row['player'] = '{0} {1}'.format(row['First Name'],
                                             row['Last Name'])
            key = '{0}_{1}'.format(
                row['player'].replace(' ', '_'), row['Team'])
            eligible_players[key] = row
    return eligible_players


def get_projections_by_position(week, slatefile):
    projections = load_all_projections(week)
    eligible_players = load_eligible_players_for_slate(week, slatefile)
    qbs = []
    rbs = []
    wrs = []
    tes = []
    defense = []
    kicker = []
    for key, val in projections.iteritems():
        if val['pos'] == 'QB' and key in eligible_players and \
                eligible_players[key]['Injury Indicator'] == '':
            qbs.append(val)
        elif val['pos'] == 'RB' and key in eligible_players and \
                eligible_players[key]['Injury Indicator'] == '':
            rbs.append(val)
        elif val['pos'] == 'WR' and key in eligible_players and \
                eligible_players[key]['Injury Indicator'] == '':
            wrs.append(val)
        elif val['pos'] == 'TE' and key in eligible_players and \
                eligible_players[key]['Injury Indicator'] == '':
            tes.append(val)
        elif val['pos'] == 'D' and key in eligible_players and \
                eligible_players[key]['Injury Indicator'] == '':
            defense.append(val)
        elif val['pos'] == 'K' and key in eligible_players and \
                eligible_players[key]['Injury Indicator'] == '':
            kicker.append(val)
    return qbs, rbs, wrs, tes, defense, kicker
