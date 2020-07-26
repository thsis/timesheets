import os
from configobj import ConfigObj
from datetime import date
from utilities import get_project_root, get_config


def _create_section(**kwargs):
    out = dict(**kwargs)
    return out


def _ask(question, answer_type=str, default=None, prompt=">:"):
    display = f"{question}[{default}]" if default is not None else question
    print(display)
    while True:
        try:
            answer = input(prompt)
            answer = answer if answer != '' else default
            return answer_type(answer)
        except ValueError:
            print(f"could not interpret your answer as {answer_type.__name__}")
            continue


def _create_setup_section():
    first_name = _ask("What is your first name?")
    last_name = _ask("What is your last name?")
    position = _ask("What is your position?", default="SHK")
    supervisor = _ask("What is your supervisor's last name?", default="Greven")
    total_hours = _ask("How many hours do you work each month?", int, 40)
    year = _ask("Which year would you like to configure?", int, date.today().year)
    setup = _create_section(first_name=first_name.capitalize(),
                            last_name=last_name.capitalize(),
                            position=position,
                            supervisor=supervisor.capitalize(),
                            total_hours=total_hours, year=year)
    return setup


def _create_fill_subsection():
    avoid_weekends, max_overtime, max_undertime = False, 0, 0
    fill_missing = _ask("Should we fill out missing hours randomly? (True/False)", bool, False)
    if fill_missing:
        avoid_weekends = _ask("Should we avoid filling hours on the weekend? (True/False)", bool, False)
        max_overtime = _ask("What is your maximum number of hours of overtime?", int, 3)
        max_undertime = _ask("What is your maximum number of hours of undertime?", int, 3)

    fill = _create_section(fill_missing=fill_missing,
                           avoid_weekends=avoid_weekends,
                           max_overtime=max_overtime,
                           max_undertime=max_undertime)
    return fill


def configure():
    config = ConfigObj()
    config.filename = os.path.join(get_project_root(), "config.ini")
    setup = _create_setup_section()
    fill = _create_fill_subsection()
    general = get_config("general")
    config["setup"] = setup
    config["general"] = general
    config["fill"] = fill
    config.write()


