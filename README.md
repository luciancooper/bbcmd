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


### Step 3. Run a test

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

The `batting`, `fielding`, `pitching`, and `rbi` commands generate aggregated stats. By default, the simulator will group the outputted data by season. The following optional flags will change how the data is grouped.
 * `-l` : by league (AL and NL).
 * `-t` : by team
 * `-g` : by game
 * `-p` : by player (8 character playerid)
 * `-ph` : by player hand (batting hand or pitching hand)
 * `-phm` : by player hand matchups

#### `batting` command

The `batting` command generates offensive stats. Columns include:
> `O,E,S,D,T,HR,BB,IBB,HBP,K,I,SH,SF,GDP,R,RBI,SB,CS,PO`

The `batting` command has an additional optional flag: `-np` or `--nopitcher`. If this is included, the simulator will ignore pitchers when aggregating results.

```bash
bbsim batting [-l | -t | -g | -p | -ph | -phm] [-v] [-np] [-y YEARS]
```

#### `fielding` command

The `fielding` command generates defensive aggregated stats. Columns include:
> `UR,TUR,P,A,E,PB`

```bash
bbsim fielding [-l | -t | -g | -p] [-v] [-y YEARS]
```

#### `pitching` command

The `pitching` command generates aggregated pitching stats. Columns include:
> `W,L,SV,IP,BF,R,ER,S,D,T,HR,BB,HBP,IBB,K,BK,WP,PO,GDP`

```bash
bbsim pitching [-l | -t | -g | -p | -ph | -phm] [-v] [-y YEARS]
```

#### `rbi` command

The `rbi` command generates details about each event in which an RBI was credited
> `RBI,O,E,S,D,T,HR,BB,IBB,HBP,K,I,SF,SH,GDP`

```bash
bbsim rbi [-l | -t | -g | -p | -ph | -phm] [-v] [-y YEARS]
```

### Generate Appearance Stats

#### `appearance` command

```bash
bbsim appearance [normal | lahman | position | simple] [-v] [-y YEARS]
```
* `-v` - **optional**:
* `-y YEARS`


### Generate Advanced Stats

Currently two sub commands supported:
 * woba: simulates the seasonal linear weights used for calculating weighted 
```bash
bbsim advcalc (woba | war) [-v] [-y YEARS]
```
