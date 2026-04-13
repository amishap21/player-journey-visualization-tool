# Game Insights from Event Data Analysis

## Insight 1: Severe Map Imbalance - AmbroseValley Dominates Play

**Observation:**
AmbroseValley accounts for 71.1% of all matches played (566 out of 796), while GrandRift only sees 7.4% (59 matches). This is a 9.6:1 ratio between the most and least played maps.

**Supporting evidence:**
- AmbroseValley: 566 matches (71.1%), 268 unique players on AmbroseValley
- Lockdown: 171 matches (21.5%), 120 unique players on Lockdown
- GrandRift: 59 matches (7.4%), 59 unique players on GrandRift

**Why this matters:**
- Players are heavily favoring one map, indicating potential design issues with the other maps
- This imbalance reduces content variety and may lead to player fatigue
- GrandRift may have gameplay issues that make it less appealing

**Actionable items:**
- **Metrics to track:** Map selection rate over time, session duration per map, player retention by map
- **Recommendations:**
  1. Survey players about why they prefer AmbroseValley over other maps
  2. Review GrandRift's spawn points, loot distribution, and terrain for issues
  3. Consider adding map-specific incentives or rewards to encourage rotation
  4. Temporarily boost GrandRift in match rotation to gather more data

**Expected impact:** More balanced map distribution, increased player engagement through variety

---

## Insight 2: Combat is Primarily PvE, Not PvP

**Observation:**
Out of 3,118 combat encounters, only 3 (0.096%) are human-vs-human kills. The vast majority (3,115 encounters, 99.9%) are human-vs-bot combat. This suggests the game feels more like a PvE experience than a competitive PvP game.

**Asumption:**
Players are able to distinguish between bots and humans

**Supporting evidence:**
- BotKill (human killed bot): 2,415 encounters
- BotKilled (bot killed human): 700 encounters
- PvP encounters (human killed human): 3 encounters (3 Kill events paired with 3 Killed events)
- PvP encounter ratio: 0.096% (3 out of 3,118 combat encounters)

**Why this matters:**
- If the game is marketed as a competitive battle royale, the actual gameplay doesn't match
- Low PvP engagement may indicate players are avoiding combat with other humans
- High bot density may be diluting the competitive experience

**Actionable items:**
- **Metrics to track:** PvP kill rate over time, average time between PvP encounters, player feedback on combat satisfaction
- **Recommendations:**
  1. Reduce bot count or make bots more challenging to encourage human engagement
  2. Add incentives for PvP kills (e.g., better loot, score bonuses)
  3. Review matchmaking to ensure more human players are in each match
  4. Consider adding a "hardcore" mode with fewer bots for competitive players

**Expected impact:** Increased PvP engagement, more competitive gameplay feel

---

## Insight 3: Lockdown Has Highest Storm Death Rate Per Match

**Observation:**
Lockdown has the highest storm death rate per match (0.099 deaths per match) compared to AmbroseValley (0.030 deaths per match). Despite having only 30% of the matches of AmbroseValley, Lockdown has the same number of storm deaths, suggesting players are struggling with the storm mechanic on this map specifically.

**Supporting evidence:**
- Lockdown: 17 storm deaths (0.099 per match, 171 total matches)
- AmbroseValley: 17 storm deaths (0.030 per match, 566 total matches)
- GrandRift: 5 storm deaths (0.085 per match, 59 total matches)
- Lockdown's storm death rate is 3.3x higher than AmbroseValley's

**Why this matters:**
- Storm deaths are frustrating for players and reduce enjoyment
- High storm deaths may indicate map design issues (poor cover, long extraction routes)
- This could be driving players away from Lockdown (second least played map)

**Actionable items:**
- **Metrics to track:** Storm death rate per map, average time to extraction, player rage quit rate during storm
- **Recommendations:**
  1. Review Lockdown's extraction points and storm path for design issues
  2. Add more storm shelters or safe zones along extraction routes
  3. Slow down the storm progression on Lockdown specifically
  4. Add visual/audio cues earlier before storm reaches players

**Expected impact:** Reduced storm death rate, improved player satisfaction on Lockdown, increased Lockdown play rate
