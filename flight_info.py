"""
Module to scrap flight info from airblue.com
"""

import datetime as dt
import argparse
import re
from itertools import product
import requests
from lxml import html

PRICE_REG = r"[A-Z]{3}\s\d+,?\d+"
CABIN_REG = r"-[A-Z]{2,}"
TIME_REG = r"\d{1,}:\d{1,}\s[AP]M"


def find_in_text(reg_pattern, text):
    """
    Find specific text via regex

    :param
        str: reg_pattern: regex pattern
    :param
        str: text: text where to find

    :return:
        tuple of str: all found matches
    """

    pattern = re.compile(reg_pattern)
    return tuple(re.findall(pattern, text))


class Flight:
    """Structure to store information about flight"""

    def __init__(self, flight_info):
        """
        The constructor for Flight class.

        :param
            flight_info (dict): contain information about flight
        """

        self.departure_time = flight_info['departure_time']
        self.arrival_time = flight_info['arrival_time']
        self.flight_duration = time_diff(flight_info['departure_time'],
                                         flight_info['arrival_time'])
        self.currency, self.price = \
            flight_info['price'].replace(',', '').split(' ')
        self.price = int(self.price)

        self.cabin = flight_info['cabin']

    def __str__(self):
        return f"{self.departure_time}-{self.arrival_time}\n" \
               f"Flight time: {self.flight_duration} " \
               f"hours, minutes and seconds respectively\n" \
               f"Cabin: {self.cabin}\n" \
               f"Price: {self.currency} {self.price}"

    def add_prices(self, flight_instance):
        """
        Sum up the cost of two flights

        :param
            flight_instance: class Flight instance

        :return:
            int: Summary price for two flights
        """

        return self.price + flight_instance.price


def create_parser():
    """
    Create argument parser

    :return:
        argparse.ArgumentParser: parser
    """

    parser = argparse.ArgumentParser(
        description='Flight information tool'
    )

    parser.add_argument('departure_city', help='Departure city IATA-code')
    parser.add_argument('arrival_city', help='Arrival city IATA-code')
    parser.add_argument('departure_date',
                        help='Departure date in format YYYY-MM-DD')
    parser.add_argument('return_date', nargs='?', default=None,
                        help='Return date in format YYYY-MM-DD')

    return parser


def parse_args():
    """
    Parse arguments from command line

    :return:
        argparse.Namespace: parsed arguments
    """

    parser = create_parser()
    try:
        args = parser.parse_args()

        return args_validation_handler(args)

    except SystemExit:
        return wrong_args_num_handler(parser)


def wrong_args_num_handler(parser):
    """
    Сalled when there are too few arguments to parse in command line

    :param parser:
        parse arguments from new user input string

    :return:
        argparse.Namespace: parsed arguments
    """

    new_args = input("Enter parameters one more time"
                     "(with date in YYYY-MM-DD format):\n").split()
    while len(new_args) < 3 or len(new_args) > 4:
        new_args = input("Wrong number of arguments, "
                         "enter parameters one more time:\n").split()

    return args_validation_handler(parser.parse_args(new_args))


def args_validation_handler(args):
    """
    Check the validity of the arguments
    and otherwise ask to re-enter them

    :param
        argparce.Namespace args: arguments to check

    :return:
        argparce.Namespace: parsed valid arguments
    """

    while True:
        if not check_date(args.departure_date):
            args.departure_date = input("Incorrect departure date, "
                                        "enter date(format: YYYY-MM-DD) "
                                        "one more time:\n")
        elif not check_date(args.return_date):
            args.return_date = input("Incorrect return date, "
                                     "enter date(format: YYYY-MM-DD) "
                                     "one more time:\n")
        elif not check_iata(args.departure_city):
            args.departure_city = input("Incorrect departure city IATA-code, "
                                        "enter date(format: YYYY-MM-DD) "
                                        "one more time:\n")
        elif not check_iata(args.arrival_city):
            args.arrival_city = input("Incorrect arrival city IATA-code, "
                                      "enter it one more time:\n")
        elif not right_dates_order(args.departure_date, args.return_date):
            print("Incorrect dates order")
            args.departure_date = \
                input("Enter departure date(format: YYYY-MM-DD) "
                      "one more time:\n")
            args.return_date = input("Enter return date(format: YYYY-MM-DD) "
                                     "one more time:\n")
        else:
            break

    return args


def str_time_to_time(time):
    """
    Convert string with time into
    datetime.datetime instance

    :param
        str: time: string in format HH:MM AM/PM

    :return:
        datetime.datetime instance
    """

    return dt.datetime.strptime(time, '%I:%M %p')


def time_diff(time_1, time_2):
    """
    Calculate time difference

    :param
       datetime.datetime: time_1: first time obj
    :param
        datetime.datetime: time_2: second time obj

    :return:
        datetime.timedelta: difference iin time
    """

    return str_time_to_time(time_2) - str_time_to_time(time_1)


def str_date_to_date(date):
    """
       Convert string with date into
       datetime.datetime instance

       :param
           str: time: string in format YYYY-MM-DD

       :return:
           datetime.datetime instance
    """

    return dt.datetime.strptime(
        date.replace('-', ''), '%Y%m%d').date()


def right_dates_order(dep, ret):
    """
    Check the right order of
    return and departure dates

    :param dep: departure date
    :param ret: return date

    :return:
        bool: order is right
    """

    if ret is None:   # checking for none to prevent
        return True   # the user from entering an empty string

    dep = str_date_to_date(dep)
    ret = str_date_to_date(ret)

    return dep <= ret


def check_iata(iata_code):
    """
    Validate IATA code
    :param
        str: iata_code: IATA code
    :return:
        bool: code is correct
    """

    return iata_code.isalpha() and len(iata_code) == 3


def check_date(date):
    """
    Validate date
    :param
        str: date:
    :return:
        bool: date is correct
    """

    if date is None:  # checking for none to prevent
        return True   # the user from entering an empty string

    try:
        date = str_date_to_date(date)
        curr_date = dt.datetime.now().date()

        return curr_date <= date

    except ValueError:
        return False


def make_request(args):
    """
    Send GET request with params from args
    :param
        argparse.Namespace: args: parameters
    :return:
         response
    """

    url = 'https://www.airblue.com/bookings/flight_selection.aspx'

    departure_date = args.departure_date.split('-')

    data_dict = {'PA': 1,
                 'DC': args.departure_city,
                 'AC': args.arrival_city,
                 'TT': 'OW',
                 'AM': departure_date[0] + '-' + departure_date[1],
                 'AD': departure_date[2]
                 }

    if args.return_date:
        return_date = args.return_date.split('-')
        data_dict.update({'TT': 'RT',
                          'RM': return_date[0] + '-' + return_date[1],
                          'RD': return_date[2]
                          })

    return requests.get(url, params=data_dict)


def parse_flights(trip):
    """
    Find needed information in trip and
    transfer it to Flight constructor

    :param
        html: trip: target html obj

    :return:
        list of Flights: initialized Flights
            parsed from html
    """

    flights = []

    for node in filter(lambda x: x.tag == 'tbody', list(trip)):

        for flight in node:
            cabins = []

            for cabin in flight.find_class('family'):
                if 'SOLD OUT' in cabin.text_content():
                    continue
                cabins.append(cabin.attrib['class'])

            cabins = tuple(cabins)
            time = tuple(find_in_text(TIME_REG, flight.text_content()))
            prices = tuple(find_in_text(PRICE_REG, flight.text_content()))
            flights_info = {'departure_time': None,
                            'arrival_time': None,
                            'price': None,
                            'cabin': None}

            for num, val in enumerate(prices):
                flights_info['departure_time'] = time[0]
                flights_info['arrival_time'] = time[1]
                flights_info['price'] = val

                cls = find_in_text(CABIN_REG,
                                   cabins[num])[0].replace('-', '')

                if cls == 'ES':
                    flights_info['cabin'] = 'Economy Standard'
                elif cls == 'ED':
                    flights_info['cabin'] = 'Economy Discount'

                flights.append(Flight(flights_info))

    return flights


def all_sorted_combinations(*args):
    """
    Creates list of all possible combinations
    for given two lists and sort it by summary flight price
    or sort one list by price if given one list

    :param
        args: contains some lists

    :return:
        list: sorted list of tuples or list
    """

    if len(args) == 1:
        args[0].sort(key=lambda x: x.price)

        return args[0]

    if len(args) == 2:
        res = list(product(*args))
        res.sort(key=lambda x: x[0].add_prices(x[1]))

        return res

    raise Exception('Too many arguments')


def pretty_print(obj):
    """
    For list or iter in list print its content
    :param
        list: obj: obj to print
    """

    if isinstance(obj[0], (list, tuple)):
        for flight_to, flight_from in obj:

            if flight_to.currency == flight_from.currency:
                print(f'{flight_to.currency} '
                      f'{flight_to.add_prices(flight_from)}')
            else:
                print(flight_to.add_prices(flight_from))

            print(f'\n\nTo:\n{flight_to}\n\nBack:\n{flight_from}\n{"-" * 100}')

    elif isinstance(obj[0], Flight):
        for flight in obj:
            print(f'{flight.currency} {flight.price}\n'
                  f'\nTo:\n{flight}\n'
                  f'\n{"-" * 100}')
    else:
        raise Exception("Wrong nesting depth")


def main():
    """
    Finds and print all available
    flights for given user input
    """

    args = parse_args()
    page = make_request(args)
    tree = html.fromstring(page.content)
    flights_not_available = \
        tree.xpath('//*[@id="content"]/div/table/tbody/tr/td/text()')
    res = None

    if flights_not_available:
        print("There are no flights available")

        return

    trip_1 = tree.get_element_by_id('trip_1_date_' +
                                    args.departure_date.replace('-', '_'))
    flights_to = parse_flights(trip_1)

    if args.return_date:
        trip_2 = tree.get_element_by_id('trip_2_date_' +
                                        args.return_date.replace('-', '_'))
        flights_from = parse_flights(trip_2)

        if flights_from and flights_to:
            res = all_sorted_combinations(flights_to, flights_from)
        elif flights_to:
            res = all_sorted_combinations(flights_to)

    else:
        res = all_sorted_combinations(flights_to)

    if res:
        pretty_print(res)
    else:
        print("There are no flights available")


if __name__ == '__main__':
    main()
