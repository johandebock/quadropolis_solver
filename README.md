# Quadropolis solver

The python script `quadropolis_solver.py` will generate high VP board layouts for the Quadropolis board game (and the Public Services expansion).

I highly recommend using [PyPy](https://pypy.org) to run the script, it should be about a factor 4 faster than regular python.

To get started simply run `pypy quadropolis_solver.py`. By default the script will generate board layouts of atleast 108 VP that use up to 5 random tiles of the Public Services expansion. When a board layout has been found it is printed out like this:
```
[['T', 'P', 'T', '_', '_'],
 ['U', 'M', 'G', 'U', '_'],
 ['U', 'G', 'U', 'S', 'F'],
 ['_', 'T', 'S', 'A', 'U']]
[[1, 1, 1, 1, 1],
 [1, 1, 1, 1, 1],
 [1, 1, 1, 1, 1],
 [1, 5, 1, 1, 1]]
expansion capi fire hall poli ward
pop 20 | 10 | 10 |  1
ene  5 |  5 |  0
   Total Towe Shop Publ Park Fact Harb Offi Monu Expa
cnt  20 |  7 |  2 |  5 |  3 |  2 |  0 |  0 |  1
pts 122 | 22 | 22 | 25 |  8 |  6 |  0 |  0 | 17 | 22
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
![image of board layout](https://raw.githubusercontent.com/johandebock/quadropolis_solver/master/solutions_expansion_1monument/quad--122--725_12_11_00000_01--20_05--22_22_25_08_06_00_00_17_22--capi_fire_hall_poli_ward.jpg)

The solution is also saved in a log file:
```
quad--122--725_12_11_00000_01--20_05--22_22_25_08_06_00_00_17_22--capi_fire_hall_poli_ward.log
```
The filename contains the VP total, counts of all building types, produced population and energy, points for all building types and used expansion tiles.

You can find more already generated optimal board layouts in the solutions_* folders.

Here are a few other high VP board layouts:
```
quad--122--835_01_11_00000_01--24_05--26_33_25_04_08_00_00_13_13--capi_hall_poli_tvst_ward.log
```
![image of board layout](https://raw.githubusercontent.com/johandebock/quadropolis_solver/master/solutions_expansion_1monument/quad--122--835_01_11_00000_01--24_05--26_33_25_04_08_00_00_13_13--capi_hall_poli_tvst_ward.jpg)
```
quad--121--625_12_02_00010_01--20_04--21_22_25_08_12_00_00_13_20--capi_hall_plan_poli_ward.log
```
![image of board layout](https://raw.githubusercontent.com/johandebock/quadropolis_solver/master/solutions_expansion_1monument/quad--121--625_12_02_00010_01--20_04--21_22_25_08_12_00_00_13_20--capi_hall_plan_poli_ward.jpg)
```
quad--121--725_12_02_00000_01--20_04--23_22_25_06_06_00_00_17_22--capi_fire_hall_poli_ward.log
```
![image of board layout](https://raw.githubusercontent.com/johandebock/quadropolis_solver/master/solutions_expansion_1monument/quad--121--725_12_02_00000_01--20_04--23_22_25_06_06_00_00_17_22--capi_fire_hall_poli_ward.jpg)
```
quad--121--825_12_10_00000_01--18_06--27_22_25_12_04_00_00_13_18--capi_elec_hall_poli_scho.log
```
![image of board layout](https://raw.githubusercontent.com/johandebock/quadropolis_solver/master/solutions_expansion_1monument/quad--121--825_12_10_00000_01--18_06--27_22_25_12_04_00_00_13_18--capi_elec_hall_poli_scho.jpg)
