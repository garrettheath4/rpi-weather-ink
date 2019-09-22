#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ConfigParser
import json

try:
    import requests
except ImportError:
    requests = None
    exit("This package requires the requests module\nInstall it with pipenv install --system")

try:
    from bs4 import BeautifulSoup
except ImportError:
    from weatherink.tests.mock import BeautifulSoup
    exit("This package requires the BeautifulSoup module\nInstall it with pipenv install --system")

try:
    import lxml
except ImportError:
    print("The BeautifulSoup library probably requires the lxml module\n"
          + "If this script fails, install lxml with sudo apt install python-lxml")


class Weather:
    def __init__(self, coords, query_api=True):
        self.coords = coords
        self._coords_str = ",".join([str(c) for c in coords])
        self.query_api = query_api

        # Create fields for weather data
        self.summary_key = None
        self.current_temp = None
        self.feels_like = None
        self.low_temp = None
        self.high_temp = None
        self.uv_index = None

        # Fetch weather data
        self._api_key = None
        if query_api:
            self._api_key = self.get_api_key_from_config()
        self.request()

    @staticmethod
    def get_api_key_from_config():
        config = ConfigParser.RawConfigParser()
        config.read("secrets.ini")
        try:
            return config.get("DarkSky", "api-key")
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            return None

    def request(self):
        if self.query_api and self._api_key:
            # exclude=currently,minutely,hourly,daily,alerts,flags
            res = requests.get("https://api.darksky.net/forecast/{}/{}?exclude=minutely,hourly,alerts,flags"
                               .format(self._api_key, self._coords_str))
            if res.status_code == 200:
                res_json = json.loads(res.content)
                self.summary_key = res_json["daily"]["icon"]
                self.current_temp = int(round(res_json["currently"]["temperature"]))
                self.feels_like = int(round(res_json["currently"]["apparentTemperature"]))
                self.low_temp = int(round(res_json["daily"]["data"][0]["temperatureLow"]))
                self.high_temp = int(round(res_json["daily"]["data"][0]["temperatureHigh"]))
                self.uv_index = int(res_json["daily"]["data"][0]["uvIndex"])
            else:
                raise Exception("API request returned a not-OK status code", res.status_code, res.url)
        else:
            if self.query_api and not self._api_key:
                print("Warning: Fetching data from current forecast page instead of API since no API key was given")
            res = requests.get("https://darksky.net/forecast/{}/us12/en".format(self._coords_str))
            if res.status_code == 200:
                soup = BeautifulSoup(res.content, "lxml")
                curr = soup.find("span", "currently")
                self.summary_key = curr.img["alt"].split()[0]
                self.current_temp = int(curr.find("span", "summary").text.split()[0][:-1])
                high_low = curr.find("span", {"class": "summary-high-low"})
                self.feels_like = int(high_low.find("span", {"class": "feels-like-text"}).text[:-1])
                self.low_temp = int(high_low.find("span", {"class": "low-temp-text"}).text[:-1])
                self.high_temp = int(high_low.find("span", {"class": "high-temp-text"}).text[:-1])
                self.uv_index = int(soup.find(id="currentDetails")
                                    .find("div", {"class": "uv_index"})
                                    .find("span", {"class": "uv__index__value"})
                                    .text)
            else:
                raise Exception("UI request returned a not-OK status code", res.status_code, res.url)