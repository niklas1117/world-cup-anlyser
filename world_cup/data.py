"""
Static data for the 2026 FIFA World Cup:
- Group draw (48 teams, 12 groups)
- Knockout bracket structure (R32 → R16 → QF → SF → Final)
- Team strength ratings for realistic simulation
"""

# 2026 FIFA World Cup groups (draw announced December 2024)
GROUPS = {
    'A': ['Mexico', 'South Korea', 'South Africa', 'Czechia'],
    'B': ['Canada', 'Bosnia and Herzegovina', 'Qatar', 'Switzerland'],
    'C': ['Brazil', 'Morocco', 'Haiti', 'Scotland'],
    'D': ['USA', 'Paraguay', 'Australia', 'Turkey'],
    'E': ['Germany', 'Curacao', "Cote d'Ivoire", 'Ecuador'],
    'F': ['Netherlands', 'Japan', 'Sweden', 'Tunisia'],
    'G': ['Belgium', 'Egypt', 'Iran', 'New Zealand'],
    'H': ['Spain', 'Cabo Verde', 'Saudi Arabia', 'Uruguay'],
    'I': ['France', 'Senegal', 'Iraq', 'Norway'],
    'J': ['Argentina', 'Algeria', 'Austria', 'Jordan'],
    'K': ['Portugal', 'DR Congo', 'Uzbekistan', 'Colombia'],
    'L': ['England', 'Croatia', 'Ghana', 'Panama'],
}

# Round of 32 bracket slots: match_num -> (slot1, slot2)
# Slot notation:
#   '1A' = winner of Group A
#   '2B' = runner-up of Group B
#   '3ABCDF' = best qualifying 3rd-place team from groups A, B, C, D, or F
R32_SLOTS = {
    73: ('2A',  '2B'),
    74: ('1E',  '3ABCDF'),
    75: ('1F',  '2C'),
    76: ('1C',  '2F'),
    77: ('1I',  '3CDFGH'),
    78: ('2E',  '2I'),
    79: ('1A',  '3CEFHI'),
    80: ('1L',  '3EHIJK'),
    81: ('1D',  '3BEFIJ'),
    82: ('1G',  '3AEHIJ'),
    83: ('2K',  '2L'),
    84: ('1H',  '2J'),
    85: ('1B',  '3EFGIJ'),
    86: ('1J',  '2H'),
    87: ('1K',  '3DEIJL'),
    88: ('2D',  '2G'),
}

# Knockout bracket progression: match_num -> (source_match_1, source_match_2)
# Covers R16 through Final. Winner of source matches plays here.
KNOCKOUT_BRACKET = {
    # Round of 16
    89:  (74, 77),
    90:  (73, 75),
    91:  (76, 78),
    92:  (79, 80),
    93:  (83, 84),
    94:  (81, 82),
    95:  (86, 88),
    96:  (85, 87),
    # Quarterfinals
    97:  (89, 90),
    98:  (93, 94),
    99:  (91, 92),
    100: (95, 96),
    # Semifinals
    101: (97,  98),
    102: (99,  100),
    # Final
    104: (101, 102),
}

ROUND_NAMES = {
    **{m: 'Round of 32' for m in range(73, 89)},
    **{m: 'Round of 16' for m in range(89, 97)},
    **{m: 'Quarterfinal' for m in range(97, 101)},
    **{m: 'Semifinal'    for m in (101, 102)},
    104: 'Final',
}

# Approximate team strength ratings (higher = stronger).
# Used for weighted match simulation.
TEAM_STRENGTH = {
    'France':                  2050,
    'Brazil':                  1980,
    'Argentina':               1970,
    'Germany':                 1950,
    'Spain':                   1940,
    'England':                 1920,
    'Portugal':                1900,
    'Netherlands':             1870,
    'Belgium':                 1850,
    'Norway':                  1760,
    'USA':                     1730,
    'Mexico':                  1710,
    'Switzerland':             1700,
    'Canada':                  1690,
    'Japan':                   1690,
    'South Korea':             1680,
    'Morocco':                 1670,
    'Senegal':                 1660,
    'Colombia':                1650,
    'Ecuador':                 1640,
    'Uruguay':                 1630,
    'Croatia':                 1620,
    'Sweden':                  1610,
    'Austria':                 1600,
    'Scotland':                1580,
    'Turkey':                  1570,
    'Australia':               1550,
    'Algeria':                 1530,
    'Tunisia':                 1520,
    'Ghana':                   1510,
    'Czechia':                 1505,
    'Iran':                    1500,
    'Egypt':                   1490,
    'Paraguay':                1480,
    'South Africa':            1470,
    'Saudi Arabia':            1460,
    'DR Congo':                1450,
    "Cote d'Ivoire":           1445,
    'Bosnia and Herzegovina':  1440,
    'Jordan':                  1430,
    'Uzbekistan':              1425,
    'Cabo Verde':              1420,
    'Qatar':                   1390,
    'Haiti':                   1380,
    'Panama':                  1370,
    'Iraq':                    1360,
    'New Zealand':             1350,
    'Curacao':                 1310,
}
