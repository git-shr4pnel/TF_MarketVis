import requests
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup as bs
import js2py as js


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
    pass


def plot(data):
    return data


def main():
    market_data = get_market_data()
    interpreted_data = interpret_data(market_data)
    plot(interpreted_data)


if __name__ == "__main__":
    main()
