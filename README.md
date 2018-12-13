# opal
Opal is a bot that scrapes the school's website for the current day's lunch. She emails it out at the specified time each day. A real lovely lady!

## Requirements
Python 3.x
### Modules:
* selenium

## Usage
#### Basic
##### Positional Arguments:
* None right now :)

##### Optional Arguments:
* `-d, --driver DRIVER` The path to your chrome web driver.
* `--time TIME` Time for email to be sent. Works on military time (23 is 11pm). Default is 7.
* `--dry` The meal will be sent in minimalist form; only the words necessary to understanding the food are kept. For example, Pasta & Meat Sauce | Meatball & Mozzarella Hoagie | Green Beans | Salad | Peaches | Milk
##### Debug Arguments
* `-e, --test, --today` Print today's meal to console instead of sending an email.
* `-t, --tomorrow` Print tomorrow's meal to console instead of sending an email.
* `-y, --yesterday` Print yesterday's meal to console instead of sending an email.
* `-a, --add ADD` Go n number of days into the future. Can also be negative to go into the past.
* `--custom-date [CUSTOM_DATE ...]` Print a custom date's meal to console instead of sending an email. Format: YYYY MM DD Example: --custom-date 2019 01 17
* `--date-range [DATE_RANGE ...]` Print the meal for all dates within the range to console instead of sending an email. Format: YYYY MM DD YYYY MM DD Example: --date-range 2019 01 17 2019 01 20
* `--send` Send a debug email.
* `--used` Show the adjectives used yesterday.
* `--gui` Show gui when running.
