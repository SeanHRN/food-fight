# food-fight

Legally Distinct Portable Fighting Monster Battle System In Python

v0.34

<br>

Play it in the terminal!

<br>

=== The Fighters ===

<br>

<h3>Rice Ninja - The Amylopectin Assassin</h3>
Type: Grass/Dark
<br>Food: Onigiri
<br>Description: Physical Attacker
<br>Ability: Adaptability

Moves

- Leaf Blade (Grass)
- Sucker Punch (Dark)
- Rice Shuriken (Grass)
	- +1 Priority, 3 Hits
- U-turn (Bug)

<h3>Soup Dumpling - The Hydraulic Crawler</h3>
Type: Water/Fire
<br>Food: Soup Dumpling
<br>Description: Tanky Physical Attacker
<br>Ability: Soup Burst - When HP is 50% or lower, all the user's stats decrease by 2 stages, and the opponent is hit with Scald. The Scald always misses if the opponent did not hit with a contact move.

Moves

- Protect (Normal)
- Jet Punch (Water)
- Heat Crash (Fire)
- Lunge (Bug)

<h3>Dinuguanggal - The Atramentous Autotomy</h3>
Type: Dark/Poison
<br>Food: Dinuguan
<br>Description: Special Attack Sweeper
<br>Ability: Technician

Moves

- Autotomize (Steel)
- scrape() (Poison)
	- The user invades and analyzes the opponent with its blood, sharply raising its special attack, lowering its defense and special defense, and poisoning the opponent.
- analyzed_impale() (Dark)
	- "The user sends out a piece of its body to pierce the opponent. If the opponent is poisoned, this move deals double damage. This also damages the user a little."
- Acid Spray (Poison)


<h3>LaabGai - The Nine-Limb Set</h3>
Types: Fighting/Dragon
<br>Food: Laab Gai (Chicken Laab)
<br>Description: Extreme Physical Attack and Speed
<br>Ability: Punk Rock

Moves

- Drum Solo (Fighting)
	- "The user punches and kicks the opponent at blistering speed. It works only once when the user is in battle."
		- +2 Priority, and it's a sound move, so it gets boosted by Punk Rock.
- Mach Punch (Fighting)
- Later Gator (Dragon)
	- It's U-turn but Dragon type, so he gets STAB.
- Belly Drum (Normal)

<h3>Halo-Halo - The Ice-Cold Mix-Ups</h3>
Types: Water/Ice
<br>Food: Halo-Halo
<br>Description: Multi-hitter
<br>Ability: Skill Link

Moves

- Chilling Water (Water)
- Icicle Spear (Ice)
- Hydro Pump (Water)
- Aqua Jet (Water)


<h3>Bonus: Gangster Punk Lizard</h3>
Types: Dark/Fighting
<br>Description: Physical Attack Sweeper With Bulk
<br>Ability: Moxie

Moves

- Ice Punch (Ice)
- Drain Punch (Fighting)
- Dragon Dance (Dragon)
- Crunch (Dark)

## Features ##

- Turn-based battle system with speed and priority

- Types

- Stats

- Stat changes

- Abilities

- Status effects (poison, bad poison, and burn)

- Specialized effect moves and abilities

- Attack damage formula factoring in levels, types, IVs, EVs, status effect, etc.

- All IVs are set to 31.

- Fighters, moves, and abilities are loaded in via JSON.

- Type effectiveness chart is loaded in via CSV.

- Cicada Husk Ghost HP limiter

- New moves: [scrape(), analyzed_impale(), Rice Shuriken, Drum Solo, Later Gator]

- New ability: Soup Burst

- View description of a move by typing [number of the move] + i.

  

## To Do ##

- Add more status effects

- Add held items

- Add weather to calculations

- Check the soup burst case where Soup Dumpling's HP is reduced by poison/burn instead of being hit. 

- Upcoming characters: Raghoul (almost done), Forest Lizard



## How To Play ##

Run battle.py in your terminal from this directory.

<br>

`python battle.py`

or

`py battle.py`


## Latest Fixes ##

- Fixed crash when Moxie tries to activate after a U-turn that KOed the opponent and the Moxie user switches in.
- Fixed infinite loop from a tie.
- "Counter" abilities (Soup Burst and eventually Rough Skin) now activate after the healing portion of a healing attack.
- Corrected U-turn behaviour in turn system, so a U-turning opponent would be hit by Soup Burst before returning.