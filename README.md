# bbcmd
Command Line Baseball Tools

## Step 1. Download Data

Download the necessary play by play data source files that the simulator depends on to run simulations. These files are stored on github in the [bbsrc](https://github.com/luciancooper/bbsrc) repository. The data in these files is derived from the play by play data provided by [retrosheet.org](https://www.retrosheet.org/). Retrosheet is an amazing organization that has painstakingly compiled the play by play data for every MLB game dating back to 1921. Find out more about the Retrosheet project [here](https://www.retrosheet.org/about.htm).

```bash
bbdata --env years path
```
- `years` - **required**: the specified MLB seasons you wish to download play by play data for, can be a single year (`2016`), range of years (`2014-2016`) or comma separated combination of the two (`2012-2014,2016` or `2012-2014,2015-2017`, etc.)
 - `path` - **optional**: the local path in which you wish to keep store your play by play data files. You will want to remember this location, as you will have to come back later if you want to delete these files. If not specified, the current working directory will be used

## Step 2. Create Data Pointer

```bash
bbdata --xml years path
```
- `years` - **required**: the specified MLB seasons you wish `bbdata.xml` to point to. Can be a single year (`2016`), range of years (`2014-2016`) or comma separated combination of the two (`2012-2014,2016` or `2012-2014,2015-2017`, etc.)
 - `path` - **optional**: the local path in which you wish to create the pointer file in. This is the directory you will be running your simulations in later, so again, remember this location. If not specified, the current working directory will be used. If you want to keep it simple, specify the same path as in the previous command


## Step 3. Test the Simulator

If the current path does not contain your `bbdata.xml` file, navigate to that path. Run the following command, which will simulate the games for all the seasons specified by `bbdata.xml`, without recording any of the data.  
```bash
bbstat -t game
```
