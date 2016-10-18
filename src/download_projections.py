import urllib


ROTOGRINDERS_PROJECTED_URL = 'https://rotogrinders.com/projected-stats'


def download_file(url, week, filename):
    f = urllib.urlopen(url)
    rows = []
    for line in f:
        rows.append(line)
    with open('../resources/{0}/{1}'.format(week, filename), 'wb') as fo:
        fo.write('player,salary,team,pos,opp,ceil,floor,fpts\n')
        for line in rows[:-1]:
            fo.write(line)


def download_weekly_projections(week):
    download_file(
        '{0}/{1}'.format(ROTOGRINDERS_PROJECTED_URL, 'nfl-qb.csv'),
        week, 'fanduel_qb.csv')
    download_file(
        '{0}/{1}'.format(ROTOGRINDERS_PROJECTED_URL, 'nfl-rb.csv'),
        week, 'fanduel_rb.csv')
    download_file(
        '{0}/{1}'.format(ROTOGRINDERS_PROJECTED_URL, 'nfl-wr.csv'),
        week, 'fanduel_wr.csv')
    download_file(
        '{0}/{1}'.format(ROTOGRINDERS_PROJECTED_URL, 'nfl-te.csv'),
        week, 'fanduel_te.csv')
    download_file(
        '{0}/{1}'.format(ROTOGRINDERS_PROJECTED_URL, 'nfl-defense.csv'),
        week, 'fanduel_defense.csv')
    download_file(
        '{0}/{1}'.format(ROTOGRINDERS_PROJECTED_URL, 'nfl-kicker.csv'),
        week, 'fanduel_kicker.csv')


download_weekly_projections('week7')
