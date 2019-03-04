"""
Unit test scraping of https://udas.nutrislice.com/menu/upper-dauphin-high/lunch
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

TEST_OPAL = opal.Opal(
    driver_path="chromedriver.exe",
    start_time=0,
    is_dry=False,
    is_test=True,
    is_tomorrow=False,
    is_yesterday=False,
    add_days=None,
    custom_date=[2018, 12, 17],
    forced_adjectives=None,
    is_test_email=False,
    gui=False,
    is_two_hour_delay=False
)


class TestOpalScraping(unittest.TestCase):
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
        TEST_OPAL.meal = ""
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
