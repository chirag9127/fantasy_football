from pulp import *

from load_projections import get_projections_by_position


def lookup(dic, key, *keys):
    if keys:
        return lookup(dic.get(key, {}), *keys)
    return dic.get(key, 0)


def convert_to_num(string):
    try:
        return float(string)
    except:
        return 0.0


def create_variables(week, slatefile):
    qbs, rbs, wrs, tes, defense, kicker = get_projections_by_position(
        week, slatefile)
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


def formulate_problem(week, slatefile,
                      maximizing_variables=['floor', 'projections']):
    print 'Maximizing: ', ' '.join(maximizing_variables)
    prob = LpProblem("Fanduel selection problem", LpMaximize)
    qbvs, rbvs, wrvs, tevs, kickervs, defvs = create_variables(week,
                                                               slatefile)
    all_players = qbvs + rbvs + wrvs + tevs + kickervs + defvs

    if 'floor' in maximizing_variables and \
            'projections' in maximizing_variables:
        prob += lpSum([item[1]['var']*(float(item[1]['data']['fpts']) *
                                       convert_to_num(
                                           item[1]['data'].get('floor')))
                       for item in all_players]), \
            "maximizing floor times projections"
    elif 'floor' in maximizing_variables:
        prob += lpSum([item[1]['var'] * convert_to_num(
            item[1]['data'].get('floor'))
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

    print_solution(prob, all_players)


def formulate_problem_with_floor_constraint(week, slatefile):
    print 'Maximizing projections with floor constraint'
    prob = LpProblem("Fanduel selection problem", LpMaximize)
    qbvs, rbvs, wrvs, tevs, kickervs, defvs = create_variables(week,
                                                               slatefile)
    all_players = qbvs + rbvs + wrvs + tevs + kickervs + defvs

    prob += lpSum([item[1]['var'] * float(item[1]['data']['fpts'])
                   for item in all_players]), "maximizing projections"

    # add floor constraint
    prob += lpSum([item[1]['var'] * convert_to_num(item[1]['data'].get('floor'))
                   for item in all_players]) >= 110, "maximizing floor"

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

    print_solution(prob, all_players)


def formulate_problem_with_points_per_dollar(week, slatefile):
    print 'Maximizing points/dollar'
    prob = LpProblem("Fanduel selection problem", LpMaximize)
    qbvs, rbvs, wrvs, tevs, kickervs, defvs = create_variables(week,
                                                               slatefile)
    all_players = qbvs + rbvs + wrvs + tevs + kickervs + defvs

    prob += lpSum([item[1]['var'] *
                   (float(item[1]['data']['fpts']) /
                    float(item[1]['data']['salary']))
                   for item in all_players]), "maximizing projections"

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

    print_solution(prob, all_players)


def print_solution(problem, all_players):
    print "-" * 100
    print "Status:", LpStatus[problem.status]
    player_var_to_item = {}
    sum_projections = 0
    sum_floor = 0
    sum_salary = 0
    for item in all_players:
        player_var_to_item[item[1]['var']] = item
    for v in problem.variables():
        if v.varValue == 1:
            sum_projections += float(player_var_to_item[v][1]['data']['fpts'])
            sum_floor += float(
                convert_to_num(player_var_to_item[v][1]['data'].get('floor')))
            sum_salary += float(player_var_to_item[v][1]['data']['salary'])
            print(v.name, "=", v.varValue,
                  player_var_to_item[v][1]['data']['fpts'],
                  convert_to_num(player_var_to_item[v][1]['data'].get('floor')),
                  player_var_to_item[v][1]['data']['salary'])
    print "Sum projections: ", sum_projections
    print "Sum floor: ", sum_floor
    print "Sum salary: ", sum_salary
    print "-" * 100


def generate_optimal_lineup(week, slatefile):
    formulate_problem(week, slatefile)
    formulate_problem(week, slatefile, ['floor'])
    formulate_problem(week, slatefile, ['projections'])
    formulate_problem_with_floor_constraint(week, slatefile)
    formulate_problem_with_points_per_dollar(week, slatefile)


generate_optimal_lineup('week7', 'fanduel_thu_sun_am.csv')
