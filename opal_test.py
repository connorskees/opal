"""
Unit test opal.py
"""
import time
import unittest
import opal

class MockDriver:
    """Contains the same methods as a driver, but doesn't require starting selenium"""
    def __init__(self):
        """init"""

    def refresh(self):
        """Normally refreshes browser page"""

    def quit(self):
        """normally ends driver"""

TEST_OPAL = opal.Opal(driver_path="chromedriver.exe",
                      start_time=0,
                      is_dry=False,
                      is_test=True,
                      is_tomorrow=False,
                      is_yesterday=False,
                      add_days=None,
                      custom_date=[2018, 12, 17],
                      forced_adjectives=None,
                      is_test_email=False,
                      gui=False)


class TestOpal(unittest.TestCase):
    """General test class for Opal"""
    def test_login(self):
        """Determine if it can make it past the checkbox"""
        TEST_OPAL.login(verbose=False)
        self.assertEqual(TEST_OPAL.driver.current_url, TEST_OPAL.url)
        TEST_OPAL.exit_driver()

    def test_find_meal(self):
        """Determine if it can correctly locate the appropriate meal"""
        TEST_OPAL.login(verbose=False)
        time.sleep(6)
        expected_meal = ("17 Mon"
                         "\nChicken Chips"
                         "\nFresh Sliced Bread"
                         "\nTangy BBQ Rib Sandwich"
                         "\nBaked Beans"
                         "\nRefreshing Fruit Cocktail"
                         "\nMilk")
        TEST_OPAL.find_meal()
        self.assertEqual(expected_meal, TEST_OPAL.meal)
        TEST_OPAL.meal = "test_find_meal"
        TEST_OPAL.exit_driver()

    def test_repeatable_meals(self):
        """Determine if it can correctly run over multiple days"""
        TEST_OPAL.login(verbose=False)
        time.sleep(6)

        TEST_OPAL.custom_date = [2018, 12, 18]
        expected_meal = ("18 Tue"
                         "\nFrench Toast Sticks & Sausage"
                         "\nMeatball & Mozzarella Hoagie"
                         "\nCrisp Tater Tots"
                         "\nGarden Salad"
                         "\nCitrusy Mandarin Oranges"
                         "\nMilk")
        TEST_OPAL.find_meal()
        self.assertEqual(expected_meal, TEST_OPAL.meal)

        TEST_OPAL.custom_date = [2018, 12, 19]
        expected_meal = ("19 Wed"
                         "\nBeef & Cheese Nachos"
                         "\nPork BBQ Sandwich"
                         "\nGolden Corn"
                         "\nDiced Pears"
                         "\nMilk")
        TEST_OPAL.find_meal()
        self.assertEqual(expected_meal, TEST_OPAL.meal)
        TEST_OPAL.exit_driver()

    def test_validate_meal(self):
        """Determine if it correctly recognizes good and bad meals"""
        fake_driver = MockDriver()
        TEST_OPAL.driver = fake_driver

        TEST_OPAL.meal = f"{TEST_OPAL.day}\nLoading Menu"
        self.assertFalse(TEST_OPAL.validate_meal())

        TEST_OPAL.meal = ""
        self.assertFalse(TEST_OPAL.validate_meal())

        TEST_OPAL.meal = ("17 Mon"
                          "\nChicken Chips"
                          "\nFresh Sliced Bread"
                          "\nTangy BBQ Rib Sandwich"
                          "\nBaked Beans"
                          "\nRefreshing Fruit Cocktail"
                          "\nMilk")
        self.assertTrue(TEST_OPAL.validate_meal())

    def clean_meal(self):
        """Determine if it is properly cleaning the meals"""
        raw_food = [
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
        dry_food = ["Apple Slices",
                    "Applesauce",
                    "BBQ Rib Sandwich",
                    "Beans",
                    "Rigatoni",
                    "Beef and Cheese Nachos",
                    "Beef and Cheese Tacos",
                    "Beef Gyro (pronounced yee-ro)",
                    "Beef Gyro (pronounced yee-ro)",
                    "Popcorn Chicken with Bread",
                    "Mixed Vegetables",
                    "Black Beans",
                    "Bread Slice",
                    "Broccoli",
                    "Buffalo Chicken Dipper with Bread",
                    "Buffalo Chicken Grilled Cheese",
                    "Cheeseburger",
                    "Chicken and Cheese Quesadilla with Salsa",
                    "Chicken Chips",
                    "Chicken Egg Roll",
                    "Chili Cheese Bowl with Rice",
                    "Applesauce",
                    "Cinnamon Apple Slices",
                    "Oranges",
                    "Corn Dog Nuggets",
                    "Scalloped Potatoes",
                    "Mashed Potatoes",
                    "Crisp Baby Carrots",
                    "Crisp Tater Tots",
                    "Chicken Tenders",
                    "Diced Pears",
                    "Dinner Roll",
                    "Early Dismissal",
                    "Egg Noodles",
                    "Beans",
                    "Food Fusion:",
                    "French Toast Sticks and Sausage",
                    "Bread",
                    "Italian Dunkers",
                    "Salad",
                    "Garlic Breadstick",
                    "Garlic Knots",
                    "Corn",
                    "Diced Carrots",
                    "Grilled Cheese",
                    "Ham and Cheese on a Pretzel Bun",
                    "No School: Holiday Break",
                    "No School: Holiday Break",
                    "Holiday Dinner",
                    "Lasagna",
                    "Refried Beans",
                    "Apple Slices",
                    "Cheeseburger",
                    "Peaches",
                    "Macaroni and Cheese with Bread",
                    "Meatball and Mozzarella Hoagie",
                    "Meatball Hoagie",
                    "No School: Memorial Day",
                    "Milk Carton",
                    "No School: New Year's Day",
                    "No School: New Year's Eve",
                    "No School",
                    "No School: MS and HS-Parent Teacher Conferences",
                    "No School:Act 80 Day",
                    "No School:Faculty In-service",
                    "No School:Parent Faculty Conferences",
                    "Chicken Bowl",
                    "Pasta and Meat Sauce",
                    "Pepperoni Roll",
                    "Philly Cheesesteak Sub",
                    "Popcorn Chicken in a Waffle Cone",
                    "Popcorn Chicken Bowl with Bread",
                    "Pork BBQ Sandwich",
                    "Pork BBQ",
                    "Pulled Pork BBQ on Bun",
                    "Fruit Cocktail",
                    "Turkey",
                    "Salisbury Steak and Bread",
                    "Brown Rice",
                    "Green Beans",
                    "Ham",
                    "Strawberries",
                    "Beef and Cheese Tacos",
                    "Broccoli",
                    "Carrot Coins",
                    "Carrots",
                    "Stewed Tomatoes",
                    "Stir-Fry Chicken and Vegetables",
                    "Strawberries",
                    "Stuffing",
                    "Meatballs over Noodles",
                    "Sweet Peas",
                    "BBQ Rib Sandwich",
                    "No School: Thanksgiving",
                    "Thanksgiving Meal",
                    "There is currently nothing on the menu today.",
                    "Tomato Soup",
                    "Pineapple Tidbits",
                    "Turkey Pot Roast with Bread",
                    "Walking Taco with Doritos",
                    "Walking Taco with Beef and Cheese",
                    "Walking Taco with Nacho Chips and Bread",
                    "Apple Crisp",
                    "or",]
        TEST_OPAL.is_dry = True
        TEST_OPAL.meal = "\n".join(raw_food)
        TEST_OPAL.clean_meal()
        self.assertEqual(TEST_OPAL.meal, "\n".join(dry_food))
