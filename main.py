import requests
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from bs4 import BeautifulSoup as bs
import js2py as js
import datetime as dt
import os
import json
import time
import datetime


class Date:
    def __init__(self, day, month, year):
        self.day = day
        self.month = month
        self.year = year

    def __str__(self):
        return f"{self.day} {self.month} {self.year}"


class Key:
    def __init__(self, price, time_is):
        self.price = price
        self.time_is = time_is

    def __repr__(self):
        return f"{self.time_is} £{self.price}"


def get_market_data():
    r = requests.get("https://steamcommunity.com/market/listings/440/Mann%20Co.%20Supply%20Crate%20Key")
    soup = bs(r.content, "html.parser")
    tags, tag = soup.find_all("script", {"type": "text/javascript"}), None
    for tag in tags:
        if "Dec 12 2012" in tag:
            break
    try:
        tag = tag.prettify()
    except AttributeError:
        raise RuntimeError("The request to the steam servers has failed. Are they up?")
    isolated_js = str(tag.splitlines()[25:-26])  # isolates single line with the javascript we want
    isolated_list = isolated_js[18:-3]  # yanks out the data that can't be compiled (?) by js2py
    converted_list = js.eval_js(isolated_list)
    return converted_list


def interpret_data(data):
    latest = len(data)-1
    formatted_list = []
    for n, item in enumerate(data):
        if n > latest - 719:  # there are 719 entries at the end of the list with time specific data.
            break             # we don't want or need that data. this simplifies working with it
        formatted_list.append(item)
    latest, monthly_list = len(formatted_list), []
    for i in range(0, latest, 31):
        monthly_list.append(data[i])
    return monthly_list


def get_exchange_rate():
    if not os.path.exists("resources"):
        os.mkdir("resources")
    if os.path.exists("resources/cache.json"):
        with open("resources/cache.json", "r") as f:
            price_data = json.load(f)
        if price_data["last_modified"] >= time.time() - 86400:
            return price_data["GBP"]
    with open("resources/cache.json", "w") as f:
        r = requests.get("https://open.er-api.com/v6/latest/USD")
        response = r.json()
        if response["result"] != "success":
            raise requests.exceptions.ConnectionError("The exchange rate API is down!")
        response = {"GBP": response["rates"]["GBP"], "last_modified": time.time()}
        json.dump(response, f)
        return response["GBP"]


def sort_monthly(data):
    forex = get_exchange_rate()
    sorted_data = []
    for element in data:
        date = Date(element[0][4:6], element[0][:3], element[0][7:11])
        price = round(element[1] * forex, 2)
        sorted_data.append(Key(price, date))
    return sorted_data


def plot(data):
    y_points, dates, values = [], [], [x for x in range(0, 10)]
    for item in data:
        y_points.append(item.price)
        dates.append(item.time_is)
    plt.ylabel("Price (£)")
    plt.xlabel("Date")
    datetime_dates = [dt.datetime.strptime(str(d), "%d %b %Y").date() for d in dates]
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%d %b %Y"))
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=8))
    plt.title("Key Value")
    plt.plot(datetime_dates, y_points, color="red")
    plt.gcf().autofmt_xdate()
    plt.show()
    return data


def main():
    market_data = get_market_data()
    interpreted_data = interpret_data(market_data)
    organised_data = sort_monthly(interpreted_data)
    plot(organised_data)


if __name__ == "__main__":
    main()
