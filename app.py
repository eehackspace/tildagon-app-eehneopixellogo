import time

from app import App
from app_components import Menu, Notification, clear_background
from typing import Literal
from app_components.tokens import clear_background, set_color


from .effects import Effects
from .palettes import Palettes

main_menu_items = ["Power", "Speed", "Effects", "Palette"]
power_menu_items = ["On", "Off"]

from events.input import Buttons, BUTTON_TYPES

from tildagonos import tildagonos


class EEHNeoPixelLogo(App):
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

    def select_handler(self, item):
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
                    self.set_menu("main")
            elif self.current_menu == "Speed":
                if item in self.effects.get_speeds():
                    self.notification = Notification("Speed = " + item)
                    self.effects.set_speed(item)
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
        elif self.current_menu == "Effects":
            if item in self.effects.get_effect_list():
                self.effects.set_effect(item, 1)
        elif self.current_menu == "Palette":
            self.show_palette = True
            if item in self.palettes.get_palette_list():
                self.effects.set_palette(item, 1)

    def set_menu(
        self, menu_name: Literal["main", "Power", "Speed", "Effects", "Palette"]
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
                position=(["Power", "Speed", "Effects", "Palette"]).index(
                    previous_menu
                ),
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
                position=self.effects.get_speeds().index(self.effects.get_speed()),
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