# Fresh Slot Finder

The idea behind this application is that it will try to find any days that have open slots for Amazon Fresh delivery. Hopefully, in the near future, I will add support for other grocery delivery services

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

What things you need to install the software and how to install them

```
Python 3.7
```

### Installing

A step by step series of examples that tell you how to get a development env running

1. Install a virtual environment inside of the project

```
MacOS and Linux: python3 -m venv env
Windows: py -m venc env
```

2. Activate the virtual environment

```
MacOS and Linux: source env/bin/activate
Windows: .\env\Scripts\activate
```

3. Install project dependencies

```
pip install -r requirements.txt
```

4. Run the application

```
python main.py
```

## Running

To get command information, run `python main.py -h`

```
usage: main.py [-h] [-l LOG_LEVEL] [-n] [-tn] [-dn DUMP_NOTIFICATIONS] [-cn]

Find open delivery slots

optional arguments:
  -h, --help            show this help message and exit
  -l LOG_LEVEL, --log-level LOG_LEVEL
                        Set the log level to TRACE, DEBUG, INFO, WARN, ERROR
  -n, --notifications   Setup Nofications
  -tn, --test-notification
                        Send a test notification
  -dn DUMP_NOTIFICATIONS, --dump-notifications DUMP_NOTIFICATIONS
                        Dumps the previous N notifications
  -cn, --clear-notifications
                        Clears all notifications from the local history
```
### Running Slot Finder

1. Start program with `python main.py` with no parameters
2. Will generate a url you can use to subscribe to notifications (Android and Desktop only)
3. Will open a browser window for you to login to Amazon
    - Make sure to select the 'Remember Me' option when logging in or else the application will time out in about 2 hours
4. Navigate to the slot selection page and hit enter on the console
5. Program will run and monitor the page for any slots that open up
    - When a slot if found, information is printed to the console
    - A notification is sent to the previous URL


## Running the tests

No tests yet

### Coding style

We are using the pep8 standards

## Deployment

Ran into permissions issues on Linux/Mac for the drivers. Please make sure that the permissions
are correct on your system.

## Built With

* [beautifulsoup4](https://pypi.org/project/beautifulsoup4/) - Used to scrape content from the web pages
* [PyYAML](https://pypi.org/project/PyYAML/) - Used for configuration management
* [selenium](https://pypi.org/project/selenium/) - Interacts with the browser and webpage
* [notify-run](https://pypi.org/project/notify-run/) - Free notification service used to alert users

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [versions on this repository](https://github.com/bryantp/fresh-slot-finder/releases). 

## Authors

* **Bryan Perino** - *Initial work*

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details