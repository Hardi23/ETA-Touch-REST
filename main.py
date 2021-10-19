import codecs
import sys

from EtaTouch import EtaTouch
from MenuModel import MenuItem


def print_current_menu(menu):
    print("====== Available items ======")
    print("\n".join(menu.sub_menus.keys()))
    print()


def print_html(eta):
    with codecs.open("collected.html", "w", "utf-8") as out:
        out.write(eta.menu.get_print_string())
        out.flush()


if __name__ == '__main__':

    args = sys.argv
    ip = ""
    port = ""
    if len(args) == 1:
        print("No ip passed")
        quit(0)
    if len(args) == 2:
        ip = args[1]
        port = "8080"
    if len(args) == 3:
        ip = args[1]
        port = args[2]
    print(f"Starting with {ip} on port {port}")
    etaTouch = EtaTouch(ip, port)
    etaTouch.load_modules()
    print("Modules loaded.")
    print("Loading current values...")
    etaTouch.load_values()

    val = ""
    cur_menu = etaTouch.menu
    print("Values loaded.\n")
    print_current_menu(cur_menu)
    while True:
        val = input("Enter menu item: ")
        if val == "exit":
            break
        if val == "val":
            cur_menu.print_values()
        elif val == "back":
            if isinstance(cur_menu, MenuItem):
                cur_menu = cur_menu.parent
            print_current_menu(cur_menu)
        elif val == "getEP":
            ep_val = input("Enter Endpoint location")
            ep = etaTouch.menu.sensor_addresses.get(ep_val)
            if ep is None:
                print("Endpoint not found")
            else:
                ep.print_values()
        elif val == "listEP":
            print(etaTouch.list_endpoints())
        elif val == "print":
            print_html(etaTouch)
        else:
            new_men = cur_menu.sub_menus.get(val)
            if new_men is None:
                print("Menu not found reset!")
            else:
                cur_menu = new_men
            print_current_menu(cur_menu)
