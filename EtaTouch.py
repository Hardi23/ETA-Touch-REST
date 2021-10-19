import re

import requests
import xmltodict

import MenuModel
import constants


class EtaTouch:
    API_URI = "/user/api"

    def __init__(self, ip, port="8080"):
        if not re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", ip):
            raise RuntimeError("Specified ip does not match pattern")
        self.host = "http://" + ip + ":" + port
        self.modules_loaded = False
        self.menu = None

    def load_modules(self):
        if not self.check_version():
            return False

        self.menu = MenuModel.MenuParser.parse_menu(self.host)
        if self.menu is None:
            print("Could not parse menu!")
            return False
        else:
            self.modules_loaded = True

    def load_values(self):
        self.menu.collect_info()

    def get_sensor(self, endpoint):
        return self.menu.sensor_addresses.get(endpoint)

    def check_version(self):
        r = requests.get(url=self.host + self.API_URI, headers=constants.DEFAULT_REQUEST_HEADERS)
        if r.status_code != 200:
            print("Version check, no connection to: " + self.host)
            return False
        parsed = xmltodict.parse(r.text)
        api_version = parsed[constants.MENU_ETA][constants.MENU_API][constants.VALUE_VERSION]
        if float(api_version) < 1.1:
            print("Version not supported, only 1.1 and up!")
            return False
        return True

    def list_endpoints(self):
        for ep in self.menu.sensor_addresses:
            print(ep)
