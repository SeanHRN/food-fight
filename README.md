# food-fight
Legally Distinct Portable Fighting Monster Battle System In Python
v0.1
<br>
Play it in the terminal!
<br>
=== Choose Your Fighters! ===
<br>
- Rice Ninja
- Soup Dumpling
- Dinuguanggal
- LaabGai

## Features ##
- Turn-based battle system with speed and priority
- Types
- Stats
- Stat changes
- Basic moves
- Abilities
- Status effects (poison, bad poison, and burn)
- Specialized effect moves and abilities
- Attack damage formula factoring in levels, types, IVs, EVs, status effect, etc.
- All IVs are 31 by default.
- Fighters, moves, and abilities are loaded in via JSON.
- Type effectiveness chart is loaded in via CSV.
- Cicada Husk Ghost HP limiter
- New moves: [scrape(), analyzed_impale()]
- New ability: Soup Burst

## To Do ##
- Add more status effects
- Improve modularization of abilities
- Add held items
- Make accuracy check do things other than return True
- Add weather to calculations
- Work in progress characters:
    - Halo-Halo
    - Gangster Punk Lizard
    - Forest Lizard

## How To Play ##
Run battle.py in your terminal from this directory.
<br>
`python battle.py`
or
`py battle.py`