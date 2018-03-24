#!/usr/bin/env python

## types and distribution in game
## Tower Blocks (+1 population)      21120  6
## Tower Blocks (+2 population)      33323 14
## Tower Blocks (+3 population)      11112  6 26 Tower Blocks
## Shops                             32333 14 14 Shops
## Public Services                   11111  5
## Public Services (+1 VP)           12211  7
## Public Services (+2 VP)           11111  5 17 Public Services
## Parks (-1 energy penalty)         22121  8
## Playgrounds (+1 population)       11111  5 13 Parks/Playgrounds
## Factories (+1 energy)             10000  1
## Factories (+2 energy)             12222  9
## Factories (+3 energy)             11111  5 15 Factories
## Harbors (+2 population)           11100  3
## Harbors (+2 energy)               10110  3
## Harbors (+1 energy +1 population) 12112  7
## Harbors (+1 VP)                   10000  1
## Harbors (+2 VP)                   01100  2
## Harbors (+3 VP)                   00012  3 19 Harbors
## Office Towers                     33344 17 17 Office Towers
## Monuments                         01111  4  4 Monuments

## types and distribution used in calculation
## T Tower Blocks (+2 population)       8
## S Shops                              4
## U Public Services (+1 VP)            3
## U Public Services (+2 VP)            2
## P Parks (-1 energy penalty)          3
## G Playgrounds (+1 population)        2
## F Factories (+3 energy)              2
## A Factories (+2 energy)              3
## 1 Harbors (+1 energy +1 population)  3
## 2 Harbors (+2 VP)                    2
## 3 Harbors (+3 VP)                    1
## 4 Harbors (+2 population)            1
## 5 Harbors (+2 energy)                1
## O Office Towers                      8
## M Monuments                          M

## types and distribution for manual finetuning
## Tower Blocks (+3 pop) extrapop +1    1
## Tower Blocks (+1 pop) extrapop -1    1

from __future__ import print_function
from __future__ import division
import argparse
import copy
import itertools
import os
import pprint
import random
import time

random_exp = 0
exp_choices = ['capi', 'cong', 'cust', 'elec', 'fire', 'hall', 'park', 'plan', 'poli', 'repr', 'scho', 'tvst', 'ward']

def floodfill(im, start_i):
    """flood fill function for Office Tower point calculation
    """
    visited = {start_i}
    queue = [start_i]
    while queue:
        i = queue.pop(-1)
        for n in (i + 1, i + 7, i - 1, i - 7):
            if n not in visited and im[n]:
                visited |= {n}
                queue.append(n)
    return visited

class Board:
    def __init__(self, b=['_'] * 20, f=[1] * 20, extra_pop=0):
        """initialise a 4x5 board
        """
        self.b = b
        self.f = f
        self.extra_pop = extra_pop

    def random_valid(self):
        """generate a valid board with 20 buildings
        valid means: used population <= produced population
                     used energy     <= produced energy
        """
        if random_exp > 0:
            args.exp = random.sample(exp_choices, random_exp)
        elif random_exp < 0:
            args.exp = random.sample(exp_choices, random.randint(0, -random_exp))
        btypes_str = 'T'*8+'S'*4+'U'*(5 - len(args.exp))+'P'*3+'G'*2+'F'*2+'A'*3+'1'*3+'2'*2+'3'*1+'4'*1+'5'*1+'O'*8+'M'*(-args.monuments if args.monuments < 0 else 0)
        btypes_min_str = 'T'*0+'S'*0+'U'*len(args.exp)+'P'*0+'G'*0+'F'*0+'A'*0+'1'*0+'2'*0+'3'*0+'4'*0+'5'*0+'O'*0+'M'*(args.monuments if args.monuments > 0 else 0)
        len_min = len(btypes_min_str)
        while 1:
            ##    TSU_PG_FA_12345_OM
            ## tot845_32_23_32111_81
            ## min00E_00_00_00000_00
            bpos = list(range(20))
            self.b = ['_'] * 20
            self.f = [1] * 20
            cnt_b = 0
            btypes_min = list(btypes_min_str)
            random.shuffle(btypes_min)
            while cnt_b < len_min:
                s_bpos = random.choice(bpos)
                c_bding = self.b[s_bpos]
                if c_bding == 'T' or c_bding == 'O':
                    if self.f[s_bpos] < 5 and c_bding in btypes_min:
                        btypes_min.remove(c_bding)
                        cnt_b += 1
                        self.f[s_bpos] += 1
                    else:
                        bpos.remove(s_bpos)
                else:
                    s_bding = btypes_min.pop(-1)
                    cnt_b += 1
                    self.b[s_bpos] = s_bding
                    if s_bding != 'T' and s_bding != 'O':
                        bpos.remove(s_bpos)
            btypes = list(btypes_str)
            random.shuffle(btypes)
            while cnt_b < 20:
                s_bpos = random.choice(bpos)
                c_bding = self.b[s_bpos]
                if c_bding == 'T' or c_bding == 'O':
                    if self.f[s_bpos] < 5 and c_bding in btypes:
                        btypes.remove(c_bding)
                        cnt_b += 1
                        self.f[s_bpos] += 1
                    else:
                        bpos.remove(s_bpos)
                else:
                    s_bding = btypes.pop(-1)
                    cnt_b += 1
                    self.b[s_bpos] = s_bding
                    if s_bding != 'T' and s_bding != 'O':
                        bpos.remove(s_bpos)
            self.calc_resources()
            if self.popula_used <= self.popula and self.energy_used <= self.energy:
                break

    def swap(self):
        """swap every combination of 2 elements in matrix
        this makes it possible to quickly generate new valid boards starting from a valid board
        the generated boards all have the same produced and used population and energy (so no resource calculation needed)
        """
        if self.cnt_swap == 0:
            i = self.swaplist[self.cnt_swap][0]
            j = self.swaplist[self.cnt_swap][1]
            self.b[i], self.b[j] = self.b[j], self.b[i]
            self.f[i], self.f[j] = self.f[j], self.f[i]
        elif self.cnt_swap < self.nb_swaps:
            i = self.swaplist[self.cnt_swap - 1][0]
            j = self.swaplist[self.cnt_swap - 1][1]
            self.b[i], self.b[j] = self.b[j], self.b[i]
            self.f[i], self.f[j] = self.f[j], self.f[i]
            i = self.swaplist[self.cnt_swap][0]
            j = self.swaplist[self.cnt_swap][1]
            self.b[i], self.b[j] = self.b[j], self.b[i]
            self.f[i], self.f[j] = self.f[j], self.f[i]
        else:
            return 0
        self.cnt_swap += 1
        return 1

    def swap_init(self):
        """swap initialisation
        """
        self.swaplist = tuple(x for x in itertools.combinations(range(20), 2))
        self.nb_swaps = len(self.swaplist)
        self.cnt_swap = 0

    def gen_board_string_calc_resources_counts_points(self):
        """generate a string with 4x5 board, used expansion tiles, produced and used population and energy, counts of all buildings, points for all buildings
        for example:
        [['U', '_', 'U', 'O', 'F'],
         ['M', 'P', 'O', 'U', 'O'],
         ['G', 'U', 'P', 'O', 'F'],
         ['T', 'G', 'T', 'U', '_']]
        [[1, 1, 1, 1, 1],
         [1, 1, 1, 1, 1],
         [1, 1, 1, 1, 1],
         [3, 1, 1, 1, 1]]
        expansion capi cong hall park ward
        pop 14 | 14 |  0 |  1
        ene  6 |  6 |  0
           Total Towe Shop Publ Park Fact Harb Offi Monu Expa
        cnt  20 |  4 |  0 |  5 |  4 |  2 |  0 |  4 |  1
        pts 119 |  7 |  0 | 25 | 19 | 16 |  0 | 20 | 12 | 20
        """
        self.calc_resources()
        self.cnt_T = self.cnt_S = self.cnt_U = self.cnt_P = self.cnt_G = self.cnt_F = self.cnt_A = self.cnt_1 = self.cnt_2 = self.cnt_3 = self.cnt_4 = self.cnt_5 = self.cnt_O = self.cnt_M = 0
        pop_norm = 0
        for i in range(20):
            b = self.b[i]
            if b == 'T':
                self.cnt_T += self.f[i]
                pop_norm += self.f[i] * 2
            elif b == 'S':
                self.cnt_S += 1
            elif b == 'U':
                self.cnt_U += 1
            elif b == 'P':
                self.cnt_P += 1
            elif b == 'G':
                self.cnt_G += 1
                pop_norm += 1
            elif b == 'F':
                self.cnt_F += 1
            elif b == 'A':
                self.cnt_A += 1
            elif b == '1':
                self.cnt_1 += 1
                pop_norm += 1
            elif b == '2':
                self.cnt_2 += 1
            elif b == '3':
                self.cnt_3 += 1
            elif b == '4':
                self.cnt_4 += 1
                pop_norm += 2
            elif b == '5':
                self.cnt_5 += 1
            elif b == 'O':
                self.cnt_O += self.f[i]
            elif b == 'M':
                self.cnt_M += 1
        if 'tvst' in args.exp:
            pop_norm += self.cnt_S
        if 'ward' in args.exp:
            pop_norm += 3
        self.cnt_total = self.cnt_T + self.cnt_S + self.cnt_U + self.cnt_P + self.cnt_G + self.cnt_F + self.cnt_A + self.cnt_1 + self.cnt_2 + self.cnt_3 + self.cnt_4 + self.cnt_5 + self.cnt_O + self.cnt_M
        self.pts_tower = self.calc_points_tower()
        self.pts_shop = self.calc_points_shop()
        self.pts_public = self.calc_points_public()
        self.pts_park = self.calc_points_park()
        self.pts_factory = self.calc_points_factory()
        self.pts_harbor = self.calc_points_harbor()
        self.pts_office = self.calc_points_office()
        self.pts_monument = self.calc_points_monument()
        self.pts_expansion = self.calc_points_expansion()
        self.pts_total = self.pts_tower + self.pts_shop + self.pts_public + self.pts_park + self.pts_factory + self.pts_harbor + self.pts_office + self.pts_monument + self.pts_expansion
        rb = [[]] * 4
        rb[0] = self.b[ 0: 5]
        rb[1] = self.b[ 5:10]
        rb[2] = self.b[10:15]
        rb[3] = self.b[15:20]
        rf = [[]] * 4
        rf[0] = self.f[ 0: 5]
        rf[1] = self.f[ 5:10]
        rf[2] = self.f[10:15]
        rf[3] = self.f[15:20]
        return '{}\n{}\nexpansion {}\npop {:2} | {:2} | {:2} | {:2}\nene {:2} | {:2} | {:2}\n   Total Towe Shop Publ Park Fact Harb Offi Monu Expa\ncnt {:3} | {:2} | {:2} | {:2} | {:2} | {:2} | {:2} | {:2} | {:2}\npts {:3} | {:2} | {:2} | {:2} | {:2} | {:2} | {:2} | {:2} | {:2} | {:2}'.format(pprint.pformat(rb, width=40), pprint.pformat(rf, width=20), ' '.join(sorted(args.exp)), self.popula, self.popula_used, self.popula - self.popula_used, self.popula - pop_norm, self.energy, self.energy_used, self.energy - self.energy_used, self.cnt_total, self.cnt_T, self.cnt_S, self.cnt_U, self.cnt_P + self.cnt_G, self.cnt_F + self.cnt_A, self.cnt_1 + self.cnt_2 + self.cnt_3 + self.cnt_4 + self.cnt_5, self.cnt_O, self.cnt_M, self.pts_total, self.pts_tower, self.pts_shop, self.pts_public, self.pts_park, self.pts_factory, self.pts_harbor, self.pts_office, self.pts_monument, self.pts_expansion)

    def gen_filename(self):
        """generate a filename with total points, counts of all buildings, produced population and energy, points for all buildings, used expansion tiles
        for example:
        quad--119--405_22_20_00_41--14_06--07_00_25_19_16_00_20_12_20--capi_cong_hall_park_ward.log

        for T and O counts hexadecimals are used when > 9
        """
        expansion_string = '_'.join(sorted(args.exp)) if args.exp else 'noexp'
        return 'quad--{}--{}{}{}_{}{}_{}{}_{}{}{}{}{}_{}{}--{:02}_{:02}--{:02}_{:02}_{:02}_{:02}_{:02}_{:02}_{:02}_{:02}_{:02}--{}.log'.format(self.pts_total, hex(self.cnt_T)[-1:], self.cnt_S, self.cnt_U, self.cnt_P, self.cnt_G, self.cnt_F, self.cnt_A, self.cnt_1, self.cnt_2, self.cnt_3, self.cnt_4, self.cnt_5, hex(self.cnt_O)[-1:], self.cnt_M, self.popula, self.energy, self.pts_tower, self.pts_shop, self.pts_public, self.pts_park, self.pts_factory, self.pts_harbor, self.pts_office, self.pts_monument, self.pts_expansion, expansion_string)

    def calc_resources(self):
        """calculate produced and used population and energy

        unchanged while swapping buildings on board
        """
        self.popula = self.energy = self.popula_used = self.energy_used = 0
        self.cnt_public = self.cnt_shop = self.cnt_1 = self.cnt_2 = self.cnt_3 = self.cnt_4 = self.cnt_5 = self.cnt_office = 0
        self.popula += self.extra_pop
        for i in range(20):
            b = self.b[i]
            if b == 'T':
                self.popula += self.f[i] * 2
                self.energy_used += 1
            elif b == 'O':
                self.popula_used += 1
                self.energy_used += 1
                self.cnt_office += self.f[i]
            elif b == 'U':
                self.popula_used += 1
                self.cnt_public += 1
            elif b == 'S':
                self.energy_used += 1
                self.cnt_shop += 1
            elif b == '1':
                self.popula += 1
                self.energy += 1
                self.popula_used += 1
                self.cnt_1 += 1
            elif b == '2':
                self.popula_used += 1
                self.cnt_2 += 1
            elif b == '3':
                self.popula_used += 1
                self.cnt_3 += 1
            elif b == '4':
                self.popula += 2
                self.popula_used += 1
                self.cnt_4 += 1
            elif b == '5':
                self.energy += 2
                self.popula_used += 1
                self.cnt_5 += 1
            elif b == 'A':
                self.energy += 2
                self.popula_used += 1
            elif b == 'F':
                self.energy += 3
                self.popula_used += 1
            elif b == 'G':
                self.popula += 1
        if 'tvst' in args.exp:
            self.popula += self.cnt_shop
        if 'ward' in args.exp:
            self.popula += 3
        if 'elec' in args.exp:
            self.energy += 3
        if 'capi' in args.exp:
            self.popula_used += 2
        if 'fire' in args.exp:
            self.popula_used += 1
        if 'park' in args.exp:
            self.popula_used += 1

    def calc_points_tower(self):
        """calculate Tower Block, Police Station and School points

        unchanged while swapping buildings on board
        """
        points = 0
        cnt_tower = 0
        vptab_tower = (0, 1, 3, 6, 10, 15)
        for i in range(20):
            if self.b[i] == 'T':
                points += vptab_tower[self.f[i]]
                cnt_tower += 1
        if 'poli' in args.exp:
            points += max(self.f)
        if 'scho' in args.exp:
            points += cnt_tower
        return points

    def calc_points_shop(self):
        """calculate Shop points

        unchanged while swapping buildings on board
        """
        rem_pop = self.popula - self.popula_used
        points = min(self.cnt_shop, rem_pop // 5) * 11
        rem_shop = self.cnt_shop - rem_pop // 5
        vptab_shop = (0, 1, 2, 4, 7)
        if rem_shop > 0:
            points += vptab_shop[rem_pop % 5]
        penalty_popula = max(rem_pop - self.cnt_shop * 5, 0)
        points -= penalty_popula
        return points

    def calc_points_public(self):
        """calculate Public Service and City Hall points
        """
        if self.cnt_public >= 2:
            nb_public_in_district = [0, 0, 0, 0, 0]
            i_to_district = (0, 0, 1, 2, 2, 0, 0, 1, 2, 2, 3, 3, 1, 4, 4, 3, 3, 1, 4, 4)
            for i in range(20):
                if self.b[i] == 'U':
                    nb_public_in_district[i_to_district[i]] += 1
            districts = len([1 for x in nb_public_in_district if x > 0])
            vptab_public = (0, 2, 5, 9, 14, 20)
            points = vptab_public[districts] + self.cnt_public - len(args.exp) + self.cnt_public * ('hall' in args.exp)
            points += min(self.cnt_public - len(args.exp), 2)
            return points
        elif self.cnt_public == 1:
            points = 4 - 2 * len(args.exp) + ('hall' in args.exp)
            return points
        return 0

    def calc_points_park(self):
        """calculate Park, Park District and Reprocessing Plant points
        """
        be = ['_'] * 8
        be += self.b[ 0: 5]
        be += ['_'] * 2
        be += self.b[ 5:10]
        be += ['_'] * 2
        be += self.b[10:15]
        be += ['_'] * 2
        be += self.b[15:20]
        be += ['_'] * 8
        cnt_PG = 0
        cnt_P = 0
        points = 0
        vptab_park = (0, 2, 4, 7, 11)
        for i in range(8, 34):
            if be[i] == 'P' or be[i] == 'G':
                cnt_PG += 1
                if be[i] == 'P':
                    cnt_P += 1
                neigh_tower_office = 0
                if be[i - 1] == 'T' or be[i - 1] == 'O':
                    neigh_tower_office += 1
                if be[i + 1] == 'T' or be[i + 1] == 'O':
                    neigh_tower_office += 1
                if be[i - 7] == 'T' or be[i - 7] == 'O':
                    neigh_tower_office += 1
                if be[i + 7] == 'T' or be[i + 7] == 'O':
                    neigh_tower_office += 1
                points += vptab_park[neigh_tower_office]
        if 'park' in args.exp:
            points += cnt_PG
        if 'repr' in args.exp:
            recycle_energy = max(self.energy - self.energy_used, 0)
            points += recycle_energy
        else:
            penalty_energy = max(self.energy - self.energy_used - cnt_P, 0)
            points -= penalty_energy
        return points

    def calc_points_factory(self):
        """calculate Factory points
        """
        be = ['_'] * 8
        be += self.b[ 0: 5]
        be += ['_'] * 2
        be += self.b[ 5:10]
        be += ['_'] * 2
        be += self.b[10:15]
        be += ['_'] * 2
        be += self.b[15:20]
        be += ['_'] * 8
        points = 0
        for i in range(8, 34):
            if be[i] == 'A' or be[i] == 'F':
                if be[i - 1] == 'O':
                    points += 4
                elif ord(be[i - 1]) < 54:
                    points += 3
                elif be[i - 1] == 'S':
                    points += 2
                if be[i + 1] == 'O':
                    points += 4
                elif ord(be[i + 1]) < 54:
                    points += 3
                elif be[i + 1] == 'S':
                    points += 2
                if be[i - 7] == 'O':
                    points += 4
                elif ord(be[i - 7]) < 54:
                    points += 3
                elif be[i - 7] == 'S':
                    points += 2
                if be[i + 7] == 'O':
                    points += 4
                elif ord(be[i + 7]) < 54:
                    points += 3
                elif be[i + 7] == 'S':
                    points += 2
        return points

    def calc_points_harbor(self):
        """calculate Harbor and Customs Office points
        """
        points = 0
        if self.cnt_1 + self.cnt_2 + self.cnt_3 + self.cnt_4 + self.cnt_5 >= 2:
            hor = 0
            for i in range(4):
                j = 0
                while j < 5 and ord(self.b[i * 5 + j]) >= 54:
                    j += 1
                if j < 4:
                    start = j
                    j += 1
                    while j < 5 and ord(self.b[i * 5 + j]) < 54:
                        j += 1
                    length = j - start
                    if length > hor:
                        hor = length
            vptab_harbor = (0, 0, 3, 7, 12, 18)
            points += vptab_harbor[hor]
            ver = 0
            for j in range(5):
                i = 0
                while i < 4 and ord(self.b[i * 5 + j]) >= 54:
                    i += 1
                if i < 3:
                    start = i
                    i += 1
                    while i < 4 and ord(self.b[i * 5 + j]) < 54:
                        i += 1
                    length = i - start
                    if length > ver:
                        ver = length
            points += vptab_harbor[ver]
            if 'cust' in args.exp:
                if ver == 4 or hor == 5:
                    points += 5
        points += 2 * self.cnt_2 + 3 * self.cnt_3
        return points

    def calc_points_office(self):
        """calculate Office Tower and Congress Center points
        """
        if 'cong' in args.exp:
            if self.cnt_office >= 1:
                be = [0] * 8
                be += [1 if x == 'O' else 0 for x in self.b[ 0: 5]]
                be += [0] * 2
                be += [1 if x == 'O' else 0 for x in self.b[ 5:10]]
                be += [0] * 2
                be += [1 if x == 'O' else 0 for x in self.b[10:15]]
                be += [0] * 2
                be += [1 if x == 'O' else 0 for x in self.b[15:20]]
                be += [0] * 8
                max_points = 0
                vptab_office = (
                    (0, 0, 0,  0,  0,  0),
                    (0, 0, 1,  3,  6, 10),
                    (0, 1, 3,  6, 10, 15),
                    (0, 2, 5,  9, 14, 20),
                    (0, 3, 7, 12, 18, 25),
                    (0, 4, 9, 15, 22, 30)
                )
                for bi in range(20):
                    if self.b[bi] == 'U':
                        be[(bi // 5 + 1) * 7 + bi % 5 + 1] = 1
                        total_visited = set()
                        points = 0
                        for i in range(8, 34):
                            if be[i] and i not in total_visited:
                                visited = floodfill(be, i)
                                total_visited |= visited
                                adj = min(len(visited), 5)
                                for vi in visited:
                                    points += vptab_office[adj][self.f[(vi // 7 - 1) * 5 + vi % 7 - 1]]
                        if points > max_points:
                            max_points = points
                        be[(bi // 5 + 1) * 7 + bi % 5 + 1] = 0
                return max_points
        else:
            if self.cnt_office >= 2:
                be = [0] * 8
                be += [1 if x == 'O' else 0 for x in self.b[ 0: 5]]
                be += [0] * 2
                be += [1 if x == 'O' else 0 for x in self.b[ 5:10]]
                be += [0] * 2
                be += [1 if x == 'O' else 0 for x in self.b[10:15]]
                be += [0] * 2
                be += [1 if x == 'O' else 0 for x in self.b[15:20]]
                be += [0] * 8
                points = 0
                total_visited = set()
                vptab_office = (
                    (0, 0, 0,  0,  0,  0),
                    (0, 0, 1,  3,  6, 10),
                    (0, 1, 3,  6, 10, 15),
                    (0, 2, 5,  9, 14, 20),
                    (0, 3, 7, 12, 18, 25),
                    (0, 4, 9, 15, 22, 30)
                )
                for i in range(8, 34):
                    if be[i] and i not in total_visited:
                        visited = floodfill(be, i)
                        total_visited |= visited
                        adj = min(len(visited), 5)
                        for vi in visited:
                            points += vptab_office[adj][self.f[(vi // 7 - 1) * 5 + vi % 7 - 1]]
                return points
        return 0

    def calc_points_monument(self):
        """calculate Monument points
        """
        be = ['_'] * 8
        be += self.b[ 0: 5]
        be += ['_'] * 2
        be += self.b[ 5:10]
        be += ['_'] * 2
        be += self.b[10:15]
        be += ['_'] * 2
        be += self.b[15:20]
        be += ['_'] * 8
        points = 0
        for i in range(8, 34):
            if be[i] == 'M':
                if be[i - 1] == 'P' or be[i - 1] == 'G':
                    points += 5
                elif be[i - 1] == 'S':
                    points += 3
                elif be[i - 1] == 'U':
                    points += 2
                elif be[i - 1] == 'A' or be[i - 1] == 'F' or ord(be[i - 1]) < 54:
                    points -= 5
                if be[i + 1] == 'P' or be[i + 1] == 'G':
                    points += 5
                elif be[i + 1] == 'S':
                    points += 3
                elif be[i + 1] == 'U':
                    points += 2
                elif be[i + 1] == 'A' or be[i + 1] == 'F' or ord(be[i + 1]) < 54:
                    points -= 5
                if be[i - 7] == 'P' or be[i - 7] == 'G':
                    points += 5
                elif be[i - 7] == 'S':
                    points += 3
                elif be[i - 7] == 'U':
                    points += 2
                elif be[i - 7] == 'A' or be[i - 7] == 'F' or ord(be[i - 7]) < 54:
                    points -= 5
                if be[i + 7] == 'P' or be[i + 7] == 'G':
                    points += 5
                elif be[i + 7] == 'S':
                    points += 3
                elif be[i + 7] == 'U':
                    points += 2
                elif be[i + 7] == 'A' or be[i + 7] == 'F' or ord(be[i + 7]) < 54:
                    points -= 5
        return points

    def calc_points_expansion(self):
        """calculate Capitol, City Planning and Fire Station points
        """
        tot_points = 0
        if 'capi' in args.exp:
            be = ['_'] * 8
            be += self.b[ 0: 5]
            be += ['_'] * 2
            be += self.b[ 5:10]
            be += ['_'] * 2
            be += self.b[10:15]
            be += ['_'] * 2
            be += self.b[15:20]
            be += ['_'] * 8
            max_points = 0
            for i in range(8, 34):
                if be[i] == 'U':
                    points = 0
                    if be[i - 1] == 'P' or be[i - 1] == 'G':
                        points += 5
                    elif be[i - 1] == 'S':
                        points += 3
                    elif be[i - 1] == 'U':
                        points += 2
                    elif be[i - 1] == 'A' or be[i - 1] == 'F' or ord(be[i - 1]) < 54:
                        points -= 5
                    if be[i + 1] == 'P' or be[i + 1] == 'G':
                        points += 5
                    elif be[i + 1] == 'S':
                        points += 3
                    elif be[i + 1] == 'U':
                        points += 2
                    elif be[i + 1] == 'A' or be[i + 1] == 'F' or ord(be[i + 1]) < 54:
                        points -= 5
                    if be[i - 7] == 'P' or be[i - 7] == 'G':
                        points += 5
                    elif be[i - 7] == 'S':
                        points += 3
                    elif be[i - 7] == 'U':
                        points += 2
                    elif be[i - 7] == 'A' or be[i - 7] == 'F' or ord(be[i - 7]) < 54:
                        points -= 5
                    if be[i + 7] == 'P' or be[i + 7] == 'G':
                        points += 5
                    elif be[i + 7] == 'S':
                        points += 3
                    elif be[i + 7] == 'U':
                        points += 2
                    elif be[i + 7] == 'A' or be[i + 7] == 'F' or ord(be[i + 7]) < 54:
                        points -= 5
                    if points > max_points:
                        max_points = points
            tot_points += max_points
        if 'plan' in args.exp:
            nb_b_in_district = [0, 0, 0, 0, 0]
            i_to_district = (0, 0, 1, 2, 2, 0, 0, 1, 2, 2, 3, 3, 1, 4, 4, 3, 3, 1, 4, 4)
            for i in range(20):
                if self.b[i] != '_':
                    nb_b_in_district[i_to_district[i]] += 1
            points = len([1 for x in nb_b_in_district if x == 4])
            if points == 5:
                points = 6
            tot_points += points
        if 'fire' in args.exp:
            be = ['_'] * 8
            be += self.b[ 0: 5]
            be += ['_'] * 2
            be += self.b[ 5:10]
            be += ['_'] * 2
            be += self.b[10:15]
            be += ['_'] * 2
            be += self.b[15:20]
            be += ['_'] * 8
            max_points = 0
            for i in range(8, 34):
                if be[i] == 'U':
                    points = 0
                    if be[i - 1] == 'A' or be[i - 1] == 'F':
                        points += 3
                    if be[i + 1] == 'A' or be[i + 1] == 'F':
                        points += 3
                    if be[i - 7] == 'A' or be[i - 7] == 'F':
                        points += 3
                    if be[i + 7] == 'A' or be[i + 7] == 'F':
                        points += 3
                    if points > max_points:
                        max_points = points
            tot_points += max_points
        return tot_points

    def calc_points_all_expansions(self):
        """calculate points from VP scoring expansion tiles
        """
        points = self.calc_points_expansion()
        if 'cust' in args.exp and self.cnt_1 + self.cnt_2 + self.cnt_3 + self.cnt_4 + self.cnt_5 >= 2:
            hor = 0
            for i in range(4):
                j = 0
                while j < 5 and ord(self.b[i * 5 + j]) >= 54:
                    j += 1
                if j < 4:
                    start = j
                    j += 1
                    while j < 5 and ord(self.b[i * 5 + j]) < 54:
                        j += 1
                    length = j - start
                    if length > hor:
                        hor = length
            ver = 0
            for j in range(5):
                i = 0
                while i < 4 and ord(self.b[i * 5 + j]) >= 54:
                    i += 1
                if i < 3:
                    start = i
                    i += 1
                    while i < 4 and ord(self.b[i * 5 + j]) < 54:
                        i += 1
                    length = i - start
                    if length > ver:
                        ver = length
            if ver == 4 or hor == 5:
                points += 5
        if 'hall' in args.exp:
            points += self.cnt_public
        if 'park' in args.exp:
            cnt_PG = 0
            for i in range(20):
                if self.b[i] == 'P' or self.b[i] == 'G':
                        cnt_PG += 1
            points += cnt_PG
        if 'poli' in args.exp:
            points += max(self.f)
        if 'repr' in args.exp:
            recycle_energy = max(self.energy - self.energy_used, 0)
            points += recycle_energy
        if 'scho' in args.exp:
            cnt_tower = 0
            for i in range(20):
                if self.b[i] == 'T':
                    cnt_tower += 1
            points += cnt_tower
        return points




### main
parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-mode', choices=['find', 'opti'], default='find')
parser.add_argument('-log')
parser.add_argument('-exp', nargs='+', choices=['none', 'all1', 'all2', 'all3', 'all4', 'all5', 'max1', 'max2', 'max3', 'max4', 'max5', 'capi', 'cong', 'cust', 'elec', 'fire', 'hall', 'park', 'plan', 'poli', 'repr', 'scho', 'tvst', 'ward'], default=['max5'])
parser.add_argument('-monuments', type=int, default=-1)
parser.add_argument('-extrapop', type=int, default=1)
parser.add_argument('-minvp', type=int, default=108)
parser.add_argument('-swapmin', type=int, default=66)
args = parser.parse_args()

if args.mode == 'find':
    if 'none' in args.exp:
        args.exp = []
    elif 'all1' in args.exp:
        random_exp = 1
    elif 'all2' in args.exp:
        random_exp = 2
    elif 'all3' in args.exp:
        random_exp = 3
    elif 'all4' in args.exp:
        random_exp = 4
    elif 'all5' in args.exp:
        random_exp = 5
    elif 'max1' in args.exp:
        random_exp = -1
    elif 'max2' in args.exp:
        random_exp = -2
    elif 'max3' in args.exp:
        random_exp = -3
    elif 'max4' in args.exp:
        random_exp = -4
    elif 'max5' in args.exp:
        random_exp = -5
    t1 = time.time()
    nr_boards_tried = 0
    max_max_points = 0
    bo = Board(extra_pop=args.extrapop)
    while 1:
        bo.random_valid()
        nr_boards_tried += 1
        pts_tower = bo.calc_points_tower()
        pts_shop = bo.calc_points_shop()
        pts_public = bo.calc_points_public()
        pts_park = bo.calc_points_park()
        pts_factory = bo.calc_points_factory()
        pts_harbor = bo.calc_points_harbor()
        pts_office = bo.calc_points_office()
        pts_monument = bo.calc_points_monument()
        pts_expansion = bo.calc_points_expansion()
        points = pts_tower + pts_shop + pts_public + pts_park + pts_factory + pts_harbor + pts_office + pts_monument + pts_expansion
        if points >= args.swapmin:
            max_bo = copy.deepcopy(bo)
            max_points = points
            new_max_found = 1
            while new_max_found:
                new_max_found = 0
                bo.swap_init()
                while bo.swap():
                    nr_boards_tried += 1
                    pts_public = bo.calc_points_public()
                    pts_park = bo.calc_points_park()
                    pts_factory = bo.calc_points_factory()
                    pts_harbor = bo.calc_points_harbor()
                    pts_office = bo.calc_points_office()
                    pts_monument = bo.calc_points_monument()
                    pts_expansion = bo.calc_points_expansion()
                    points = pts_tower + pts_shop + pts_public + pts_park + pts_factory + pts_harbor + pts_office + pts_monument + pts_expansion
                    if points > max_points:
                        max_bo = copy.deepcopy(bo)
                        max_points = points
                        new_max_found = 1
                if new_max_found:
                    bo = copy.deepcopy(max_bo)
            if max_points > max_max_points:
                max_max_points = max_points
            if max_points >= args.minvp:
                print('')
                max_bo_string = max_bo.gen_board_string_calc_resources_counts_points()
                print(max_bo_string)
                print('')
                filename = max_bo.gen_filename()
                with open(filename, 'w') as f:
                    print(max_bo_string, file=f)
        if time.time() - t1 > 30:
            print('speed {} {}'.format(int(nr_boards_tried // (time.time() - t1)), max_max_points))
            t1 = time.time()
            nr_boards_tried = 0
            max_max_points = 0

elif args.mode == 'opti':
    if args.log:
        with open(args.log, 'r') as f:
            log = f.readlines()
        b  = [str(x.strip().strip("'[]")) for x in log[0].split(',')[0:5]]
        b += [str(x.strip().strip("'[]")) for x in log[1].split(',')[0:5]]
        b += [str(x.strip().strip("'[]")) for x in log[2].split(',')[0:5]]
        b += [str(x.strip().strip("'[]")) for x in log[3].split(',')[0:5]]
        f  = [int(x.strip().strip("'[]")) for x in log[4].split(',')[0:5]]
        f += [int(x.strip().strip("'[]")) for x in log[5].split(',')[0:5]]
        f += [int(x.strip().strip("'[]")) for x in log[6].split(',')[0:5]]
        f += [int(x.strip().strip("'[]")) for x in log[7].split(',')[0:5]]
        args.exp = log[8].strip().split(' ')[1:]
        extra_pop = int(log[9].split('|')[-1])
        bo = Board(b, f, extra_pop)
        bo_string = bo.gen_board_string_calc_resources_counts_points()
        print(bo_string)
        print('pts all exp', bo.calc_points_all_expansions())
        print('')
        max_bo = copy.deepcopy(bo)
        max_points = bo.pts_total
        max_exp = list(args.exp)
        for args.exp in [x for x in itertools.combinations(exp_choices, len(args.exp))]:
            bo.calc_resources()
            if bo.popula_used <= bo.popula and bo.energy_used <= bo.energy:
                new_max_found = 1
                while new_max_found:
                    new_max_found = 0
                    bo.swap_init()
                    while bo.swap():
                        pts_tower = bo.calc_points_tower()
                        pts_shop = bo.calc_points_shop()
                        pts_public = bo.calc_points_public()
                        pts_park = bo.calc_points_park()
                        pts_factory = bo.calc_points_factory()
                        pts_harbor = bo.calc_points_harbor()
                        pts_office = bo.calc_points_office()
                        pts_monument = bo.calc_points_monument()
                        pts_expansion = bo.calc_points_expansion()
                        points = pts_tower + pts_shop + pts_public + pts_park + pts_factory + pts_harbor + pts_office + pts_monument + pts_expansion
                        if points > max_points:
                            max_bo = copy.deepcopy(bo)
                            max_points = points
                            max_exp = list(args.exp)
                            new_max_found = 1
                    if new_max_found:
                        bo = copy.deepcopy(max_bo)
        args.exp = list(max_exp)
        max_bo_string = max_bo.gen_board_string_calc_resources_counts_points()
        print(max_bo_string)
        print('pts all exp', max_bo.calc_points_all_expansions())
        os.remove(args.log)
        filename = max_bo.gen_filename()
        print('writing to {}'.format(filename))
        with open(filename, 'w') as f:
            print(max_bo_string, file=f)
    else:
        print('provide a log to optimize with -log')
