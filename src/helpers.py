from pulp import *


def lookup(dic, key, *keys):
    if keys:
        return lookup(dic.get(key, {}), *keys)
    return dic.get(key, 0)


def total_floor_constraint_func(value):
    def floor_sum(all_players):
        return lpSum([item.variable * floor(item)
               for item in all_players.values()]) >= value, "maximizing floor"
    return floor_sum


def fpts(player):
    return player.data['fpts']


def floor(player):
    return player.floor


def ceil(player):
    return player.ceiling


def inv_dollar(player):
    return 1 / float(player.data['salary'])