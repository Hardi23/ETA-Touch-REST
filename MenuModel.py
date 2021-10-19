import time
from abc import abstractmethod, ABCMeta

import requests
import xmltodict

import constants


class SubMenuContainer:

    def __init__(self):
        self.sub_menus = {}

    def get_sub_menu(self, name):
        if self.sub_menus.__contains__(name):
            return self.sub_menus[name]
        return None


class MainMenu(SubMenuContainer):
    host = None
    sensor_addresses = {}

    def __init__(self, host_address):
        super().__init__()
        MainMenu.host = host_address + "/user/var"

    def add_sub_menu(self, menu_item):
        menu_item.can_collect_data = False
        menu_item.parent = self
        self.sub_menus[menu_item.name] = menu_item

    def print(self):
        for sub_men in self.sub_menus:
            sub_men.html_print(0)

    def size(self):
        return len(self.sub_menus)

    def collect_info(self):
        for sub_men in self.sub_menus.values():
            sub_men.collect_info()

    def get_print_string(self):
        result_string = "<!doctype html>\n<html lang=\"en\">\n"
        result_string += "<head>\n"
        result_string += " <title>ETA Touch Data</title>\n"
        result_string += "<meta charset=\"utf-8\"/>"
        result_string += "</head>\n<body>\n"
        result_string += " <ul>\n"
        for sub_men in self.sub_menus.values():
            result_string += "  <li>\n"
            result_string += sub_men.get_html_string(3)
            result_string += "  </li>\n"
        result_string += " </ul>\n"
        result_string += "</body>\n</html>"
        return result_string


class MenuItem(SubMenuContainer, metaclass=ABCMeta):

    def __init__(self, name):
        super().__init__()
        self.parent = None
        self.name = name
        self.uri = None
        self.value_collected = False
        self.last_update = 0
        self.str_val = ""
        self.unit = ""
        self.decimal_places = 0
        self.scale_factor = 1
        self.adv_text_offset = ""
        self.xml_val = ""
        self.can_collect_data = True

    def set_parent(self, parent):
        self.parent = parent

    def set_uri(self, param):
        self.uri = param

    def parse_data(self, xml_response):
        data_entry = xml_response[constants.ETA_MEN][constants.VALUE_MEN]
        self.str_val = data_entry[constants.STR_VAL]
        self.unit = data_entry[constants.UNIT]
        self.decimal_places = data_entry[constants.DEC_PLACES]
        self.scale_factor = data_entry[constants.SCALE_FACTOR]
        self.adv_text_offset = data_entry[constants.TEXT_OFFSET]
        self.xml_val = data_entry[constants.XML_TEXT]

        self.last_update = time.time()
        self.value_collected = True

    def exec_collect(self):
        r = requests.get(MainMenu.host + self.uri, headers=constants.DEFAULT_REQUEST_HEADERS)
        if r.status_code != 200:
            print("Error receiving response for: " + self.name + " at URI: " + self.uri)
        from_xml = xmltodict.parse(r.text)
        if not from_xml:
            print("Error parsing response value for: " + self.name + " at URI: " + self.uri)
        else:
            self.parse_data(from_xml)

    def print_values(self):
        print("Name : "+self.name)
        print("String value : " + self.str_val)
        print("Unit : " + self.unit)
        print("Decimal places : " + str(self.decimal_places))
        print("Scale factor : " + str(self.scale_factor))
        print("XML val : " + self.xml_val)
        print("Last update : " + str(self.last_update))

    @abstractmethod
    def get_html_string(self, depth):
        pass

    def html_print(self, depth):
        print(self.get_html_string(depth))

    @abstractmethod
    def collect_info(self):
        pass


class SubMenu(MenuItem):

    def __init__(self, name):
        super().__init__(name)

    def add_sub_menu(self, submenu):
        submenu.parent = self
        self.sub_menus[submenu.name] = submenu

    def set_uri(self, param):
        self.uri = param

    def get_html_string(self, depth):
        printable_string = " " * depth + "<details>\n"
        printable_string += (" " * (depth + 1)) + "<summary>" + self.name + " (" + self.uri + ")" + "</summary>\n"
        printable_string += " " * (depth + 1) + "<ul>\n"

        if self.can_collect_data:
            printable_string += " " * (depth + 2) + "<li>str_val : " + self.str_val + "</li>\n"
            printable_string += " " * (depth + 2) + "<li>unit : " + self.unit + "</li>\n"
            printable_string += " " * (depth + 2) + "<li>decimal_places : " \
                                + self.decimal_places.__str__() + "</li>\n"
            printable_string += " " * (depth + 2) + "<li>scale_factor : " \
                                + self.scale_factor.__str__() + "</li>\n"
            printable_string += " " * (depth + 2) + "<li>text_offset : " \
                                + self.adv_text_offset + "</li>\n"
            printable_string += " " * (depth + 2) + "<li>xml_val : " + self.xml_val + "</li>\n"

        if len(self.sub_menus) > 0:
            for item in self.sub_menus.values():
                printable_string += " " * (depth + 2) + "<li>\n"
                printable_string += item.get_html_string(depth=depth + 3)
                printable_string += " " * (depth + 2) + "</li>\n"
        printable_string += " " * (depth + 1) + "</ul>\n"
        printable_string += " " * depth + "</details>\n"
        return printable_string

    def collect_info(self):
        if self.can_collect_data:
            self.exec_collect()
        for sub_men in self.sub_menus.values():
            sub_men.collect_info()


class Endpoint(MenuItem):

    def __init__(self, name):
        super().__init__(name)

    def update_value(self, value):
        post_val = value * self.scale_factor
        r = requests.post(MainMenu.host + self.uri, f"value={post_val}")
        print(r.status_code)
        return r.status_code == 200

    def get_html_string(self, depth):
        printable_string = " " * depth + "<details>\n"
        printable_string += " " * (depth + 1) + "<summary>" + self.name + " (" + self.uri + ")" \
                            + "</summary>\n"
        printable_string += " " * (depth + 1) + "<ul>\n"

        printable_string += " " * (depth + 2) + "<li>str_val : " + self.str_val + "</li>\n"
        printable_string += " " * (depth + 2) + "<li>unit : " + self.unit + "</li>\n"
        printable_string += " " * (depth + 2) + "<li>decimal_places : " \
                            + self.decimal_places.__str__() + "</li>\n"
        printable_string += " " * (depth + 2) + "<li>scale_factor : " \
                            + self.scale_factor.__str__() + "</li>\n"
        printable_string += " " * (depth + 2) + "<li>text_offset : " \
                            + self.adv_text_offset + "</li>\n"
        printable_string += " " * (depth + 2) + "<li>xml_val : " + self.xml_val + "</li>\n"
        printable_string += " " * (depth + 1) + "</ul>\n"
        printable_string += " " * depth + "</details>\n"
        return printable_string

    def collect_info(self):
        self.exec_collect()


class MenuParser:

    @staticmethod
    def parse_menu(host):
        r = requests.get(host + constants.MENU_EP, headers=constants.DEFAULT_REQUEST_HEADERS)
        if r.status_code != 200:
            raise Exception("No Connection")
        parsed_dict = xmltodict.parse(r.text)
        menu_base = parsed_dict[constants.ETA_MEN][constants.MENU][constants.FUB]
        parsed_menu = MainMenu(host)
        for sub_men in menu_base:
            parsed_menu.add_sub_menu(MenuParser.parse_sub_menu(sub_men, parsed_menu))
        return parsed_menu

    @staticmethod
    def parse_sub_menu(param, main_menu):
        if constants.OBJECT_VAL in param.keys():
            sm = SubMenu(param[constants.NAME])
        else:
            sm = Endpoint(param[constants.NAME])
        sm.set_uri(param[constants.URI])

        if isinstance(sm, SubMenu):
            if isinstance(param[constants.OBJECT_VAL], list):
                for listItem in param[constants.OBJECT_VAL]:
                    sm.add_sub_menu(MenuParser.parse_sub_menu(listItem, main_menu))
            else:
                sm.add_sub_menu(MenuParser.parse_sub_menu(param[constants.OBJECT_VAL], main_menu))

        main_menu.sensor_addresses[sm.uri] = sm
        return sm
