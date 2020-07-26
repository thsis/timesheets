# `timesheets` - Automatically fill HU Chair of Statistics timesheets

Are you tired of filling in your timesheets? Every month you punch in the numbers into an Excel-file and you just can't stand it anymore? Don't worry anymore because you do not have to do that any longer!

This little time-saver is designed to read in the especially obnoxious timesheets at the Humboldt University's chair of statistics. You can now:
- fill in your regular hours - especially tutorials are repeated every week, now `timesheets` can do that for you!
- automatically convert the spreadsheet to a PDF with the correct naming convention applied completely automatically. Yes, there is a naming convention for these files and you just never bothered. Why start now? Leave it to `timesheets`!
- and if your regular hours don't cut it, didn't you just type in something entirely random because you didn't remember the last time your worked for the chair? We've all been there - but now `timesheets` can take over this part. Remember you're not lying to the Chair of Statistics if a robot did it!

## Installing the module

1. clone the repo
2. create an environment
  ```sh
  python3 -m venv env
  ```
3. activate it (this depends on your platform - so you need to find out for yourself, [here](https://docs.python.org/3/library/venv.html) is a good start)
4. install the submodules locally
  ```sh
  pip install -e .
  ```
 ## Set up the Chair's Spreadsheet
 
If you haven't done it already, now is a good time to download the newest Chair of Statistics timesheet spreadsheet, save it in this directory and fill in the first worksheet with your name, the year and your position.

If your current spreadsheet already contains values, don't worry. You can simply move it into this directory and continue with it - as is.
 
 ## Create a configuration file
 
 Simply run the command:
 
 ```sh
 python3 timesheets.py configure
 ```
 and follow the instructions.
 
 ## Fill your timesheet
 
 From now on you can create a ready-to-be-uploaded PDF file documenting your possibly imaginary work hours with one command. Let's say my worksheet spreadsheet is called `Gleitzeiterfassung_SHK_2020.xlsx` and I wanted to fill the August of the year 2020:
 ```
 python3 timesheets.py fill Gleitzeiterfassung_SHK_2020.xlsx 2020 1
 ```
 will do the trick. The generated file will be saved in the `archives` directory.
