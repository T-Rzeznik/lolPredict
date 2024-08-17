Purpose
---------------
To try to understand how the early game(first 4 minutes) jungler/jungle stragegy affects the outcome of the game.
Target variable being if they win the game or not

Important Variables may be whiether the jungler gets first blood or not, thier gold income, what jungle item they start, or how many jungle camps they clear.



About this Dataset
-----------------------
This dataset was produced utilizing the Riot Games API to extract certain game events and stats about the player, specifically the player who is playing the role 'Jungle' in each game.

All ~3000 games recorded are from emerald ranked players.

For each player used to collect data from, their last 10 games were recorded.

Since there are more than one game type in League of Legends the dataset records these.
For variable consistency, we want to only look at Ranked Solo/Duo ranked games - (players tend to competetively try to win games rather than the other gamemodes)
So you will have to do some data cleaning already to filter out unwanted gamemodes. Note: Ranked flex should not be included and is largely different than Ranked Solo/Duo.

If you are inclined to use the other gamemodes such as Normal Draft or Ranked Flex, you can do so though they are not the main purpose of this dataset.


Some variables that may need explaining
--------------------------------------
kills_details - Consists of a list of the timestamps of all the kills they got within the first 4 minutes of the game

level_at_first_blood - When first blood happens during the game, what level was the jungler

camps_cleared_first_4_min - Junglers have to clear jungle camps to earn gold and xp, though this takes time away from ganking / making plays

gold_earned_first_4_min - This metric is important because when players earn more gold, they are able to buy more items and become stronger than thier opponents

summoner_spells - Every player must pick 2 summoner spells going into each game, the jungler should always take smite, leaving the second summoner spell up to variable. Some summoner spells give aggressive advantages while others give defensive advatages, and some spells such as flash are always good.

Here is a list of the summoner spell ids:

11 - Smite

1 - Cleanse

21 - Barrier

14 - Ignite

3 - Exhaust

4 - Flash

6 - Ghost

7 - Heal

12 - teleport
