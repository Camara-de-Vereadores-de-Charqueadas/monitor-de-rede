from front.menu import MonitorUI
from front.controller import Controller

if __name__ == "__main__":
    controller = Controller()
    menu = MonitorUI("devices.json")
    menu.main_menu(controller)