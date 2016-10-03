import json
from pulp import *

from load_projections import get_projections_by_position


def lookup(dic, key, *keys):
    if keys:
        return lookup(dic.get(key, {}), *keys)
    return dic.get(key, 0)


def create_variables(teams):
    qbs, rbs, wrs, tes, defense, kicker = get_projections_by_position(teams)
    qbvs, rbvs, wrvs, tevs, defvs, kickervs = [], [], [], [], [], []
    for qb in qbs:
        qbvs.append((qb['player'], {'var':
                                    LpVariable(qb['player'], 0, 1, LpInteger),
                                    'data': qb}))
    for rb in rbs:
        rbvs.append((rb['player'], {'var':
                                    LpVariable(rb['player'], 0, 1, LpInteger),
                                    'data': rb}))
    for wr in wrs:
        wrvs.append((wr['player'], {'var':
                                    LpVariable(wr['player'], 0, 1, LpInteger),
                                    'data': wr}))
    for te in tes:
        tevs.append((te['player'], {'var':
                                    LpVariable(te['player'], 0, 1, LpInteger),
                                    'data': te}))
    for de in defense:
        defvs.append((de['player'], {'var':
                                     LpVariable(de['player'], 0, 1, LpInteger),
                                     'data': de}))
    for ki in kicker:
        kickervs.append((ki['player'], {'var':
                                        LpVariable(
                                            ki['player'], 0, 1, LpInteger),
                                        'data': ki}))
    return qbvs, rbvs, wrvs, tevs, kickervs, defvs


def formulate_problem(teams, maximizing_variables=['floor', 'projections']):
    print 'Maximizing: ', ' '.join(maximizing_variables)
    prob = LpProblem("Fanduel selection problem", LpMaximize)
    qbvs, rbvs, wrvs, tevs, kickervs, defvs = create_variables(teams)
    all_players = qbvs + rbvs + wrvs + tevs + kickervs + defvs

    if 'floor' in maximizing_variables and \
            'projections' in maximizing_variables:
        prob += lpSum([item[1]['var']*(float(item[1]['data']['fpts']) +
                                       lookup(item[1]['data'],
                                              'consistency', 'floor'))
                       for item in all_players]), \
            "maximizing floor and projections"
    elif 'floor' in maximizing_variables:
        prob += lpSum([item[1]['var'] * lookup(item[1]['data'],
                                               'consistency', 'floor')
                       for item in all_players]), \
            "maximizing floor"
    elif 'projections' in maximizing_variables:
        prob += lpSum([item[1]['var'] * float(item[1]['data']['fpts'])
                       for item in all_players]), \
            "maximizing projections"

    # add salary constraint
    prob += lpSum([item[1]['var'] * float(item[1]['data']['salary'])
                   for item in all_players]) <= 60000.0, "Salary constraint"

    # qb constraint
    prob += lpSum([item[1]['var'] for item in qbvs]) == 1, "qb constraint"

    # rb constraint
    prob += lpSum([item[1]['var'] for item in rbvs]) == 2, "rb constraint"

    # wr constraint
    prob += lpSum([item[1]['var'] for item in wrvs]) == 3, "wr constraint"

    # te constraint
    prob += lpSum([item[1]['var'] for item in tevs]) == 1, "te constraint"

    # de constraint
    prob += lpSum([item[1]['var'] for item in defvs]) == 1, "def constraint"

    # kicker constraint
    prob += lpSum([item[1]['var'] for item in kickervs]) == 1, "ki constraint"

    prob.solve()

    print "Status:", LpStatus[prob.status]
    for v in prob.variables():
        if v.varValue == 1:
            print(v.name, "=", v.varValue)


def generate_optimal_lineup(week='week4'):
    with open('../resources/{0}/games.json'.format(week)) as f:
        for line in f:
            games = json.loads(line.strip())
            break
    for game, teams in games.iteritems():
        print game
        formulate_problem(teams)
        formulate_problem(teams, ['floor'])
        formulate_problem(teams, ['projections'])
        print '\n\n\n'


generate_optimal_lineup()