# Quadropolis solver

The python script `quadropolis_solver.py` will generate high VP board layouts for the Quadropolis board game (and the Public Services expansion).

I highly recommend using [PyPy](https://pypy.org) to run the script, it should be about a factor 4 faster than regular python.

To get started simply run `pypy quadropolis_solver.py`. By default the script will generate board layouts of atleast 108 VP that use 5 random tiles of the Public Services expansion. When a board layout has been found it is printed out like this:
```
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
```

You can use the following table to link the letter codes with the full building names. Note that for optimization reasons the variations of some buildings in the actual game are reduced (for example for Tower Blocks only the +2 population variant is used).
```
T Tower Blocks (+2 population)
S Shops
U Public Services (+1 VP)
P Parks (-1 energy penalty)
G Playgrounds (+1 population)
F Factories (+3 energy)
A Factories (+2 energy)
1 Harbors (+1 energy +1 population)
2 Harbors (+2 VP)
O Office Towers
M Monuments

capi Capitol
cong Congress Center
cust Customs Office
elec Electric Utility
fire Fire Station
hall City Hall
park Park District
plan City Planning
poli Police Station
repr Reprocessing Plant
scho School
tvst TV Station
ward Maternity Ward
```
If you would make this board layout in the actual game it would look like this:
![image of board layout](https://raw.githubusercontent.com/johandebock/quadropolis_solver/master/solutions_expansion_1monument/quad--119--405_22_20_00_41--14_06--07_00_25_19_16_00_20_12_20--capi_cong_hall_park_ward.jpg)

The solution is also saved in a log file:
```
quad--119--405_22_20_00_41--14_06--07_00_25_19_16_00_20_12_20--capi_cong_hall_park_ward.log
```
The filename contains the VP total, counts of all building types, produced population and energy, points for all building types and used expansion tiles.
