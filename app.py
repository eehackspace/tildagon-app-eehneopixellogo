import time

import app
from app_components import Menu, Notification, clear_background
from typing import Literal
from app_components.tokens import clear_background, set_color
import settings


from .effects import Effects
from .palettes import Palettes

main_menu_items = [
    "Power",
    "Speed",
    "Brightness",
    "Effects",
    "Palette",
    "Slot",
    "Slot 2",
    "About",
]
power_menu_items = ["On", "Off"]

from events.input import Buttons, BUTTON_TYPES

from tildagonos import tildagonos


class EEHNeoPixelLogo(app.App):
    def __init__(self):
        # Menu setup
        self.menu = None
        self.current_menu = None

        self.set_menu("main")
        self.show_palette = False

        # Notification setup
        self.notification = None

        # Button setup
        self.button_states = Buttons(self)

        # Main app setup
        self.power = True
        self.effects = Effects()
        self.palettes = Palettes()

    def set_slot(self, slot):
        slot = int(slot)
        settings.set("eeh.slot", slot)
        settings.save()
        self.effects.clear_leds()
        self.effects.init_chain()

    def set_slot2(self, slot):
        if slot != "None":
            slot = int(slot)
        settings.set("eeh.slot2", slot)
        settings.save()
        self.effects.clear_leds()
        self.effects.init_chain()

    def back_handler(self):
        # If in the topmost menu, minimize, otherwise move one menu up.
        if self.current_menu == "main":
            self.minimise()
        else:
            if self.current_menu == "Palette":
                self.show_palette = True
            else:
                self.show_palette = False
            self.set_menu("main")
            self.effects.set_speed(None, 1)
            self.effects.set_effect(None, 1)
            self.effects.set_palette(None, 1)

    def select_handler(self, item, idx):
        # If Power or Preset item selected enter that menu
        if item in main_menu_items:
            self.set_menu(item)
        else:
            if self.current_menu == "Power":
                if item == "On":
                    self.notification = Notification("Power On")
                    self.power = True
                    self.set_menu("main")
                elif item == "Off":
                    self.notification = Notification("Power Off")
                    self.power = False
                    self.effects.set_led_all((0, 0, 0))
                    self.set_menu("main")
            elif self.current_menu == "Speed":
                if item in self.effects.get_speeds():
                    self.notification = Notification("Speed=" + item)
                    self.effects.set_speed(item)
                    self.set_menu("main")
            elif self.current_menu == "Brightness":
                if item in self.effects.get_brightnesses():
                    self.notification = Notification("Brightness=" + item)
                    self.effects.set_brightness(item)
                    self.set_menu("main")
            elif self.current_menu == "Effects":
                if item in self.effects.get_effect_list():
                    self.notification = Notification(item)
                    self.effects.set_effect(item)
                    self.set_menu("main")
            elif self.current_menu == "Palette":
                if item in self.palettes.get_palette_list():
                    self.notification = Notification(item)
                    self.effects.set_palette(item)
                    self.set_menu("main")
            elif self.current_menu == "Slot":
                if item in ["1", "2", "3", "4", "5", "6"]:
                    self.notification = Notification("Slot=" + item)
                    self.set_slot(item)
                    self.set_menu("main")
            elif self.current_menu == "Slot 2":
                if item in ["None", "1", "2", "3", "4", "5", "6"]:
                    self.notification = Notification("Slot=" + item)
                    self.set_slot2(item)
                    self.set_menu("main")

            else:
                self.notification = Notification(self.current_menu + "." + item + '"!')

    def change_handler(self, item):
        if self.current_menu == "main":
            if item == "Palette":
                self.show_palette = True
            else:
                self.show_palette = False
        elif self.current_menu == "Speed":
            if item in self.effects.get_speeds():
                self.effects.set_speed(item, 1)
        elif self.current_menu == "Brightness":
            if item in self.effects.get_brightnesses():
                self.effects.set_brightness(item, 1)
        elif self.current_menu == "Effects":
            if item in self.effects.get_effect_list():
                self.effects.set_effect(item, 1)
        elif self.current_menu == "Palette":
            self.show_palette = True
            if item in self.palettes.get_palette_list():
                self.effects.set_palette(item, 1)

    def set_menu(
        self,
        menu_name: Literal[
            "main",
            "Power",
            "Speed",
            "Brightness",
            "Effects",
            "Palette",
            "Slot",
            "About",
        ],
    ):
        if self.menu:
            self.menu._cleanup()
        if self.current_menu:
            previous_menu = self.current_menu
        else:
            previous_menu = "Power"
        self.current_menu = menu_name
        if menu_name == "main":
            self.menu = Menu(
                self,
                main_menu_items,
                select_handler=self.select_handler,
                change_handler=self.change_handler,
                back_handler=self.back_handler,
                position=(
                    [
                        "Power",
                        "Speed",
                        "Brightness",
                        "Effects",
                        "Palette",
                        "Slot",
                        "Slot 2",
                        "About",
                    ]
                ).index(previous_menu),
            )
        elif menu_name == "Power":
            self.menu = Menu(
                self,
                power_menu_items,
                select_handler=self.select_handler,
                back_handler=self.back_handler,
                position=0 if self.power else 1,
            )
        elif menu_name == "Speed":
            self.menu = Menu(
                self,
                self.effects.get_speeds(),
                select_handler=self.select_handler,
                change_handler=self.change_handler,
                back_handler=self.back_handler,
                position=self.effects.get_speeds().index(str(self.effects.get_speed())),
            )
        elif menu_name == "Brightness":
            self.menu = Menu(
                self,
                self.effects.get_brightnesses(),
                select_handler=self.select_handler,
                change_handler=self.change_handler,
                back_handler=self.back_handler,
                position=self.effects.get_brightnesses().index(
                    str(self.effects.get_brightness())
                ),
            )
        elif menu_name == "Effects":
            self.menu = Menu(
                self,
                self.effects.get_effect_list(),
                select_handler=self.select_handler,
                change_handler=self.change_handler,
                back_handler=self.back_handler,
                position=self.effects.get_effect_list().index(
                    self.effects.get_effect()
                ),
            )
        elif menu_name == "Palette":
            self.show_palette = True
            self.menu = Menu(
                self,
                self.palettes.get_palette_list(),
                select_handler=self.select_handler,
                change_handler=self.change_handler,
                back_handler=self.back_handler,
                position=self.palettes.get_palette_list().index(
                    self.effects.get_palette()
                ),
            )
        elif menu_name == "Slot":
            self.menu = Menu(
                self,
                ["1", "2", "3", "4", "5", "6"],
                select_handler=self.select_handler,
                back_handler=self.back_handler,
                position=settings.get("eeh.slot", 1) - 1,
            )

        elif menu_name == "Slot 2":
            pos = settings.get("eeh.slot2", "None")
            if pos == "None":
                pos = 0
            else:
                pos = pos + 1
            self.menu = Menu(
                self,
                ["None", "1", "2", "3", "4", "5", "6"],
                select_handler=self.select_handler,
                back_handler=self.back_handler,
                position=pos,
            )

        elif menu_name == "About":
            self.menu = Menu(
                self,
                [
                    "Buy an East",
                    "Essex Hackspace",
                    "NeoPixel Hexpansion",
                    "from the",
                    "EEH Village",
                    "in Camping C",
                    "OR",
                    "Night Market",
                ],
                back_handler=self.back_handler,
            )

    def draw(self, ctx):
        clear_background(ctx)
        if self.show_palette:
            shape_colour = self.palettes.get_palette(self.effects.get_palette())

            ctx.linear_gradient(-100, -35, 100, -35)
            for key, value in shape_colour.items():
                ctx.add_stop(key / 256, value, 1)
            ctx.rectangle(-100, -35, 200, 10).fill()

        self.menu.draw(ctx)

        if self.notification:
            self.notification.draw(ctx)

    def update(self, delta):
        self.menu.update(delta)
        if self.notification:
            self.notification.update(delta)

    #        print(self.power)

    def background_update(self, delta):
        #        print("background_update")
        #        print(time.time())
        #        print(self.power)
        if self.power == True:
            self.effects.cycle()
        print(settings.get("eeh.slot"))
        print(settings.get("eeh.slot2"))
        # if self.button_states.get(BUTTON_TYPES["RIGHT"]):
        #     tildagonos.leds[2] = (255, 0, 0)
        #     tildagonos.leds[3] = (255, 0, 0)
        # elif self.button_states.get(BUTTON_TYPES["LEFT"]):
        #     tildagonos.leds[8] = (0, 255, 0)
        #     tildagonos.leds[9] = (0, 255, 0)
        # elif self.button_states.get(BUTTON_TYPES["UP"]):
        #     tildagonos.leds[12] = (0, 0, 255)
        #     tildagonos.leds[1] = (0, 0, 255)
        # elif self.button_states.get(BUTTON_TYPES["DOWN"]):
        #     tildagonos.leds[6] = (255, 255, 0)
        #     tildagonos.leds[7] = (255, 255, 0)
        # elif self.button_states.get(BUTTON_TYPES["CANCEL"]):
        #     tildagonos.leds[10] = (0, 255, 255)
        #     tildagonos.leds[11] = (0, 255, 255)
        # elif self.button_states.get(BUTTON_TYPES["CONFIRM"]):
        #     tildagonos.leds[4] = (255, 0, 255)
        #     tildagonos.leds[5] = (255, 0, 255)
        # else:
        #     for i in range(0,12):
        #         tildagonos.leds[i+1] = (255, 255, 255)


__app_export__ = EEHNeoPixelLogo
