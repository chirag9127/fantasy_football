from collections import defaultdict
from helpers import *

from pulp import *

from load_projections import get_projections_by_position


def product(list_floats):
    ret_val = 1
    for f in list_floats:
        ret_val *= float(f)
    return ret_val

class PlayerVariable(object):

    def __init__(self, pos, data):
        self.position = pos
        self.data = data
        self.name = data['player']
        self.variable = LpVariable(data['player'], 0, 1, LpInteger)

    @property
    def fpts(self):
        return float(self.data['fpts'])

    @property
    def floor(self):
        return lookup(self.data, 'consistency', 'floor')

    @property
    def ceiling(self):
        return lookup(self.data, 'consistency', 'ceil')

    @property
    def salary(self):
        return float(self.data['salary'])


POSITIONS = [('qb', 1), ('rb', 2), ('wr', 3), ('te', 1), ('def', 1), ('k', 1)]
POSITION_ORDERS = {POSITIONS[i][0]: i for i in range(len(POSITIONS))}

class Lineup(object):

    def __init__(self, all_players, prob):
        self.prob = prob
        self.players = [all_players[p.name] for p in prob.variables() if p.varValue == 1]
        self.players.sort(key=lambda x: x.name)
        self.string_players = ';'.join([p.name for p in self.players])
        self.players.sort(key=lambda x: POSITION_ORDERS[x.position])
        print self.players[0].data

    def __str__(self):
        return "Status: {}\n{}\n{}\n".format(LpStatus[self.prob.status],
            "\n".join(["{}: {}".format(k, v) for k, v in self.summary]),
            "\n".join(['{}: {}'.format(p.position, p.name) for p in self]))

    @property
    def summary(self):
        return [
            ('projected', sum(player.fpts for player in self)),
            ('salary', sum(player.salary for player in self)),
            ('floor', sum(player.floor for player in self)),
            ('ceiling', sum(player.ceiling for player in self)),
        ]

    @property
    def floor(self):
        return sum(player.floor for player in self)

    def __iter__(self):
        return iter(self.players)

    def __hash__(self):
        return self.string_players.__hash__()

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()


def new_lp_problem(all_players):
    prob = LpProblem("Fanduel selection problem", LpMaximize)
    # add salary constraint
    prob += lpSum([item.variable * item.salary
                   for item in all_players.values()]) <= 60000.0, "Salary constraint"

    for position, num_pos in [('qb', 1), ('rb', 2), ('wr', 3), ('te', 1), ('def', 1), ('k', 1)]:
        prob += lpSum([player.variable for player in all_players.values()
                       if player.position == position]) == num_pos,\
                "{} constraint".format(position)
    return prob


def create_variables(week, slatefile):
    qbs, rbs, wrs, tes, defense, kicker = get_projections_by_position(
        week, slatefile)
    variables = {}
    for pos, pos_list in [('qb', qbs), ('rb', rbs), ('wr', wrs),
                          ('te', tes), ('def', defense), ('k', kicker)]:
        for player in pos_list:
            pv = PlayerVariable(pos, player)
            variables[pv.variable.name] = pv
    return variables


def add_maximizing(prob, all_players, maximizing):
    prob += lpSum([player.variable * product(
        maximize(player) for maximize in maximizing
    ) for player in all_players.values()])
    return prob


def add_constraints(prob, all_players, constraints):
    for constraint_func in constraints:
        prob += constraint_func(all_players)
    return prob


def formulate(all_players, maximizing, constraints=list()):
    prob = new_lp_problem(all_players)
    prob = add_maximizing(prob, all_players, maximizing)
    prob = add_constraints(prob, all_players, constraints)
    prob.solve()
    return Lineup(all_players, prob)


def generate_optimal_lineup(week, slatefile):
    d = defaultdict(list)
    all_players = create_variables(week, slatefile)
    d[formulate(all_players, [fpts, floor])].append('maximizing projection * floor')
    d[formulate(all_players, [floor])].append('maximizing floor')
    d[formulate(all_players, [fpts])].append('maximizing projection')
    d[formulate(all_players, [fpts], [total_floor_constraint_func(80)])].append('maximize proj, with min floor 80')
    d[formulate(all_players, [fpts, inv_dollar], [total_floor_constraint_func(80)])].append('maximize pts/dollar, min floor 80')
    d[formulate(all_players, [floor, ceil])].append('maximizing floor * ceil')
    d[formulate(all_players, [floor, ceil, fpts])].append('maximizing floor * ceil * proj')
    d[formulate(all_players, [ceil], [total_floor_constraint_func(80)])].append('maximizing ceil')

    max_floor = formulate(all_players, [floor]).floor
    d[formulate(all_players, [ceil], [total_floor_constraint_func(0.85 * max_floor)])].append('maximizing ceil; with floor >.85 max')
    d[formulate(all_players, [ceil], [total_floor_constraint_func(0.95 * max_floor)])].append('maximizing ceil; with floor >.95 max')
    d[formulate(all_players, [ceil, fpts], [total_floor_constraint_func(0.85 * max_floor)])].append('maximizing ceil * proj; with floor >.85 max')
    d[formulate(all_players, [ceil, fpts], [total_floor_constraint_func(0.95 * max_floor)])].append('maximizing ceil * proj; with floor >.95 max')

    for k, v in d.iteritems():
        for reason in v:
            print reason
        print k

    d2 = defaultdict(int)

    for lineup in d:
        for player in lineup:
            d2[(player.position, player.name)] += 1
    for p in sorted(d2, key=lambda x: d2[x], reverse=True):
        print p, d2[p]

generate_optimal_lineup('week7', 'fanduel_sunday_1pm_only.csv')
