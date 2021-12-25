import requests
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup as bs
import js2py as js


class TFData:
    def __init__(self, date):
        self.date = date

    def __repr__(self):
        return f"{self.date}"

    def discern_price(self):
        full_date = str(self.date[0][:11])
        price = []
        for character in str(self.date[1]):
            if character == ",":
                break
            price.append(character)
        price = "".join(price)
        print(price)


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
    for i in range(0, latest, 30):
        monthly_list.append(TFData(data[i]))
    return monthly_list


def plot(data):
    return data


def main():
    market_data = get_market_data()
    interpreted_data = interpret_data(market_data)
    plot(interpreted_data)


if __name__ == "__main__":
    main()
