import os
import sys
import re
import shutil
import numpy as np
import openpyxl
from openpyxl.styles import Font, Alignment
from PyPDF2 import PdfFileWriter, PdfFileReader

from utilities import get_config, get_project_root
from schedule import Schedule, MONTHS_REV

CONFIG = get_config()
ORIENTATION = {"vertical": np.array([1, 0]),
               "horizontal": np.array([0, 1])}
OPPOSITE_ORIENTATION = {"vertical": np.array([0, 1]),
                        "horizontal": np.array([1, 0])}


def convert_cell_position(cell):
    pattern = re.compile(r"([A-Z]+)(\d+)")
    match = re.match(pattern, cell)
    col_string = match.group(1)
    row_string = match.group(2)
    col = sum((ord(c) - 64)*26**i for i, c in enumerate(col_string[::-1]))
    row = int(row_string)
    return np.array([row, col])


class Writer:
    font = Font(name='Arial', size=10, bold=False, italic=False,
                vertAlign=None, underline='none', strike=False,
                color='FF000000')

    align_right = Alignment(horizontal='right',
                            vertical='top')

    def __init__(self, filename):
        self.filename = filename
        self.year, self.month, self.month_name, self.sheet = None, None, None, None
        self.anchor = convert_cell_position(CONFIG["general"]["start_cell"])
        self.orientation = ORIENTATION[CONFIG["general"]["orientation"]]
        self.opposite_orientation = OPPOSITE_ORIENTATION[CONFIG["general"]["orientation"]]
        self.wb = openpyxl.load_workbook(filename=self.filename)

    def fill(self, year, month):
        """fill sheet with schedule."""
        self.year = year
        self.month = month
        self.month_name = MONTHS_REV[self.month]
        self.sheet = self.wb[self.month_name]

        schedule = self.__get_schedule(self.year, self.month)
        self.__write(schedule)

    @staticmethod
    def __get_schedule(year, month):
        schedule = Schedule()
        reg = schedule.fill(year, month)
        if CONFIG["fill"]["fill_missing"]:
            reg = schedule.autocomplete(reg)
        return reg

    def __update_cell(self, pos, value, mode="time"):
        row, col = pos
        cell = self.sheet.cell(row=row, column=col)
        cell.value = value
        if mode == "time":
            cell.number_format = 'hh:mm'
            cell.font = self.font
            cell.alignment = self.align_right

    def __get_positions(self, days):
        anchor, orient, opposite = self.anchor, self.orientation, self.opposite_orientation
        pos_start = anchor + orient * days
        pos_end = anchor + orient * days + opposite * int(CONFIG["general"]["time_end_offset"])
        pos_note = anchor + orient * days + opposite * int(CONFIG["general"]["notes_offset"])
        return pos_start, pos_end, pos_note

    def __write(self, schedule):
        for i, data in schedule.iterrows():
            pos_start, pos_end, pos_note = self.__get_positions(i.day)
            self.__update_cell(pos_start, value=data.activity_start)
            self.__update_cell(pos_end, value=data.activity_end)
            self.__update_cell(pos_note, value=data.note, mode="text")
        self.wb.save(self.filename)

    def check(self):
        """open file to allow for corrections."""
        try:
            if sys.platform == "windows":
                cmd = f"start EXCEL.EXE {self.filename}"
            else:
                cmd = f"libreoffice {self.filename}"
            os.system(cmd)
        except Exception as e:
            raise e

    def __get_pdf_name(self):
        position = CONFIG["setup"]["position"]
        supervisor = CONFIG["setup"]["supervisor"]
        last_name = CONFIG["setup"]["last_name"]
        outfile = f"{position}_{supervisor}_{last_name}_{self.year}{self.month:02d}.pdf"
        return os.path.join(get_project_root(), "archive", outfile)

    def __prepare(self):
        basename = os.path.basename(self.filename)
        command = f"libreoffice --headless --convert-to pdf {basename} --outdir ephm"
        os.system(command)

    def __clean_up(self):
        shutil.rmtree("ephm")

    def convert(self):
        """convert sheet to pdf."""
        self.__prepare()
        basename = os.path.basename(self.filename.replace(".xlsx", ".pdf"))
        filename = os.path.join("ephm", basename)
        outfile = self.__get_pdf_name()
        output = PdfFileWriter()

        with open(filename, "rb") as input_file:
            input_doc = PdfFileReader(input_file)

            pageNumber = self.month + int(CONFIG["general"]["pdf_page_offset"])
            page = input_doc.getPage(pageNumber=pageNumber)
            output.addPage(page)

            with open(outfile, "wb") as output_file:
                output.write(output_file)
        self.__clean_up()


if __name__ == "__main__":
    fn = os.path.join(get_project_root(), "Gleitzeiterfassung_SHK_2019_1.xlsx")
    writer = Writer(fn)
    writer.fill(2019, 1)
    writer.convert()

