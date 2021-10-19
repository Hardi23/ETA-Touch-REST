import codecs
import sys

from EtaTouch import EtaTouch


def print_current_menu(menu):
    print("\n".join(menu.sub_menus.keys()))


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
    etaTouch = EtaTouch(ip, port)
    etaTouch.load_modules()
    etaTouch.load_values()
    # print_current_menu(main_menu)
    val = ""
    cur_menu = etaTouch.menu
    while val != "exit":
        val = input("Enter menu item: ")
        if val == "val":
            cur_menu.print_values()
        elif val == "back":
            cur_menu = cur_menu.parent
        elif val == "getEP":
            ep_val = input("Enter Endpoint location")
            ep = etaTouch.menu.sensor_addresses.get(ep_val)
            if ep is None:
                print("Enpoint not found")
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
