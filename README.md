# bbcmd
Command Line Baseball Tools


# Baseball Simulators
#### `core`
- [ ] `core.GameSim`
- [ ] `core.RosterSim`
 * `core.GameSim`

#### `stats`
- [ ] `stats.SeasonStatSim`
 * `core.GameSim`
- [ ] `stats.RosterStatSim`
 * `player.RosterSim`
   * `core.GameSim`
****
#### `team`
- [x] `team.GameStatSim`
 * `core.GameSim`
- [x] `team.ScoreSim`
 * `core.GameSim`
****
#### `league`
- [x] `league.LeagueStatSim`
 * `stats.SeasonStatSim`
   * `core.GameSim`

#### `woba`
- [x] `woba.wOBAWeightSim`
 * `stats.SeasonStatSim`
   * `core.GameSim`

#### `runexp`
- [x] `runexp.REMSim`
 * `stats.SeasonStatSim`
   * `core.GameSim`

#### `defout`
- [x] `defout.FposOutSim`
 * `stats.RosterStatSim`
   * `player.RosterSim`
     * `core.GameSim`

#### `roster`
- [x] `roster.PIDStatSim`
 * `stats.RosterStatSim`
   * `player.RosterSim`
     * `core.GameSim`
- [x] `roster.PPIDStatSim`
 * `stats.RosterStatSim`
   * `player.RosterSim`
     * `core.GameSim`

#### `appearance`
- [x] `appearance.AppearanceSim`
 * `stats.RosterStatSim`
   * `player.RosterSim`
     * `core.GameSim`
- [x] `appearance.LahmanAppearanceSim`
 * `stats.RosterStatSim`
   * `player.RosterSim`
     * `core.GameSim`



****
## Simulator
* **core.GameSim**
  * `simGame`
  * `simSeason`
  * `simSeasons`
  * `simAll`
  * `_simYears`
  * `_simGamedata`
  * `_simGame`
* **stats.SeasonStatSim**
  * `_simYears`
  * `_simGamedata`
  * *`_frameIndex(years)`*
* **stats.RosterStatSim**
  * `_simYears`
  * `_simGamedata`
  * *`_frameIndex(years)`*
* **team.GameStatSim**
  * `_simYears`
  * *`_frameIndex(years)`*
* **team.ScoreSim**
  * `_simYears`
  * *`_frameIndex(years)`*
* **league.LeagueStatSim**
* **woba.wOBAWeightSim**
  * `_simGamedata`
* **runexp.REMSim**
* **defout.FposOutSim**
* **roster.PIDStatSim**
* **roster.PPIDStatSim**
  * *`_frameIndex(years)`*
* **appearance.AppearanceSim**
* **appearance.LahmanAppearanceSim**


****
## Simulator 2
* **core.GameSim**
  * `_simYears`
  * `_simGamedata`
  * `_simGame`
* **stats.SeasonStatSim**
  * `_simYears`
  * `_simGamedata`
  * *`_frameIndex(years)`*
* **stats.RosterStatSim**
  * `_simYears`
  * `_simGamedata`
  * *`_frameIndex(years)`*
* **team.GameStatSim**
  * `_simYears`
  * *`_frameIndex(years)`*
* **team.ScoreSim**
  * `_simYears`
  * *`_frameIndex(years)`*
* **league.LeagueStatSim**
* **woba.wOBAWeightSim**
  * `_simGamedata`
* **runexp.REMSim**
* **defout.FposOutSim**
* **roster.PIDStatSim**
* **roster.PPIDStatSim**
  * *`_frameIndex(years)`*
* **appearance.AppearanceSim**
* **appearance.LahmanAppearanceSim**
