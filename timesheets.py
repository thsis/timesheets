import argparse
from utilities import configure
from writer import Writer


def fill(args):
    writer = Writer(args.file)
    writer.fill(args.year, args.month)
    if not args.blind:
        writer.check()
    writer.convert()


DESCRIPTION = """
The tediousness of filling timesheets has finally ended. Now you can automatically:
fill your timesheet for a specific month, convert it to a pdf and store it 
- in the correct naming convention - in the 'archive' directory.
"""

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    subparsers = parser.add_subparsers()

    configure_parser = subparsers.add_parser('configure', description="set up the configuration file")
    configure_parser.set_defaults(func=configure)

    fill_parser = subparsers.add_parser('fill', description="fill the timesheet")
    fill_parser.set_defaults(func=fill)
    fill_parser.add_argument("file", help="path to spreadsheet")
    fill_parser.add_argument("year", help="year to fill", type=int)
    fill_parser.add_argument("month", help="month to fill, needs to be an integer, i.e. January=1", type=int)
    fill_parser.add_argument("-b", "--blind", default=False, action="store_true",
                             help="don't check the spreadsheet before saving")

    arguments = parser.parse_args()
    print(arguments)
    arguments.func(arguments)
