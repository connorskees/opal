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
import random
import smtplib
import sys
import time
import warnings
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException


############## TODO: CONVERT TO 2 CLASSES #####################################

# TODO: FORMAT TIME FUNCTION SO THAT IF ITS OVER 24 HOURS IT DOES IT IN DAYS, 3600 SECONDS = HOURS, ETC.
# TODO: opal_email_archive BETTER DATE USE strftime()
# TODO: PRINT ASCII ART MAYBE AT THE START
# TODO: RENAME USED ADJECTIVES CSV TO used_adjectives.csv
# TODO: RENAME --send AND ITS VARIABLES
# TODO: NO WIFI CONTINGENCY (THIS ACTUALLY MIGHT ALREADY EXIST WITH WHILE LOOPS, BUT TEST)
# TODO: --force [FORCE] TO FORCE ADJECTIVE(S) THE FOLLOWING DAY. nargs="+"
# TODO: MAYBE SWITCH THE RANDOM STUFF IN VERSION_NUMBER TO BE CALCULATED BY FUNCTION
# TODO: CREATE ADJECTIVE CSV HEADER AS datetime.now().strftime(YEAR-MONTH-DAY)
# TODO: SHE CANT SEND TWO EMAILS IN ONE DAY (CHECK HER SENT)

EMAILS_DICT = {
    '2020': ["20calhse@kids.udasd.org", "20skeeco@kids.udasd.org", # Searia Calhoun, Connor Skees
             "20etzwem@kids.udasd.org", "20schaha@kids.udasd.org", # Emily Etzweiler, Hannah Schade
             "20ayerma@kids.udasd.org", "20kerwsa@kids.udasd.org", # Macklin Ayers, Sam Kerwin
             "20schima@kids.udasd.org", "20wiesto@kids.udasd.org", # Rosie Schiano, Torie Wiest
             "20fausna@kids.udasd.org", "20smitni@kids.udasd.org", # Nathan Faust, Nick Smith
             "20buffni@kids.udasd.org", "20dunkma@kids.udasd.org", # Nick Buffington, Mason Dunkle
             "20daubka@kids.udasd.org",                            # Kaylob Dauberman
            ],

    '2019': ["19sampca@kids.udasd.org", "19kingza@kids.udasd.org", # Cailen Sample, Zane King
             "19millva@kids.udasd.org", "19lenkle@kids.udasd.org", # Vaughn Miller, Lea Lenker
             "19wolfpr@kids.udasd.org", "19zimmda@kids.udasd.org", # Preston Wolfe, Dane Zimmerman
             "19bordry@kids.udasd.org", "19shadka@kids.udasd.org", # Ryan Bordner, Kaitlyn Shade
             "19woodch@kids.udasd.org", "19welkbr@kids.udasd.org", # Christopher Woodward, Brock W.
             "19raupbe@kids.udasd.org", "19margja@kids.udasd.org", # Betty Raup, Jake Margetanski
             "19roheal@kids.udasd.org", "19tappmy@kids.udasd.org", # Alexia Rohena, Mykenzie Tapper
             "19foxem@kids.udasd.org", "19deibsha@kids.udasd.org", # Emily Fox, Shantel Deibert-Fye
             "19hochka@kids.udasd.org", "19durasa@kids.udasd.org", # Kate Hoch, Samaria Duran
             "19snydde@kids.udasd.org", "19kennzo@kids.udasd.org", # Destin Snyder, Zoe Kennerly
             "19millma@kids.udasd.org",                            # Madison Miller

            ],

    'teachers': ["heathj@udasd.org", "smithv@udasd.org",],         # Mr. Heath, Mrs. Smith

    'other': ["connor1skees@gmail.com",],                          # Connor Skees (personal)

    'debug': ["20skeeco@kids.udasd.org"]                           # Used during --send
}

# Randomly adds one of these if "Holiday Dinner", "Tasty Bites", or "Food Fusion" is in meal
SPECIAL_EVENT_NOUNS = ["You", "Your first born child", "Alex Jones", "Sarah Palin",]

# Emails, duh
EMAILS = set(EMAILS_DICT['2020']+EMAILS_DICT['2019']+EMAILS_DICT['teachers']+EMAILS_DICT['other'])

# used in VERSION_NUMBER. Randomly selected
MEMBER_NAMES = ["Members", "Followers", "Disciples", "True Believers",
                "Enlightened Ones", "Acolytes", "Righteous Ones", "Flat Earthers",
                "Survivors", "Children", "Subscribers",]

# Randomly chooses from here when there is no lunch
NO_LUNCH = ["https://www.youtube.com/watch?v=xO2gkQQ8SB0", "Starve!", "Perish!",
            "Suffer!", "nothing lol",]

# Removes all of th ese suffixes from meal
SUFFIXES = ['Florets', 'on a Bun', 'with Gravy', 'in a Cone', 'on a Stick',
            'with Fresh Bread', 'with Lettuce, Tomato & Sauce', 'w/Lettuce, Tomato & Sauce']

# Removes all of these adjectives from meal
ADJ_REMOVE = ["Bite Sized", "Bold", "Chilled", "Citrusy", "Creamy", "Crispy",
              "Flavorful", "Fresh Sliced", "Freshly Baked", "Garden",
              "Golden", "Home Style", "Homestyle", "Homemade", "Juicy", "Luscious",
              "Orange Kissed", "Oven Baked", "Baked", "Refreshing", "Savory",
              "Seasoned", "Sliced", "Spicy", "Swedish", "Tangy", "Tropical",
              "Warm", "Blended", "Mandarin", "Roasted", "Vegetarian", "Steamed",
              "Soft", "Mediterranean", "Citrus", "Oven", "Crisp",
             ]

# Randomly adds one of these adjectives to each item not in skip
ADJ_ADD = ['100% Real Beef', 'Adequate', 'Aged', 'Ambitious', 'Antimicrobial',
           'Artisinal', 'Average', 'Beefy', 'Berry Berry Delicious',
           'Blood of Opal\'s Enemies Red', 'Buttery',
           'Charming', 'Chewy', 'Comforting', 'Country Fried',
           'Courageous', 'Cream of the Crop', 'Cultured', 'Curdled',
           'Daring', 'Definitely Safe to Eat', 'Edible', 'Enticing',
           'FDA Approved', 'Fermented', 'Fishy', 'Flavorless', 'Freshly Squeezed',
           'Fresh', 'Fruity', 'Full-Bodied', 'Good Enough', 'Gourmet', 'Greasy',
           'Grilled', 'Hairy', 'Hand Picked', 'Hand Squeezed', 'Handcrafted',
           'Heavenly', 'Heterosexual', 'Homogenized', 'Immune Boosting',
           'Inventive', 'Limp', 'Lip Smacking Good', 'Locally Sourced',
           'Luxurious', 'Meaty', 'Mediocre', 'Meticulously Prepared',
           'Moist', 'Mouth Watering', 'Mouth-Watering', 'Nutritious', 'O.K.',
           'Oily', 'Okay', 'Opal\'s Favorite', 'Organic', 'Parisian', 'Passionate',
           'Piping Hot', 'Potent', 'Quaint', 'Questionable', 'Ripe', 'Roasted',
           'Safe', 'Sanitary', 'Satisfactory', 'Scrumdiddlyumptious',
           'Simply Scrumptious', 'Skillfully Prepared', 'Subpar',
           'Succulent', 'Suspiciously Tasty', 'Thick',
           'Packed with necessary vitamins and minerals',
           'You will die if you do not eat this', 'Zesty',
           'Pathetic', 'George Bush\'s', 'Flaccid', 'Biblical', 'Rich in Calcium',
           'Soggy', 'Slimy', 'Veiny', 'Depressing', '6\' 2\"', 'Kafkaesque',
           'Weird', 'Smelly', 'Creamy', 'Mr. Heath\'s', 'Mrs. Smith\'s', 'Brooding',
           'Sinister', 'Heavily Armed', 'Straight from the Cow', '100% Real Pork',
           '100% Real Horse', '100% Fake Beef', '2nd Highest Paid in the District',
           'Cruel', 'Dastardly', 'Porcine', 'Sadistic', 'Masochistic', 'Leftover',
           'ok.. this is Epic:', 'Magically Delicious', 'Gr-r-reat', 'Choosy Mothers Choose',
           'Boneless', 'Bone-Filled', 'Mike Pence\'s', 'Unimaginative', 'Stressful',
           'Stressed', 'Moldy', 'Off-Putting', 'Unpalatable', 'Old', 'Plain',
           'Bland', 'Dry', 'Rad', 'Actually likes talking on the phone',
           'Single Hardworking Mother of 2', 'Proud Conservative Mother of 3',
           'Widowed', 'ANGERY!!', 'Brooding', 'Redneck', "A little hip hop and country",
           'Rusty', 'Wicked Awesome', 'Damp', "😎😎😎"
          ]

# Appended to version number during --send
ERROR_MESSAGE = "\n\nThis is a debug email. Please reply if you were not expecting it."

# Misc stats at the bottom of the meal
VERSION_NUMBER = (f"Opal v2.6.1\nCurrent {random.choice(MEMBER_NAMES)}: {len(EMAILS)}\n"
                  f"Adjectives: {len(ADJ_ADD)}\nLines of Code: {len(open('opal.py').readlines())}")

def main():
    """main() function for CLI"""
    parser = argparse.ArgumentParser()

    parser.add_argument("-d", "--driver", type=str, default="chromedriver.exe", dest="d",
                        help="This is the path of your chrome web driver.")

    parser.add_argument("--time", dest="time", default=7, type=int,
                        help="""Hour for email to be sent at. E.g. 13 will send it
                              at 1pm; 7 will send it at 7am""")

    parser.add_argument("--dry", action="store_true", default=False,
                        help=("The meal will be sent in minimalist form; only "
                              "the words necessary to understanding the food are "
                              "kept. (e.g. Pasta & Meat Sauce | Meatball & "
                              "Mozzarella Hoagie | Green Beans | Salad | Peaches "
                              "| Milk)"))

    ########################### DEBUG ###########################

    parser.add_argument("-e", "--test", "--today", action="store_true", default=False, dest="test",
                        help="Print today's meal to console instead of sending an email.")

    parser.add_argument("-t", "--tomorrow", action="store_true", default=False,
                        help="""Print tomorrow's meal to console instead of sending an email.
                             Basically a shortcut subclass of --custom-date but it's
                             always 1 day in the future.""")

    parser.add_argument("-y", "--yesterday", action="store_true", default=False, dest="yesterday",
                        help="""Print yesterday's meal to console instead of sending an email.
                             Basically a shortcut subclass of --custom-date but it's
                             always 1 day in the past.""")

    parser.add_argument("-a", "--add", type=int, default=None, dest="add",
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


    parser.add_argument("--send", action="store_true",
                        default=False, help="""Send the email no matter time of day.
                                               Does not override --test""")

    parser.add_argument("--used", action="store_true", default=False,
                        help="Show the adjectives used yesterday")

    parser.add_argument("--gui", action="store_true", default=False,
                        help="Show gui when running.")

    args = parser.parse_args()
    sys.stdout.write(str(handle_args(args)))

def start_driver(driver_path, gui):
    """Creates the driver variable and starts selenium"""
    chrome_options = webdriver.ChromeOptions()
    prefs = {'profile.managed_default_content_settings.images':2, 'disk-cache-size':4096}
    chrome_options.add_experimental_option("prefs", prefs)

    # run as headless
    if not gui:
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--window-size=1280,800')
        chrome_options.add_argument('log-level=2')

    driver = webdriver.Chrome(driver_path, chrome_options=chrome_options)
    return driver

def handle_args(args):
    """
    Determines if it should run as a test and which days to scrape.
    Calls the functions real_meal(), test_meal(), meal_range() based on CLI input
    """
    try:
        if args.used:
            # test_adjective_add()
            print_used()
            return ''

        test = any((args.tomorrow, args.date_range, args.custom_date, args.test,
                    args.yesterday, args.add))

        now = datetime.now()
        if args.tomorrow:
            now += timedelta(days=1)
        elif args.yesterday:
            now += timedelta(days=-1)
        elif args.add:
            now += timedelta(days=args.add)
        elif args.custom_date:
            now = datetime(*args.custom_date)
            print(f"Custom date: {now}")

        if not test:
            try:
                start_of_real_meal = time.time()
                real_meal(send_time=args.time, send=args.send, driver_path=args.d, gui=args.gui,
                          dry=args.dry)
            except KeyboardInterrupt:
                if not args.send:
                    total_real_meal_time = round(time.time()-start_of_real_meal, 2)
                    print(f"\n\nRan for {format_seconds(total_real_meal_time)}")

        elif test and not args.date_range:
            test_meal(now=now, driver_path=args.d, gui=args.gui, dry=args.dry)

        elif args.date_range:
            date_range_meal(date_range=args.date_range, driver_path=args.d,
                            gui=args.gui, dry=args.dry)

    except KeyboardInterrupt:
        print("\nInterrupt recieved. Exiting now...")
    return ''

def print_used():
    """
    Print yesterday's adjectives to console
    """
    print("-"*80)
    for adjective in sorted(read_csv("adjectives.csv", flat=True)):
        print(adjective)
    print("-"*80)

def real_meal(send_time, send, driver_path, gui, dry):
    """
    Used for actually sending email

    Args:
        send_time: time for email to be sent (daily)
        send: bool force send email to only EMAILS_DICT['debug']
        driver_path: str path to chrome driver
        gui [debug]: bool run chrome with gui
        dry: bool send the meal without adjectives

    Returns:
        Nothing :)

    Dependencies:
        from datetime import datetime
        import selenium
        from selenium import webdriver
    """
    if send:
        global EMAILS, VERSION_NUMBER
        EMAILS = EMAILS_DICT['debug']
        VERSION_NUMBER += ERROR_MESSAGE

    logged_in = False
    while True:
        now = datetime.now()
        if now.hour != send_time and not send:
            if now.second > 3:
                print(f"Recorrecting seconds (sleeping for {60-now.second} seconds)")
                time.sleep(60-now.second)
                continue
            print(f"{now.hour}h {now.minute}m {now.second}s")
            time.sleep(60)
            continue
        print(time.strftime("%A, %B %d, %Y %H:%M:%S", time.localtime()))

        date = now.strftime("%Y-%m-%d")
        day = now.strftime("%d %a")
        if day.endswith(("Sat", "Sun")):
            print(f"No lunch: Weekend")
            if send:
                break
            print("Sleeping for 1 hour...")
            time.sleep(60*60)
            continue

        url = f"https://udas.nutrislice.com/menu/upper-dauphin-high/lunch/{date}"
        if not logged_in:
            driver = start_driver(driver_path, gui)
        driver.get(url)

        if not logged_in:
            login(driver)
            logged_in = True

        parse_meal(driver=driver, day=day, test=False, dry=dry, send=send)

        if send:
            break
        print("Sleeping for 1 hour...")
        time.sleep(60*60)

def test_meal(now, driver_path, gui, dry):
    """Prints meal to console"""
    start = time.time()
    date = now.strftime("%Y-%m-%d")
    day = now.strftime("%d %a")
    if day.endswith(("Sat", "Sun")):
        print("-"*80)
        print(f"No lunch: Weekend")
        return ''

    url = f"https://udas.nutrislice.com/menu/upper-dauphin-high/lunch/{date}"
    driver = start_driver(driver_path, gui)
    driver.get(url)

    login(driver)

    print("-"*80)
    parse_meal(driver=driver, day=day, test=True, dry=dry)
    print("-"*80)
    print(f"{round(time.time()-start, 3)} seconds")

    return ''

def date_range_meal(date_range, driver_path, gui, dry):
    """
    Prints all meals within range to console.
    Range takes ['YYYY', 'MM', 'DD', 'YYYY', 'MM', 'DD'] format
    """
    start_date = datetime(*date_range[:3])

    end_date = datetime(*date_range[3:])

    if start_date > end_date:
        start_date, end_date = end_date, start_date

    end_date += timedelta(days=1) # increase day to make it include both start and end

    logged_in = False
    start = time.time()
    driver = start_driver(driver_path, gui)

    print(f"Date range: {start_date} to {end_date}")
    print("-"*80)
    while start_date < end_date:
        now = start_date
        date = now.strftime("%Y-%m-%d")
        print(date)
        day = now.strftime("%d %a")

        if day.endswith(("Sat", "Sun")):
            print(f"No lunch: Weekend")
            print(f"{round(time.time()-start, 3)} seconds")
            print("-"*80)
            start_date += timedelta(days=1)
            continue

        url = f"https://udas.nutrislice.com/menu/upper-dauphin-high/lunch/{date}"
        driver.get(url)

        if not logged_in:
            login(driver)
            logged_in = True

        parse_meal(driver=driver, day=day, test=True, dry=dry)
        print(f"{round(time.time()-start, 3)} seconds")
        print("-"*80)
        start_date += timedelta(days=1)

def test_adjective_add(noun="Milk"):
    """Print every adjective with a noun to test for whitespace, spelling, etc."""
    for adj in ADJ_ADD:
        print(f"{adj} {noun}")

    # holding this food variable here for now; ignore :)
    food = [
        'Apple Slices',
        'Applesauce',
        'BBQ Rib Sandwich',
        'Baked Beans',
        'Baked Rigatoni',
        'Beef & Cheese Nachos',
        'Beef & Cheese Soft Tacos',
        'Beef Gyro w/Lettuce, Tomato & Sauce',
        'Beef Gyro with Lettuce, Tomato & Sauce',
        'Bite Sized Popcorn Chicken with Fresh Sliced Bread',
        'Blended Mixed Vegetables',
        'Bold Black Beans',
        'Bread Slice',
        'Broccoli Florets',
        'Buffalo Chicken Dipper with Fresh Sliced Bread',
        'Buffalo Chicken Grilled Cheese',
        'Cheeseburger',
        'Chicken & Cheese Quesadilla with Salsa',
        'Chicken Chips',
        'Chicken Egg Roll',
        'Chili Cheese Bowl with Rice',
        'Chilled Applesauce',
        'Cinnamon Apple Slices',
        'Citrusy Mandarin Oranges',
        'Corn Dog Nuggets',
        'Creamy Baked Scalloped Potatoes',
        'Creamy Mashed Potatoes with Gravy',
        'Crisp Baby Carrots',
        'Crisp Tater Tots',
        'Crispy Chicken Tenders',
        'Diced Pears',
        'Dinner Roll',
        'Early Dismissal-No Lunch',
        'Egg Noodles',
        'Flavorful Vegetarian Beans',
        'Food Fusion',
        'French Toast Sticks & Sausage',
        'Fresh Sliced Bread',
        'Freshly Baked Italian Dunkers',
        'Garden Salad',
        'Garlic Breadstick',
        'Garlic Knots',
        'Golden Corn',
        'Golden Diced Carrots',
        'Grilled Cheese Sandwich',
        'Ham and Cheese on a Pretzel Bun',
        'Holiday Break - No School',
        'Holiday Break-No School',
        'Holiday Dinner',
        'Homemade Lasagna with Fresh Bread',
        'Homestyle Refried Beans',
        'Juicy Apple Slices',
        'Juicy Cheeseburger on a Bun',
        'Juicy Sliced Peaches',
        'Macaroni and Cheese w/Sliced Bread',
        'Meatball & Mozzarella Hoagie',
        'Meatball Hoagie',
        'Memorial Day - No School',
        'Milk',
        "New Year's Day - No School",
        'New Years Eve - No School',
        'No School',
        'No School for MS & HS-Parent Teacher Conferences',
        'No School-Act 80 Day',
        'No School-Faculty In-service',
        'No School-Parent Faculty Conferences',
        'Orange Kissed Chicken Bowl',
        'Pasta & Homemade Meat Sauce with Fresh Bread',
        'Pepperoni Roll',
        'Philly Cheesesteak Sub',
        'Popcorn Chicken Bowl Waffle Cone',
        'Popcorn Chicken Bowl w/Fresh Sliced Bread',
        'Pork BBQ Sandwich',
        'Pork BBQ on a Bun',
        'Pulled Pork BBQ on Bun',
        'Refreshing Fruit Cocktail',
        'Roasted Turkey',
        'Salisbury Steak with Gravy & Sliced Bread',
        'Savory Brown Rice',
        'Seasoned Green Beans',
        'Sliced Ham',
        'Sliced Luscious Strawberries',
        'Soft Beef & Cheese Tacos',
        'Steamed Broccoli',
        'Steamed Carrot Coins',
        'Steamed Carrots',
        'Stewed Tomatoes',
        'Stir-Fry Chicken & Vegetables',
        'Strawberries',
        'Stuffing',
        'Swedish Meatballs over Noodles',
        'Sweet Peas',
        'Tangy BBQ Rib Sandwich',
        'Tasty Bites',
        'Thanksgiving - No School',
        'Thanksgiving Meal',
        'There is currently nothing on the menu today.',
        'Tomato Soup',
        'Tropical Pineapple Tidbits',
        'Turkey Pot Roast w/Sliced Bread',
        'Walking Taco w/ Nacho Doritos',
        'Walking Taco with Beef & Cheese',
        'Walking Taco with Nacho Chips & Fresh Sliced Bread',
        'Warm Apple Crisp',
        'or']

def format_seconds(seconds, rounding=3):
    minute = 60
    hour = minute*60
    day = hour*24
    year = day*365
    if seconds <= minute:
        return f"{seconds} seconds"
    elif minute <= seconds < hour:
        return f"{round(seconds/minute, rounding)} minutes"
    elif hour <= seconds < day:
        return f"{round(seconds/(hour), rounding)} hours"
    elif day <= seconds < year:
        return f"{round(seconds/(day), rounding)} days"
    elif year <= seconds:
        return f"{round(seconds/(60*60*24*365), rounding)} years"

def login(driver):
    """Gets past bot page on website"""
    while True:
        try:
            driver.execute_script("arguments[0].click();",
                                  driver.find_element_by_css_selector("body main div input"))
            driver.find_element_by_css_selector("button.primary").click()
            break
        except NoSuchElementException:
            print("\nNoSuchElementException in login()\n")
            continue
        else:
            break
    return ''

def contains(string, *args):
    """Checks if string contains arbitrary number of arguments"""
    for arg in args:
        if arg in string:
            return True
    return False

def parse_meal(driver, day, test, dry, send=False):
    """Determines if the meal is valid and calls send_email()"""
    time.sleep(int(day[:2])/18)

    meal = find_meal(driver, day)

    if meal.strip() == f"{day}\nLoading Menu":
        driver.refresh()
        time.sleep(2)
        parse_meal(driver, day, test, dry)
        return None

    elif contains(meal.lower(), "no school", "no lunch", "early dismissal", "holiday break"):
        if not dry:
            meal = random.choice(NO_LUNCH)
        else:
            print(f"{meal}\n(no email)")
            return None

    elif not meal.replace(" ", "").replace("\n", ""):
        time.sleep(.5)
        parse_meal(driver, day, test, dry)
        return None

    elif "There is currently nothing on the menu today." in meal:
        print("The lunch hasn't been planned out this far in the future.\n(no email)")
        return None

    meal = clean_meal(meal, day, test, dry, send)#[::-1]

    if test:
        print(meal)

    elif not test:
        print("Sending email...")
        print("-"*80)
        print(meal)
        print("-"*80)
        send_email(subject=f"{day} Lunch", text=meal, recipient=EMAILS,
                   sender="lunchladyopal@gmail.com",
                   password=read_file("password.txt"))
        if not send:
            create_csv([f"{day}\n{meal.replace(VERSION_NUMBER, '').strip()}"], name="opal_email_archive", override=False)
    return True

def clean_meal(meal, day, test, dry, send=False):
    """Cleans meal (replaces adjectives and adds version number)"""
    for adj in SUFFIXES+ADJ_REMOVE:
        if adj == 'Crisp' and meal.find("Apple Crisp") > -1:
            continue
        meal = meal.replace(adj, "")

    if not dry and ("Holiday Dinner" in meal or "Tasty Bites" in meal or "Food Fusion" in meal):
        meal = meal.replace("Milk", f"{random.choice(SPECIAL_EVENT_NOUNS)}\nMilk")

    meal = meal_replacements(meal)
    meal = meal.split("\n")
    meal = [m.strip() for m in meal if m != day]

    skip = ["or", "Recipe of the Month",] + NO_LUNCH + SPECIAL_EVENT_NOUNS

    # add adjective
    if not dry:
        yesterday = read_csv("adjectives.csv", flat=True)
        used = []
        for index, value in enumerate(meal):
            while True:
                if value in skip:
                    break
                choice = random.choice(ADJ_ADD)
                if choice in used or choice in yesterday:
                    if len(used)+len(yesterday) == len(ADJ_ADD):
                        warnings.warn("There are more terms than adjectives")
                        break
                    continue
                meal[index] = choice + " " + value
                used.append(choice)
                break

        if used and not test and not send and not dry:
            create_csv(used, name="adjectives.csv", override=True, verbose=False)

    string_meal = ""
    for line in meal:
        string_meal += (line+"\n")

    string_meal += f"\n{VERSION_NUMBER}"

    string_meal = string_meal.replace("  ", " ").strip()

    return string_meal

def meal_replacements(meal):
    """An extension of clean_meal but contains the manual meal.replace methods"""
    replacements = {
        "Tasty Bites\n": "",
        "Beef Gyro": "Beef Gyro (pronounced yee-ro)",
        "Food Fusion": "Food Fusion:", # makes no sense without colon
        "Popcorn Chicken Bowl Waffle Cone": "Popcorn Chicken in a Waffle Cone",
        "Nacho Doritos": "Doritos",
        "Grilled Cheese Sandwich": "Grilled Cheese", #sandwich is weird to say
        "Milk": "Milk Carton", # avoid "Mrs. Smith's Milk"
        "&": "and", # I *HATE* the ampersand
        "w/": "with", # This abbreviation is annoying
        "Pasta & Meat Sauce": "Pasta with Meat Sauce",
        "Pasta and Meat Sauce": "Pasta with Meat Sauce",
        "Salisbury Steak & Bread": "Salisbury Steak with Bread",
        "Salisbury Steak and Bread": "Salisbury Steak with Bread",
        "No School-": "No School - ",
        "No School for": "No School -",
        "New Year's Day - No School": "No School - New Year's Day",
        "New Years Day - No School": "No School - New Year's Day",
        "New Year's Eve - No School": "No School - New Year's Eve",
        "New Years Eve - No School": "No School - New Year's Eve",
        "Thanksgiving - No School": "No School - Thanksgiving",
        "Memorial Day - No School": "No School - Memorial Day",
        "Holiday Break-No School": "No School - Holiday Break",
        "Holiday Break - No School": "No School - Holiday Break",
        "Early Dismissal-No Lunch": "Early Dismissal",
        "Early Dismissal - No Lunch": "Early Dismissal",
    }

    for key, value in replacements.items():
        meal = meal.replace(key, value)
    return meal

def find_meal(driver, day):
    """Find the meal on the webpage"""
    while True:
        try:
            days = driver.find_elements_by_css_selector("li.day")
            break
        except NoSuchElementException:
            print("\nNoSuchElementException in parse_meal()\n")
        else:
            break

    meal = ""

    for i in days:
        if i.text.startswith(day):
            meal = i.text
            break
    return meal

def send_email(subject, text, recipient, sender, password):
    """Sends email to EMAILS"""
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender
    # msg['To'] = recipient

    part1 = MIMEText(text)
    msg.attach(part1)
    # from email.mime.image import MIMEImage
    # msg.attach(MIMEImage(open(r"C:\Users\Connor\Downloads\fru-fru edited.png", "rb").read()))

    mail = smtplib.SMTP('smtp.gmail.com', 587)


    mail.ehlo()

    mail.starttls()

    mail.login(sender, password)
    mail.sendmail(sender, recipient, msg.as_string())
    mail.quit()

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
            write.writerows([[row]])

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
    with open(file_path, mode='r') as file:
        x = file.read()
        if split_char:
            x = x.split(split_char)
        return x

if __name__ == "__main__":
    main()





#
