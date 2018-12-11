# bbcmd

[![PyPI version shields.io](https://img.shields.io/pypi/v/bbcmd.svg)](https://pypi.python.org/pypi/bbcmd/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/bbcmd.svg)](https://pypi.python.org/pypi/bbcmd/)
[![PyPI license](https://img.shields.io/pypi/l/bbcmd.svg)](https://pypi.python.org/pypi/bbcmd/)

Command Line Baseball Data Tools. This project includes 2 command line tools for generating a variety of stats and scraping data from the web.

### Contents
* [Installation](#installation)
* [Scraper](#scraping)
* [Simulator Setup](#simulator_setup)
* [Simulator Usage](#simulator_usage)


# Installation

Use `pip` via [PyPi](https://pypi.org)

```bash
pip install bbcmd
```

**Or** use `git`

```bash
git clone git://github.com/luciancooper/bbcmd.git bbcmd
cd bbcmd
python setup.py install
```
##### Install Notes
This project depends on [cmdprogress](https://github.com/luciancooper/cmdprogress) for command line progress bars

##### Commands
After installation, the `bbsim` and `bbscrape` commands should be in your systems path, via the `Scripts` directory of your Python installation

# Scraper

The `bbscrape` command is a tool that scrapes data from the following websites:
 * [baseball-reference.com](baseball-reference.com)
 * [fangraphs.com](fangraphs.com)
 * [spotrac.com](spotrac.com)


# Simulator Setup

### Step 1. Download Data

Download the necessary play by play data source files that the simulator depends on to run simulations. These files are stored on github in the [bbsrc](https://github.com/luciancooper/bbsrc) repository. The data in these files is derived from the play by play data provided by [retrosheet.org](https://www.retrosheet.org/). Retrosheet is an amazing organization that has painstakingly compiled the play by play data for every MLB game dating back to 1921. Find out more about the Retrosheet project [here](https://www.retrosheet.org/about.htm).

```bash
bbsim setup --env years path
```
 * `years` - **required**: the specified MLB seasons you wish to download play by play data for, can be a single year (`2016`), range of years (`2014-2016`) or comma separated combination of the two (`2012-2014,2016` or `2012-2014,2015-2017`, etc.)
 * `path` - **optional**: the local path in which you wish to keep store your play by play data files. You will want to remember this location, as you will have to come back later if you want to delete these files. If not specified, the current working directory will be used

### Step 2. Create Data Pointer

```bash
bbsim setup --xml years path
```
 * `years` - **required**: the specified MLB seasons you wish `bbdata.xml` to point to. Can be a single year (`2016`), range of years (`2014-2016`) or comma separated combination of the two (`2012-2014,2016` or `2012-2014,2015-2017`, etc.)
 * `path` - **optional**: the local path in which you wish to create the pointer file in. This is the directory you will be running your simulations in later, so again, remember this location. If not specified, the current working directory will be used. If you want to keep it simple, specify the same path as in the previous command


### Step 3. Run a quick test

If the current path does not contain your `bbdata.xml` file, navigate to that path. Run the following command, which will simulate the games for all the seasons specified by `bbdata.xml`, without recording any of the data.  
```bash
bbsim test game
```

# Simulator Usage

The following simulations are currently supported by this project

### Gamescores

The `gamescore` command generates data grouped by mlb game. Columns include:
> `ascore,hscore,aout,hout`

```bash
bbsim gamescore [-v] [-y YEARS]
```


### Generate Aggregated Stats

The `batting`, `fielding`, and `pitching` commands generate aggreated stats. By default, the simulator will group the outputted data by season, unless one of the following optional flags is included:
 * `-l` or `--league` : data is grouped by league (AL and NL).
 * `-t` or `--team` : data is grouped by team
 * `-g` or `--game` : data is grouped by game (like in a box score)


#### `batting` command
The `batting` command generates offensive stats. Columns include:
> `O,E,S,D,T,HR,BB,IBB,HBP,K,I,SH,SF,GDP,R,RBI,SB,CS,PO`

The `batting` command has an additional optional flag: `-np` or `--nopitcher`. If this is included, the simulator will ignore pitchers when aggregating results.

```bash
bbsim batting [-l | -t | -g] [-v] [-np] [-y YEARS]
```

#### `fielding` command

The `fielding` command generates defensive aggregated stats. Columns include:
> `UR,TUR,P,A,E,PB`

```bash
bbsim fielding [-l | -t | -g] [-v] [-y YEARS]
```

#### `pitching` command

The `pitching` command generates aggregated pitching stats. Columns include:
> `W,L,SV,IP,BF,R,ER,S,D,T,HR,BB,HBP,IBB,K,BK,WP,PO,GDP`

```bash
bbsim pitching [-l | -t | -g] [-v] [-y YEARS]
```


### Generate Roster Stats

#### `player` command

Basic Usage:
The player command generates stats that are grouped by player. Each row of outputted data contains a unique, 8 character `playerid` corresponding to an individual. There are currently 4 runnable subcommands:

```bash
bbsim player (batting | fielding | pitching | rbi)  > file.csv
```


The `batting` subcommand generates offensive stats. Outputted data columns include:
> `O,E,S,D,T,HR,BB,IBB,HBP,K,I,SH,SF,GDP,R,RBI,SB,CS,PO`

```bash
bbsim player batting [-v] [-y YEARS] [--handed] > batting_stats.csv
```

The `pitching` subcommand generates pitching stats. Outputted data columns include:
> `W,L,SV,IP,BF,R,ER,S,D,T,HR,BB,HBP,IBB,K,BK,WP,PO,GDP`

```bash
bbsim player pitching [-v] [-y YEARS] [--handed] > stat_file.csv
```

Both the `batting` and `pitching` subcommands have an optional `--handed` flag. If this flag is included, then data will be further grouped by batting hand and pitching hand


The `fielding` subcommand generates defensive stats. Outputted columns include:
> `P,A,E,PB`

```bash
bbsim player fielding [-v] [-y YEARS]
```

The `rbi` subcommand generates details about each event in which a player recieved an RBI.
> `RBI,O,E,S,D,T,HR,BB,IBB,HBP,K,I,SF,SH,GDP`

```bash
bbsim player rbi [-v] [-y YEARS]
```

#### `appearance` command

```bash
bbsim appearance [normal | lahman | position | simple] [-v] [-y YEARS]
```
* `-v` - **optional**:
* `-y YEARS`


### Generate Advanced Stats

```bash
bbsim advcalc (woba | war) [-v] [-y YEARS]
```
