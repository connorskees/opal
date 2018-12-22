#!/usr/bin/env python
"""
Send an email of today's lunch menu
"""
import argparse
import csv
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import itertools
import os
from pprint import pprint
import random
import smtplib
import sys
import time
import warnings
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException


# TODO: better handling of validate_emails
# TODO: holiday adjectives


class Opal:
    """Visits menu hosted online; finds, validates, and cleans meal"""
    def __init__(self,
                 driver_path,
                 start_time,
                 is_dry,
                 is_test,
                 is_tomorrow,
                 is_yesterday,
                 add_days,
                 custom_date,
                 forced_adjectives,
                 date_range,
                 is_test_email,
                 gui):

        self.start = time.time()

        self.driver_path = driver_path
        self.start_time = start_time
        self.is_dry = is_dry
        self.is_test = is_test
        self.add_days = add_days
        self.custom_date = custom_date
        self.forced_adjectives = forced_adjectives
        self.date_range = date_range
        self.is_test_email = is_test_email
        self.gui = gui

        if is_tomorrow:
            self.add_days = 1
        elif is_yesterday:
            self.add_days = -1

        self.line = "-"*80

        self.meal = ""
        self.driver = "" # defined in start_driver()

        self.special_events = ("Holiday Dinner", "Tasty Bites", "Food Fusion")
        self.special_event_nouns = ("You", "Your first born child", "Alex Jones", "Sarah Palin",)

        self.member_names = ("Members", "Followers", "Disciples", "True Believers",
                             "Enlightened Ones", "Acolytes", "Righteous Ones", "Flat Earthers",
                             "Survivors", "Children", "Subscribers",)

        self.no_lunch_nouns = ("https://www.youtube.com/watch?v=xO2gkQQ8SB0", "Starve!",
                               "suffer.", "nothing lol",)

        self.suffixes_remove = ('Florets', 'on a Bun', 'with Gravy', 'in a Cone',
                                'on a Stick', 'with Fresh Bread',
                                'with Lettuce, Tomato & Sauce',
                                'w/Lettuce, Tomato & Sauce')
        self.suffixes_add = ()

        self.adjectives_remove = ("Bite Sized", "Bold", "Chilled", "Citrusy",
                                  "Creamy", "Crispy", "Flavorful", "Fresh Sliced",
                                  "Freshly Baked", "Garden", "Golden", "Home Style",
                                  "Homestyle", "Homemade", "Juicy", "Luscious",
                                  "Orange Kissed", "Oven Baked", "Baked", "Refreshing",
                                  "Savory", "Seasoned", "Sliced", "Spicy", "Swedish",
                                  "Tangy", "Tropical", "Warm", "Blended", "Mandarin",
                                  "Roasted", "Vegetarian", "Steamed", "Soft",
                                  "Mediterranean", "Citrus", "Oven", "Crisp",
                                 )
        self.adjectives_add = ('100% Real Beef', 'Adequate', 'Aged', 'Ambitious',
                               'Antimicrobial', 'Artisinal', 'Average', 'Beefy',
                               'Berry Berry Delicious', 'Blood of Opal\'s Enemies Red',
                               'Buttery', 'Charming', 'Chewy', 'Comforting',
                               'Country Fried', 'Courageous', 'Cream of the Crop',
                               'Cultured', 'Curdled', 'Daring', 'Definitely Safe to Eat',
                               'Edible', 'Enticing', 'FDA Approved', 'Fermented',
                               'Fishy', 'Flavorless', 'Freshly Squeezed', 'Fresh',
                               'Fruity', 'Full-Bodied', 'Good Enough', 'Gourmet',
                               'Greasy', 'Grilled', 'Hairy', 'Hand Picked',
                               'Hand Squeezed', 'Handcrafted', 'Heavenly',
                               'Heterosexual', 'Homogenized', 'Immune Boosting',
                               'Inventive', 'Limp', 'Lip Smacking Good',
                               'Locally Sourced', 'Luxurious', 'Meaty',
                               'Mediocre', 'Meticulously Prepared', 'Moist',
                               'Mouth Watering', 'Mouth-Watering', 'Nutritious',
                               'O.K.', 'Oily', 'Okay', 'Opal\'s Favorite',
                               'Organic', 'Parisian', 'Passionate', 'Piping Hot',
                               'Potent', 'Quaint', 'Questionable', 'Ripe', 'Roasted',
                               'Safe', 'Sanitary', 'Satisfactory',
                               'Scrumdiddlyumptious', 'Simply Scrumptious',
                               'Skillfully Prepared', 'Subpar', 'Succulent',
                               'Suspiciously Tasty', 'Thick',
                               'Packed with necessary vitamins and minerals',
                               'You will die if you do not eat this', 'Zesty',
                               'Pathetic', 'George Bush\'s', 'Flaccid', 'Biblical',
                               'Rich in Calcium', 'Soggy', 'Slimy', 'Veiny',
                               'Depressing', '6\' 2\"', 'Kafkaesque', 'Weird',
                               'Smelly', 'Creamy', 'Mr. Heath\'s', 'Mrs. Smith\'s',
                               'Brooding', 'Sinister', 'Heavily Armed',
                               'Straight from the Cow', '100% Real Pork',
                               '100% Real Horse', '100% Fake Beef',
                               '2nd Highest Paid in the District', 'Cruel',
                               'Dastardly', 'Porcine', 'Sadistic', 'Masochistic',
                               'Leftover', 'ok.. this is Epic:', 'Magically Delicious',
                               'Gr-r-reat', 'Choosy Mothers Choose', 'Boneless',
                               'Bone-Filled', 'Mike Pence\'s', 'Unimaginative',
                               'Stressful', 'Stressed', 'Moldy', 'Off-Putting',
                               'Unpalatable', 'Old', 'Plain', 'Bland', 'Dry', 'Rad',
                               'Actually likes talking on the phone',
                               'Single Hardworking Mother of 2',
                               'Proud Conservative Mother of 3', 'Widowed',
                               'ANGERY!!', 'Brooding', 'Redneck',
                               'A little hip hop and country', 'Rusty', 'Wicked Awesome',
                               'Damp', 'Socially Inadequate', 'Wet', 'Musty',
                               'Crusty',
                              )

        self.emails_dict = {
            '2020': ["20calhse@kids.udasd.org", # Searia Calhoun
                     "20skeeco@kids.udasd.org", # Connor Skees
                     "20etzwem@kids.udasd.org", # Emily Etzweiler
                     "20schaha@kids.udasd.org", # Hannah Schade
                     "20ayerma@kids.udasd.org", # Macklin Ayers
                     "20kerwsa@kids.udasd.org", # Sam Kerwin
                     "20schima@kids.udasd.org", # Rosie Schiano
                     "20wiesto@kids.udasd.org", # Torie Wiest
                     "20fausna@kids.udasd.org", # Nathan Faust
                     "20smitni@kids.udasd.org", # Nick Smith
                     "20buffni@kids.udasd.org", # Nick Buffington
                     "20dunkma@kids.udasd.org", # Mason Dunkle
                     "20daubka@kids.udasd.org", # Kaylob Dauberman
                     "20mattka@kids.udasd.org", # Kade Matter
                    ],

            '2019': ["19sampca@kids.udasd.org", # Cailen Sample
                     "19kingza@kids.udasd.org", # Zane King
                     "19millva@kids.udasd.org", # Vaughn Miller
                     "19lenkle@kids.udasd.org", # Lea Lenker
                     "19wolfpr@kids.udasd.org", # Preston Wolfe
                     "19zimmda@kids.udasd.org", # Dane Zimmerman
                     "19bordry@kids.udasd.org", # Ryan Bordner,
                     "19shadka@kids.udasd.org", # Kaitlyn Shade
                     "19woodch@kids.udasd.org", # Christopher Woodward
                     "19welkbr@kids.udasd.org", # Brock Welker
                     "19raupbe@kids.udasd.org", # Betty Raup
                     "19margja@kids.udasd.org", # Jake Margetanski
                     "19roheal@kids.udasd.org", # Alexia Rohena
                     "19tappmy@kids.udasd.org", # Mykenzie Tapper
                     "19foxem@kids.udasd.org",  # Emily Fox
                     "19deibsha@kids.udasd.org",# Shantel Deibert-Fye
                     "19hochka@kids.udasd.org", # Kate Hoch
                     "19durasa@kids.udasd.org", # Samaria Duran
                     "19snydde@kids.udasd.org", # Destin Snyder
                     "19kennzo@kids.udasd.org", # Zoe Kennerly
                     "19millma@kids.udasd.org", # Madison Miller
                    ],

            'teachers': ["heathj@udasd.org",    # Mr. Heath
                         "smithv@udasd.org",    # Mrs. Smith
                        ],

            'other': ["connor1skees@gmail.com", # Connor Skees (personal)
                      "bettyraup@gmail.com",    # Betty Raup (personal)
                     ],

            'debug': ["20skeeco@kids.udasd.org"]}# Used during --send
        self.validate_emails(self.emails_dict)
        self.emails = set(self.emails_dict['2020'] +
                          self.emails_dict['2019'] +
                          self.emails_dict['teachers'] +
                          self.emails_dict['other'])

        debug_email_message = ("\n\nThis is a debug email. Please reply if you "
                               "were not expecting it.")
        self.version_number = (f"\nOpal v3.2.0"
                               f"\nCurrent {self.random_member_name}: {len(self.emails)}"
                               f"\nAdjectives: {len(self.adjectives_add)}"
                               f"\nLines of Code: {len(open('opal.py').readlines())}"
                               f"\nFind out more here: https://github.com/ConnorSkees/opal")

        if self.is_test_email:
            self.version_number += debug_email_message
            self.emails = self.emails_dict['debug']

        self.is_test = any((self.is_test, self.add_days, self.custom_date, self.date_range))

        url_date = self.now.strftime("%Y-%m-%d")
        self.url = f"https://udas.nutrislice.com/menu/upper-dauphin-high/lunch/{url_date}"

        self.is_weekend = True if self.day.endswith(("Sat", "Sun")) else False

    def __del__(self):
        try:
            self.driver.quit()
        except AttributeError:
            pass
        print(f"Ran for {self.time_ran}")

    def start_driver(self):
        """Creates the driver variable and starts selenium"""
        options = webdriver.ChromeOptions()
        prefs = {'profile.managed_default_content_settings.images':2, 'disk-cache-size':4096}
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

    @staticmethod
    def contains(string, *args):
        """Checks if string contains arbitrary number of arguments"""
        for arg in args:
            if arg in string:
                return True
        return False

    @staticmethod
    def print_used():
        """
        Print yesterday's adjectives to console
        """
        adjectives = "\n".join(adj for adj in sorted(read_csv("used_adjectives.csv", flat=True)))
        line = "-"*80
        print(f"{line}\n{adjectives}\n{line}")

    @staticmethod
    def validate_emails(emails_dict: dict):
        """Validate emails in emails_dict. Prints emails with issues"""
        length_exceptions = ("19foxem@kids.udasd.org", "19deibsha@kids.udasd.org")

        for key, value in emails_dict.items():
            for email in value:
                if key.startswith("20"):
                    if not email.startswith(key[2:]):
                        print(f"\nWARNING --|{email}|-- does not match the year\n")
                    elif len(email) != 23 and email not in length_exceptions:
                        print((f"\nWARNING --|{email}|-- has an irregular length and"
                               " is not listed as an exception\n"))
                    elif not email.endswith("@kids.udasd.org"):
                        print(f"\nWARNING --|{email}|-- is not a kids.udasd.org email\n")

                elif key == 'teachers':
                    if not email.endswith("udasd.org"):
                        print(f"\nWARNING --|{email}|-- is not a udasd.org email\n")
                    elif len(email) != 16 and email not in length_exceptions:
                        print((f"\nWARNING --|{email}|-- has an irregular length and"
                               " is not listed as an exception\n"))

    @staticmethod
    def format_seconds(seconds, rounding=3):
        """
        Returns time formatted in a nicer format than '56007 seconds'

        Args:
            seconds: int|float Number of seconds
            rounding: int decimal place to round to

        Returns:
            str Time formatted with most suitable time unit

        Dependencies:
            none
        """
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
    def random_member_name(self):
        """Return a random member name"""
        return random.choice(self.member_names)

    @property
    def time_ran(self):
        """Returns time run"""
        return self.format_seconds(time.time() - self.start)

    @property
    def now(self):
        """Returns datetime to get lunch from"""
        current_time = datetime.now()
        if self.add_days:
            return current_time + timedelta(days=self.add_days)
        elif self.custom_date:
            return datetime(*self.custom_date)
        return current_time

    @property
    def day(self):
        """Return the self.now in dd weekday (ex. 03 Mon, 17 Tue, 28 Wed, etc.)"""
        return self.now.strftime("%d %a")

    @property
    def timestamp(self):
        """Return current time in str YYYY-MM-DD form"""
        return datetime.now().strftime('%Y-%m-%d')

    def login(self, verbose=True):
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
                # below is the code for it
                # terms_checkbox = driver.find_element_by_css_selector("body main div input")
                # driver.execute_script("arguments[0].click();", terms_checkbox)
                driver.find_element_by_css_selector("button.primary").click()
                break
            except NoSuchElementException:
                if verbose:
                    print("NoSuchElementException in login()")
                continue

    def find_meal(self):
        """Find the meal on the webpage"""
        time.sleep(int(self.day[:2])/18)

        old_date = datetime.strptime(self.url, "https://udas.nutrislice.com/menu/upper-dauphin-high/lunch/%Y-%m-%d")
        if old_date.month != self.now.month:
            url_date = self.now.strftime("%Y-%m-%d")
            new_url = f"https://udas.nutrislice.com/menu/upper-dauphin-high/lunch/{url_date}"
            if self.driver.current_url != new_url:
                self.url = f"https://udas.nutrislice.com/menu/upper-dauphin-high/lunch/{url_date}"
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

    def validate_meal(self):
        """Determines if the meal exists and is usable"""
        day = self.day
        meal = self.meal
        driver = self.driver

        if meal.strip() == f"{day}\nLoading Menu" or not meal.strip():
            driver.refresh()
            time.sleep(2)
            return False

        elif self.contains(meal.lower(), "no school", "no lunch", "early dismissal", "holiday break"):
            if not self.is_dry:
                self.meal = random.choice(self.no_lunch_nouns)
            else:
                print(f"{self.meal}\n(no email)")
                return False

        elif "There is currently nothing on the menu today." in meal:
            print("The lunch hasn't been planned out this far in the future.\n(no email)")
            return False
        return True

    def clean_meal(self):
        """Makes changes to meal"""
        self.remove_adjectives_and_suffixes()
        self.add_special_events()
        self.meal_replacements()

        self.meal = [m.strip() for m in self.meal.split("\n") if m != self.day]

        self.add_adjectives()

        self.meal = "\n".join(self.meal)
        self.meal += f"\n{self.version_number}"
        self.meal = self.meal.replace("  ", " ").strip()

    def remove_adjectives_and_suffixes(self):
        """Removes adjectives and suffixes"""
        for adj in self.suffixes_remove+self.adjectives_remove:
            if adj == "Crisp" and self.meal.find("Apple Crisp") > -1:
                continue
            self.meal = self.meal.replace(adj, "")

    def add_special_events(self):
        """Adds special event nouns if special event"""
        if not self.is_dry:
            for event in self.special_events:
                if event in self.meal:
                    random_noun = random.choice(self.special_event_nouns)
                    self.meal = self.meal.replace("Milk", f"{random_noun}\nMilk")

    def meal_replacements(self):
        """Makes manual replacements for clarity"""
        replacements = {
            "Tasty Bites\n": "", # 'tasty bites' makes no sense to me
            "Beef Gyro": "Beef Gyro (pronounced yee-ro)",
            "Food Fusion": "Food Fusion:", # makes no sense without colon
            "Popcorn Chicken Bowl Waffle Cone": "Popcorn Chicken in a Waffle Cone",
            "Nacho Doritos": "Doritos",
            "Grilled Cheese Sandwich": "Grilled Cheese", #sandwich is weird to say
            "Milk": "Milk Carton", # avoid "Mrs. Smith's Milk"
            "&": "and", # I *HATE* the ampersand
            "w/": "with", # This abbreviation is annoying
            "Pasta and Meat Sauce": "Pasta with Meat Sauce",
            "Salisbury Steak and Bread": "Salisbury Steak with Bread",
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
        }

        for original, replacement in replacements.items():
            self.meal = self.meal.replace(original, replacement)

    def add_adjectives(self):
        """Randomly assigns adjectives to each food item"""
        skip = ("or", "Recipe of the Month",) + self.no_lunch_nouns + self.special_event_nouns
        f_adj = self.forced_adjectives
        adjectives_add = self.adjectives_add

        # add adjective
        if not self.is_dry:
            adjectives_yesterday = read_csv("used_adjectives.csv", flat=True)
            adjectives_used = []
            for index, value in enumerate(self.meal):
                while True:
                    if value in skip:
                        break
                    choice = random.choice(adjectives_add)
                    # adjectives_used does not include adjectives_yesterday because
                    # adjectives_used is put into csv later
                    if choice in adjectives_used + adjectives_yesterday:
                        if len(adjectives_used)+len(adjectives_yesterday) == len(adjectives_add):
                            warnings.warn("There are more terms than adjectives")
                            break
                        continue
                    self.meal[index] = choice + " " + value
                    adjectives_used.append(choice)
                    break

            # so this block of code is a real mess and needs to be refactored
            # first, it removes adjectives not in the normal list
            # then, it removes extra adjectives and zips with already used adjs
            # replaces the already used adjectives and re splits
            if f_adj and adjectives_used:
                f_adj = [adj for adj in f_adj if adj in adjectives_add][:len(adjectives_used)]
                self.meal = "\n".join(self.meal)
                for used, forced in zip(adjectives_used, f_adj):
                    self.meal = self.meal.replace(used, forced)
                self.meal = self.meal.split("\n")

            if adjectives_used and not self.is_test and not self.is_test_email and not self.is_dry:
                create_csv(data=[self.timestamp]+adjectives_used,
                           name="used_adjectives.csv",
                           override=True,
                           verbose=False)

    def add_forced_adjectives(self):
        """Adds forced adjectives"""

    def send_email(self):
        """Sends email"""
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"{self.day} Lunch"
        msg['From'] = "lunchladyopal@gmail.com"

        part1 = MIMEText(self.meal)
        msg.attach(part1)

        mail = smtplib.SMTP('smtp.gmail.com', 587)


        mail.ehlo()

        mail.starttls()

        mail.login("lunchladyopal@gmail.com", read_file("password.txt"))
        mail.sendmail("lunchladyopal@gmail.com", self.emails, msg.as_string())
        mail.quit()

    def test_adjective_add(self, noun="Milk"):
        """Print every adjective with a noun to test for whitespace, spelling, etc."""
        noun_w_adj = '\n'.join(f'{adj} {noun}' for adj in self.adjectives_add)
        print(f"{self.line}\n{noun_w_adj}\n{self.line}")

    def exit_driver(self):
        """Exit driver (really only used to exit during unit testing)"""
        if self.driver:
            self.driver.quit()
            return True
        return False

def main():
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

    parser.add_argument("--date-range", "--date_range", nargs="+", dest="date_range",
                        default=None, type=int,
                        help="""Print the meal for all dates within the range to
                                console instead of sending an email. Format: YYYY MM DD
                                YYYY MM DD Example: --date-range 2019 01 17 2019 01 20""")


    parser.add_argument("--send", action="store_true", dest="is_test_email",
                        default=False, help="Send a debug email.")

    parser.add_argument("--used", "--show-used", action="store_true", default=False,
                        dest="show_used", help="Show the adjectives used yesterday.")

    parser.add_argument("--emails", "--show-emails", action="store_true", default=False,
                        dest="show_emails", help="Print email dict to console.")

    parser.add_argument("--test-adjectives", action="store_true", default=False,
                        dest="test_adjectives", help="Test all adjectives against noun.")

    parser.add_argument("--gui", action="store_true", default=False, dest="gui",
                        help="Show gui when running.")

    args = parser.parse_args()
    sys.stdout.write(str(handle_args(args)))

def handle_args(args):
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
    return ''

def real_meal(opal: Opal):
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
        create_csv([f"{opal.timestamp}\n{opal.meal.replace(opal.version_number, '').strip()}"],
                   name="opal_email_archive", override=False, verbose=False)
        print("Sleeping for 1 hour...")
        time.sleep(60*60)

def test_meal(opal: Opal):
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

    Dependencies:
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

def read_csv(csv_file, flat=False):
    """
    Read data from csv

    Args:
        csv_file: str path to csv file to read
        flat: bool choose whether or not to preserve rows and columns

    Returns:
        list containing all data in a csv

    Dependencies:
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
        return [[]] # it shouldn't prevent the email even if it can't find the file

def read_file(file_path, split_char=None):
    """Read a text file"""
    with open(file_path, mode='r') as file:
        data = file.read()
        if split_char:
            data = data.split(split_char)
        return data

if __name__ == "__main__":
    main()





#
