# opal
Opal is a bot that scrapes the school's website for the current day's lunch. She emails it out at the specified time each day. A real lovely lady!

The idea behind her is to have the lunch menu for the day on your iPad or phone at all times during the day :)

## Requirements
Python 3.6+ (this project makes heavy use of [f-strings](https://realpython.com/python-f-strings/#f-strings-a-new-and-improved-way-to-format-strings-in-python) and [optional static typing](https://realpython.com/python-type-checking/#static-type-checking))

[Selenium](https://www.seleniumhq.org/)


## TODO:
* The HTML email she sends out could be improved to work more consistently
* More adjectives
* Hosting
* Look into using gmail API instead of smptlib to send emails

## Usage
#### Basic
##### Optional Arguments:
* `-d, --driver DRIVER` The path to your chrome web driver
* `--time TIME` Time for email to be sent. Works on military time (23 is 11pm). Default is 7
* `--dry` The meal will be sent in minimalist form; only the words necessary to understanding the food are kept. For example, Pasta & Meat Sauce | Meatball & Mozzarella Hoagie | Green Beans | Salad | Peaches | Milk
##### Debug Arguments
* `-e, --test, --today` Print today's meal to console instead of sending an email
* `-t, --tomorrow` Print tomorrow's meal to console instead of sending an email
* `-y, --yesterday` Print yesterday's meal to console instead of sending an email
* `-a, --add ADD` Go `n` number of days into the future. Can also be negative to go into the past
* `--custom-date [CUSTOM_DATE ...]` Print a custom date's meal to console instead of sending an email. Format: YYYY MM DD Example: --custom-date 2019 01 17
* `--send` Send meal as email
* `--force [FORCE ...]` Force adjectives passed to show up in meal
* `--used` Show the adjectives used yesterday
* `--raw` Show meal as it appears on website without any cleaning
* `--emails, --show-emails` Print email dict to console
* `--gui` Show chrome gui when running
