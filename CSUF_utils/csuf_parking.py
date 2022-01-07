#!/usr/bin/env python3.5

# sorts by which parking structure is most available

import itertools
import operator
import os
import typing
import dataclasses
import re

from selenium import webdriver


from selenium.webdriver.firefox.options import Options

@dataclasses.dataclass
class Structure:
    name: str
    spaces_open: int
    total_capacity: int

    @property
    def percent(self) -> float:
        return self.spaces_open / self.total_capacity

class Driver:
    def __init__(self, url: str):
        self.url = url

        option = Options()
        option.headless = True
        self._driver = webdriver.Firefox(options=option)
    def __del__(self):
        self._driver.quit()
        os.remove("geckodriver.log")


    def _run(self):
        self._driver.get(self.url)

    def parse_results(self) -> typing.List[Structure]:
        self._run()
        parse_capacity = re.compile(r"([\d]+)")

        structures = self._driver.find_elements_by_class_name('LocationName')
        total_avail = self._driver.find_elements_by_class_name('TotalSpaces')
        yellow_avail = self._driver.find_elements_by_css_selector("p[class='AvailableCountYellow ZeroTopBottom']")

        container: typing.List[Structure] = []

        for (name, availability, current_capacity) in itertools.zip_longest(structures, total_avail, yellow_avail):
            print(f'[INFO] Structure: {name.text}')
            current_available = 0
            match current_capacity.text:
                case "Closed":
                    current_capacity.text = 0
                case _:
                    match availability.text:
                        case "Open":
                            current_available = 100
                            current_capacity.text = availability.text

            current_capacity = int(current_capacity.text)
            total = parse_capacity.search(availability.text).group(0)
            print(name.text, total, current_available)
        container.sort(key=operator.attrgetter('percentage'), reverse=True)
        return container

url = "https://parking.fullerton.edu/ParkingLotCounts/mobile.aspx"

DRIVER = Driver(url)

results = DRIVER.parse_results()


# if(current_capacity.text == "Closed"):
# current_available = 0
# else:
# if at.text == "Open":
# print("100% avaiable")
# else:
# current_available = int(at.text)
# name = n.text
# avail = int(a.text.split()[2])
# i.append(Structure(name, avail, current_available))

# i.sort(key=operator.attrgetter('percentage'), reverse=True)
# for element in i:
# print("-"*50)
# print("Name: {}\nPercent: {}".format(element.name, element.percentage))
# print("-"*50)
