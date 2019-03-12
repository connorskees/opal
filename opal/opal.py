#!/usr/bin/env python
"""
Send an email of today's lunch menu
"""
import argparse
import csv
from datetime import datetime, timedelta
from email.mime.audio import MIMEAudio
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import itertools
import json
import os
from pprint import pprint
import random
import re
from sndhdr import what
import smtplib
import sys
import time
from typing import Dict, List, Optional, Tuple, Union
import warnings

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException


__version__ = "4.2.0"


class Opal:
    """Visits menu hosted online; finds, validates, and cleans meal"""
    def __init__(self,
                 driver_path: str,
                 start_time: int,
                 is_dry: bool,
                 is_test: bool,
                 is_tomorrow: bool,
                 is_yesterday: bool,
                 add_days: Optional[int],
                 custom_date: Optional[Tuple[str, str, str]],
                 forced_adjectives: Optional[List[str]],
                 is_test_email: bool,
                 gui: bool,
                 is_two_hour_delay: bool,
                 is_raw: bool) -> None:

        self.start = time.time()

        if is_tomorrow:
            add_days = 1
        elif is_yesterday:
            add_days = -1
        self.add_days = add_days

        self.driver_path = driver_path
        self.start_time = start_time
        self.is_dry = is_dry
        self.custom_date = custom_date
        self.forced_adjectives = forced_adjectives
        self.is_test_email = is_test_email
        self.gui = gui
        self.is_raw = is_raw

        self.is_test = any((is_test, add_days, custom_date)) and not is_test_email

        self.email_image = "two_hour_delay_schedule.png" if is_two_hour_delay else None

        if is_tomorrow:
            self.add_days = 1
        elif is_yesterday:
            self.add_days = -1

        self.line = "-"*80

        self.meal = ""
        self.driver: webdriver  # defined in start_driver()

        self.special_events = (
            "Holiday Dinner",
            "Tasty Bites",
            "Food Fusion",
        )
        self.special_event_nouns = (
            "You",
            "Your first born child",
            "Alex Jones",
            "Sarah Palin",
            "Egg",
            "George Lopez"
        )

        # no magic strings!
        emails_path = "data/emails.json"
        holidays_path = "data/holidays.json"
        suffixes_remove_path = "data/suffixes_remove.txt"
        adjectives_remove_path = "data/adjectives_remove.txt"
        adjectives_add_path = "data/adjectives_add.txt"

        create_list = lambda path: sorted(read_file(path).split("\n"), key=len, reverse=True)

        with open(holidays_path, mode="r", encoding="utf-8") as holiday_file:
            self.holidays = json.load(holiday_file)

        self.no_lunch_nouns = (
            "Starve!", "suffer.", "nothing lol",
            # Go back to sleep and starve vine
            "https://www.youtube.com/watch?v=xO2gkQQ8SB0",
            # Globgogabgalab
            "https://www.youtube.com/watch?v=_ieCjpmliSg",
            # warm it up thats a 10.exe
            "https://www.youtube.com/watch?v=JbepN4dKLbU",
            # Bev 'N' Bob Wake Me Up Inside
            "https://www.youtube.com/watch?v=4Kc4Np1rdPc",
            # Pokemon go to the polls
            "https://www.youtube.com/watch?v=vwaiyjh1dGk",
        )

        self.suffixes_remove = create_list(suffixes_remove_path)
        self.suffixes_add = ()

        self.adjectives_remove = create_list(adjectives_remove_path)
        self.adjectives_add = create_list(adjectives_add_path)

        with open(emails_path, mode="r", encoding="utf-8") as email_file:
            self.emails_dict = {key: set(value) for key, value in json.load(email_file).items()}

        self._validate_emails(self.emails_dict)
        self.emails = (
            set()
            | self.emails_dict['2021']
            | self.emails_dict['2020']
            | self.emails_dict['2019']
            | self.emails_dict['teachers']
            | self.emails_dict['other']
        )

        if self.is_test_email:
            self.emails = self.emails_dict['debug']

        self.debug_email_message = ""
        if not self.is_test and self.is_test_email:
            self.debug_email_message = (
                "<br />"
                "<br />"
                "This is a debug email."
                " Please reply if you were not expecting it."
                "<br />"
                f"Sent to {self.emails}"
            )

        url_date = self.now.strftime("%Y-%m-%d")
        self.base_url = f"https://udas.nutrislice.com/menu/upper-dauphin-high/lunch/"
        self.url = f"{self.base_url}{url_date}"

    def __del__(self) -> None:
        try:
            self.driver.quit()
        except AttributeError:
            pass
        print(f"Ran for {self.time_ran}")

    def start_driver(self) -> webdriver:
        """Creates the driver variable and starts selenium"""
        options = webdriver.ChromeOptions()
        prefs = {
            'profile.managed_default_content_settings.images': 2,
            'disk-cache-size': 4096
        }
        options.add_experimental_option("prefs", prefs)

        # run as headless
        if not self.gui:
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.add_argument('--window-size=1280,800')
            options.add_argument('--log-level=3')

        driver = webdriver.Chrome(self.driver_path, options=options)
        return driver

    def print_used(self) -> None:
        """
        Print yesterday's adjectives to console
        """
        used = sorted(read_csv("used_adjectives.csv", flat=True))
        adjectives = "\n".join(adj for adj in used)
        print(f"{self.line}\n{adjectives}\n{self.line}")

    @staticmethod
    def _contains(string: str, *args) -> bool:
        """Checks if string contains arbitrary number of arguments"""
        for arg in args:
            if arg in string:
                return True
        return False

    @staticmethod
    def _validate_emails(emails_dict: dict) -> None:
        """Validate emails in self.emails_dict. Prints emails with issues"""
        length_exceptions = ("19foxem@kids.udasd.org",
                             "19deibsha@kids.udasd.org")

        # uses `print()` instead of `warnings.warn()` because I feel it is
        # easier to immediately read which emails are invalid

        for key, value in emails_dict.items():
            for email in value:
                if key.startswith("20"):
                    if not email.startswith(key[2:]):
                        print((f"\nWARNING --|{email}|-- does not match "
                               "the year\n"))
                    elif len(email) != 23 and email not in length_exceptions:
                        print((f"\nWARNING --|{email}|-- has an irregular "
                               "length and is not listed as an exception\n"))
                    elif not email.endswith("@kids.udasd.org"):
                        print((f"\nWARNING --|{email}|-- is not a "
                               "kids.udasd.org email\n"))

                elif key == 'teachers':
                    if not email.endswith("udasd.org"):
                        print((f"\nWARNING --|{email}|-- is not a udasd.org "
                               "email\n"))
                    elif len(email) != 16 and email not in length_exceptions:
                        print((f"\nWARNING --|{email}|-- has an irregular"
                               "length and is not listed as an exception\n"))

    @staticmethod
    def _format_seconds(seconds: Union[int, float], rounding: int = 3) -> str:
        """
        Returns time formatted in a nicer format than '56007 seconds'

        Args:
            seconds: int or float Number of seconds
            rounding: int decimal place to round to

        Returns:
            str Time formatted with most suitable time unit

        Imports:
            none
        """
        # pylint: disable=R1705
        if seconds < 0:
            raise ValueError("`seconds` cannot be less than 0.")

        minute = 60
        hour = minute*60
        day = hour*24
        year = day*365
        if seconds < minute:
            return f"{round(seconds, rounding)} seconds"
        elif minute <= seconds < hour:
            return f"{round(seconds/minute, rounding)} minutes"
        elif hour <= seconds < day:
            return f"{round(seconds/(hour), rounding)} hours"
        elif day <= seconds < year:
            return f"{round(seconds/(day), rounding)} days"
        return f"{round(seconds/(year), rounding)} years"

    @property
    def time_ran(self) -> str:
        """Returns time run"""
        return self._format_seconds(time.time() - self.start)

    @property
    def now(self) -> datetime:
        """Returns datetime to get lunch from"""
        current_time = datetime.now()
        if self.add_days:
            return current_time + timedelta(days=self.add_days)
        if self.custom_date:
            return datetime(*self.custom_date)
        return current_time

    @property
    def day(self) -> str:
        """Return self.now in `%d %a` form (ex. 03 Mon, 17 Tue, etc.)"""
        return self.now.strftime("%d %a")

    @property
    def fancy_date(self) -> str:
        """Return self.now in `%B %d, %Y` form (ex. FEBRUARY 4, 2019)"""
        return self.now.strftime("%B %d, %Y").replace(" 0", " ").upper()

    @property
    def timestamp(self) -> str:
        """Return current time in str YYYY-MM-DD form"""
        return datetime.now().strftime('%Y-%m-%d')

    @property
    def is_weekend(self) -> bool:
        """Return true if the current day of the week is saturday or sunday"""
        return self.now.weekday() in (5, 6)

    def login(self, verbose: bool = True) -> None:
        """Gets past bot page on website"""
        self.driver = self.start_driver()
        driver = self.driver
        driver.get(self.url)
        counter = 0
        while self.driver.current_url != self.url:
            counter += 1
            if counter >= 10:
                counter = 0
                driver.refresh()
                time.sleep(.5)
            try:
                # there used to be a terms and services checkbox
                # below is the code for it:
                # terms = driver.find_element_by_css_selector("main div input")
                # driver.execute_script("arguments[0].click();", terms)
                driver.find_element_by_css_selector("button.primary").click()
                break
            except NoSuchElementException:
                if verbose:
                    print("NoSuchElementException in login()")
                continue

    def find_meal(self):
        """Find the meal on the webpage"""
        time.sleep(int(self.day[:2])/18)

        old_date = datetime.strptime(self.url, f"{self.base_url}%Y-%m-%d")
        if old_date.month != self.now.month:
            url_date = self.now.strftime("%Y-%m-%d")
            new_url = f"{self.base_url}{url_date}"
            if self.driver.current_url != new_url:
                self.url = f"{self.base_url}{url_date}"
                self.driver.get(self.url)
                time.sleep(int(self.day[:2])/18)

        while True:
            try:
                days = self.driver.find_elements_by_css_selector("li.day")
                break
            except NoSuchElementException:
                print("\nNoSuchElementException in parse_meal()\n")
            else:
                break

        for i in days:
            if i.text.startswith(self.day):
                self.meal = i.text
                break

    def validate_meal(self) -> bool:
        """Determines if the meal exists and is usable"""
        day = self.day
        meal = self.meal
        driver = self.driver
        no_lunch_signifiers = (
            "no school",
            "no lunch",
            "early dismissal",
            "holiday break",
        )

        if meal.strip() == f"{day}\nLoading Menu" or not meal.strip():
            driver.refresh()
            time.sleep(2)
            return False

        if self._contains(meal.lower(), *no_lunch_signifiers):
            if not self.is_dry:
                self.meal = random.choice(self.no_lunch_nouns)
            else:
                print(f"{self.meal}\n(no email)")
                return False

        elif "There is currently nothing on the menu today." in meal:
            print(("The lunch hasn't been planned out this far in the future."
                   "\n(no email)"))
            return False
        return True

    def clean_meal(self) -> None:
        """Makes changes to meal"""
        if not self.is_raw:
            self.remove_adjectives_and_suffixes()
            if not self.is_dry:
                self.add_special_events()
            self.meal_replacements()

            self.meal = [m.strip() for m in self.meal.split("\n") if m != self.day]

            if not self.is_dry:
                self.add_adjectives()

            self.meal = "\n".join(self.meal)
            self.meal = self.meal.replace("  ", " ").strip()
            if not self.is_test:
                self.meal = self.meal.replace("\n", "<br />")

    def remove_adjectives_and_suffixes(self) -> None:
        """Removes adjectives and suffixes"""
        for adj in sorted((*self.suffixes_remove, *self.adjectives_remove),
                          key=len, reverse=True):
            if adj == "Crisp" and self.meal.find("Apple Crisp") > -1:
                continue
            self.meal = self.meal.replace(adj, "")

    def add_special_events(self) -> None:
        """Adds special event nouns if special event"""
        for event in self.special_events:
            if event in self.meal:
                random_noun = random.choice(self.special_event_nouns)
                self.meal = self.meal.replace("Milk", f"{random_noun}\nMilk")

    def meal_replacements(self) -> None:
        """
        These are meal replacements that target specific food items.
        They have been added over time as weirdly worded foods were found
        and reworded for clarity.

        These replacements are made before adjectives are added and during
        dry meals.
        """
        replacements = {
            # I *HATE* the ampersand
            "&": "and",

            # This abbreviation is annoying
            "w/": "with",

            # there should be a space here
            "w/Bread": "with Bread",
            "w/Nacho": "with Nacho",

            # 'tasty bites' makes no sense to me
            "Tasty Bites\n": "",

            # often mispronounced :)
            "Beef Gyro": "Beef Gyro (pronounced yee-ro)",

            # what
            "Hot Sicilian Melt": "Hot Sicilian Melt (whatever that is?)",

            # makes no sense without colon
            "Food Fusion": "Food Fusion:",

            # 'nacho' is redundant and misleading (nacho flavored)
            "Nacho Doritos": "Doritos",

            # `sandwich` is weird to say
            "Grilled Cheese Sandwich": "Grilled Cheese",

            # avoid "Mrs. Smith's Milk"
            "Milk": "Milk Carton",

            # more natural with 'with' than 'and'
            "Pasta & Meat Sauce": "Pasta with Meat Sauce",
            "Salisbury Steak & Bread": "Salisbury Steak with Bread",

            # this is weirdly worded
            "Turkey Bacon Club Pretzel Melt": "Turkey and Bacon Pretzel Melt",
            "Beef & Cheese Walking w/Nacho Doritos": ("Beef & Cheese Walking T"
                                                      "aco w/ Nacho Doritos"),
            "Popcorn Chicken Bowl Waffle Cone": "Popcorn Chicken in a Waffle Cone",
            "Nachos Waffle Cone": "Nachos in a Waffle Cone",

            # sounds nicer (even though 'tidbits' is the brand name)
            "Pineapple Tidbits": "Pineapple Bites",

            # standardize no lunch meals for potential future use
            "No School-": "No School:",
            "No School for": "No School:",
            "New Year's Day - No School": "No School: New Year's Day",
            "New Years Day - No School": "No School: New Year's Day",
            "New Year's Eve - No School": "No School: New Year's Eve",
            "New Years Eve - No School": "No School: New Year's Eve",
            "Thanksgiving - No School": "No School: Thanksgiving",
            "Memorial Day - No School": "No School: Memorial Day",
            "Holiday Break-No School": "No School: Holiday Break",
            "Holiday Break - No School": "No School: Holiday Break",
            "Early Dismissal-No Lunch": "Early Dismissal",
            "Early Dismissal - No Lunch": "Early Dismissal",
            "No School-Faculty In-service": "No School: Faculty In-Service",
        }

        self.meal = replace_all(self.meal, replacements)

    def add_adjectives(self) -> None:
        """Randomly assigns adjectives to each food item"""
        skip = ("or", "Recipe of the Month", "\n",
                *self.no_lunch_nouns,
                *self.special_event_nouns)
        f_adj = self.forced_adjectives
        for holiday in self.holidays:
            if holiday in ''.join(self.meal):
                self.adjectives_add = self.holidays[holiday]['adjectives']
                break
        adjectives_add = self.adjectives_add

        adjectives_yesterday: List[str] = read_csv("used_adjectives.csv", flat=True)
        adjectives_used: List[str] = []
        for index, value in enumerate(self.meal):
            while True:
                if value in skip:
                    break
                choice = random.choice(adjectives_add)
                # `adjectives_used` doesn't include adjectives_yesterday because
                # adjectives_used is put into csv later
                if choice in adjectives_used + adjectives_yesterday:
                    if len(adjectives_used)+len(adjectives_yesterday) >= len(adjectives_add):
                        warnings.warn("There are more terms than adjectives")
                        break
                    continue
                if self.is_test:
                    self.meal[index] = f"{choice} {value}"
                else:
                    self.meal[index] = f"<strong>{choice}</strong> {value}"
                adjectives_used.append(choice)
                break

        # so this block of code is a real mess and needs to be refactored
        # first, it removes adjectives not in the normal list
        # then, it removes extra adjectives and zips with already used adjs
        # replaces the already used adjectives and re splits
        # it's for forcing adjectives
        if f_adj and adjectives_used:
            f_adj = [adj for adj in f_adj if adj in adjectives_add][:len(adjectives_used)]
            self.meal = "\n".join(self.meal)
            for used, forced in zip(adjectives_used, f_adj):
                self.meal = self.meal.replace(used, forced)
            self.meal = self.meal.split("\n")

        if adjectives_used and not any((self.is_test, self.is_test_email, self.is_dry)):
            create_csv(data=[self.timestamp]+adjectives_used,
                       name="used_adjectives.csv",
                       override=True,
                       verbose=False)

    def add_forced_adjectives(self) -> None:
        """Adds forced adjectives"""

    def send_email(self, video_path: str = None) -> None:
        """
        Send an email

        Args:
            subject: str email subject
            text: str email text
            recipients: str or list of str recipients of email
            sender: str Email to be sent from
            password: str Sender's password
            video_path: str Path to video file to attach

        Returns:
            None

        Imports:
            from email.mime.multipart import MIMEMultipart
            from email.mime.audio import MIMEAudio
            from email.mime.image import MIMEImage
            from email.mime.text import MIMEText
            import smtplib
            import os
            from sndhdr import what
        """
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"{self.day} Lunch"
        msg['From'] = "lunchladyopal@gmail.com"

        template_replacements = {
            "{MEAL}": self.meal,
            "{DATE}": self.fancy_date,
            "{DAY}": self.day,
            "{VERSION}": __version__,
            "{DEBUG_MESSAGE}": self.debug_email_message
        }

        html_template: str = read_file("dirty-template.html")

        template = replace_all(html_template, template_replacements)

        part1 = MIMEText(template, 'html')
        msg.attach(part1)

        if self.email_image is not None:
            try:
                image = MIMEImage(read_file(self.email_image))
                image.add_header('Content-Disposition',
                                 'attachment',
                                 filename=os.path.basename(self.email_image))
                msg.attach(image)
            except FileNotFoundError:
                warnings.warn('Unable to attach image because the file was not '
                              'found.')

        if video_path is not None:
            video = MIMEAudio(read_file(video_path), _subtype=what(video_path))
            video.add_header('Content-Disposition',
                             'attachment',
                             filename=os.path.basename(video_path))
            msg.attach(video)


        mail = smtplib.SMTP('smtp.gmail.com', 587)

        mail.ehlo()

        mail.starttls()

        mail.login("lunchladyopal@gmail.com", read_file("password.txt"))
        mail.sendmail("lunchladyopal@gmail.com", self.emails, msg.as_string())
        mail.quit()

    def test_adjective_add(self, noun: str = "Milk") -> None:
        """
        Print every adjective with a noun to test for whitespace, spelling, etc
        """
        noun_w_adj = '\n'.join(f'{adj} {noun}' for adj in self.adjectives_add)
        print(f"{self.line}\n{noun_w_adj}\n{self.line}")

    def exit_driver(self) -> bool:
        """Exit driver (really only used to exit during unit testing)"""
        if self.driver:
            self.driver.quit()
            return True
        return False

def main() -> None:
    """main() function for CLI"""
    parser = argparse.ArgumentParser()

    parser.add_argument("-d", "--driver", type=str, default="chromedriver.exe", dest="driver_path",
                        help="This is the path of your chrome web driver.")

    parser.add_argument("--time", dest="start_time", default=7, type=int,
                        help="""Hour for email to be sent at. E.g. 13 will send it
                              at 1pm; 7 will send it at 7am""")

    parser.add_argument("--dry", action="store_true", default=False, dest="is_dry",
                        help=("The meal will be sent in minimalist form; only "
                              "the words necessary to understanding the food are "
                              "kept. (e.g. Pasta & Meat Sauce | Meatball & "
                              "Mozzarella Hoagie | Green Beans | Salad | Peaches "
                              "| Milk)"))

    ########################### DEBUG ###########################

    parser.add_argument("-e", "--test", "--today", action="store_true", default=False,
                        dest="is_test",
                        help="Print today's meal to console instead of sending an email.")

    parser.add_argument("-t", "--tomorrow", action="store_true", default=False, dest="is_tomorrow",
                        help="""Print tomorrow's meal to console instead of sending an email.
                             Basically a shortcut subclass of --custom-date but it's
                             always 1 day in the future.""")

    parser.add_argument("-y", "--yesterday", action="store_true", default=False,
                        dest="is_yesterday",
                        help="""Print yesterday's meal to console instead of sending an email.
                             Basically a shortcut subclass of --custom-date but it's
                             always 1 day in the past.""")

    parser.add_argument("-a", "--add", type=int, default=None, dest="add_days",
                        help="""Go n number of days into the future. Can also be
                                negative to go into the past""")

    parser.add_argument("--custom-date", "--custom_date", nargs="+", dest="custom_date",
                        default=None, type=int,
                        help="""Print a custom date's meal to console instead of
                                sending an email. Format: YYYY MM DD Example:
                                --custom-date 2019 01 17""")

    parser.add_argument("--force", nargs="+", dest="forced_adjectives",
                        default=None, type=str,
                        help="""Force the adjectives for the coming day""")

    parser.add_argument("--send", action="store_true", dest="is_test_email",
                        default=False, help="Send a debug email.")

    parser.add_argument("--used", "--show-used", "--used-adjectives",
                        action="store_true", default=False, dest="show_used",
                        help="Show the adjectives used yesterday.")

    parser.add_argument("--emails", "--show-emails", action="store_true",
                        default=False, dest="show_emails",
                        help="Print email dict to console.")

    parser.add_argument("--test-adjectives", action="store_true",
                        default=False, dest="test_adjectives",
                        help="Test all adjectives against noun.")

    parser.add_argument("--gui", action="store_true", default=False, dest="gui",
                        help="Show gui when running.")

    parser.add_argument("--delay", action="store_true", default=False,
                        dest="is_two_hour_delay", help="Show gui when running.")

    parser.add_argument("--raw", action="store_true", default=False,
                        dest="is_raw", help="Give raw meal with no edits.")

    args = parser.parse_args()
    sys.stdout.write(str(handle_args(args)))

def handle_args(args) -> str:
    """
    Determines if it should run as a test and which days to scrape.
    Calls the functions real_meal(), test_meal(), meal_range() based on CLI input
    """
    try:
        opal_args = vars(args).copy()
        opal_args.pop("show_used")
        opal_args.pop("test_adjectives")
        opal_args.pop("show_emails")
        opal = Opal(**opal_args)

        if args.show_used:
            opal.print_used()
            quit()
        elif args.test_adjectives:
            opal.test_adjective_add()
            quit()
        elif args.show_emails:
            pprint(opal.emails_dict)
            quit()

        if not opal.is_test:
            real_meal(opal)

        elif opal.is_test:
            test_meal(opal)

    except KeyboardInterrupt:
        print("\nInterrupt recieved. Exiting now...")
    return ''  # print nothing to console

def real_meal(opal: Opal) -> None:
    """Used for actually sending email"""
    opal.login()
    while True:
        if opal.now.hour != opal.start_time and not opal.is_test_email:
            if opal.now.second > 1:
                print(("Recorrecting seconds (sleeping for "
                       f"{60-opal.now.second} seconds)"))
                time.sleep(60-opal.now.second)
                continue
            print(f"{opal.now.hour}h {opal.now.minute}m {opal.now.second}s")
            time.sleep(60)
            continue

        if opal.is_weekend:
            print(f"{opal.line}\nNo lunch: Weekend\n(no email)\n{opal.line}")
            if opal.is_test_email:
                break
            time.sleep(60*60)
            continue

        opal.find_meal()

        while not opal.validate_meal():
            print("Invalid meal.. restarting")
            opal.find_meal()
        opal.clean_meal()
        opal.send_email()
        print(f"\nEmail successfully sent at {datetime.now()}")
        print(f"{opal.line}\n{opal.meal}\n{opal.line}")
        if opal.is_test_email:
            break
        create_csv([f"{opal.timestamp}\n{opal.meal.strip()}"],
                   name="opal_email_archive", override=False, verbose=False)
        print("Sleeping for 1 hour...")
        time.sleep(60*60)

def test_meal(opal: Opal) -> None:
    """Prints meal to console"""
    if opal.is_weekend:
        print(f"{opal.line}\nNo lunch: Weekend\n{opal.line}")
        quit()

    opal.login()
    print(opal.line)
    opal.find_meal()
    while not opal.validate_meal():
        print("Invalid meal.. restarting")
        opal.find_meal()
    opal.clean_meal()
    print(opal.meal)
    print(opal.line)

def create_csv(data, **kwargs):
    """
    Creates a csv based on data given

    Args:
        data: data in form of iterable
        name: name of file
        header: column header
        override: delete data in file before writing
        path: path for file (does not include file name)
        run: run file after creation

    Imports:
        import csv
        import os
        import time
        import warnings
    """

    name = kwargs.get('name', "d.csv")
    header = kwargs.get('header', None)
    override = kwargs.get('override', False)
    path = kwargs.get('path', None)
    run = kwargs.get('run', False)
    verbose = kwargs.get('verbose', True)

    if not data:
        try:
            warnings.warn("There is nothing to make a csv with.")
        except ImportError:
            print("There is nothing to make a csv with.")

    if verbose:
        print("\nCreating file...")

    if not path:
        path = os.getcwd()
    os.chdir(path)

    if not name.endswith(".csv"):
        name += ".csv"

    if header:
        data.insert(0, header)

    mode = "a" if (not override and os.path.exists(os.path.join(path, name))) else "w"

    with open(name, mode, newline='') as open_csv:
        write = csv.writer(open_csv, delimiter=',', dialect='excel')
        for row in data:
            try:
                write.writerows([[row]])
            except UnicodeEncodeError as unicode_exception:
                warnings.warn(str(unicode_exception))
                write.writerows([[]])

    file_size = f"{round(os.path.getsize(name)/1000)}KB"

    if verbose:
        print(f"csv creation successful:\n\tFile Name: {name}\n\tPath: {path}\n\tSize: {file_size}")

    if run:
        os.popen(f"{name}")

def read_csv(csv_file: str, flat: bool = False) -> Union[List[List[str]], List[str]]:
    """
    Read data from csv

    Args:
        csv_file: str path to csv file to read
        flat: bool choose whether or not to preserve rows and columns

    Returns:
        list containing all data in a csv

    Imports:
        import csv
        import os
        import warnings
    """
    if not csv_file.endswith(".csv"):
        csv_file = f"{csv_file}.csv"

    if os.path.exists(csv_file):
        with open(csv_file, "r") as file:
            data = [x for x in csv.reader(file)]
            if flat:
                data = [i for i in itertools.chain.from_iterable(data)]
            return data
    else:
        warnings.warn(f"Could not locate '{csv_file}'")
        # it shouldn't prevent the email even if it can't find the file
        return [[]]

def read_file(path_to_file: str) -> Union[bytes, str]:
    """
    Read file and return it as str

    Args:
        file_path: str Path to file

    Returns:
        str data within file
    """
    try:
        with open(path_to_file, mode='r', encoding='utf-8') as file:
            return file.read()
    except (TypeError, UnicodeDecodeError):
        with open(path_to_file, mode='rb') as file:
            return file.read()

def replace_all(string: str, replacements: Dict[str, str]):
    """
    Replace all instances

    Args:
        string: str to be replaced
        replacements: dict with keys to be replaced by values

    Returns:
        str with all replacements made

    Dependencies:
        import re
    """
    substrs = sorted(replacements, key=len, reverse=True)
    regexp = re.compile('|'.join((re.escape(s) for s in substrs)))
    return regexp.sub(lambda match: replacements[match.group(0)], string)

if __name__ == "__main__":
    main()
