import time
import neopixel
from machine import Pin
import settings

from .palettes import Palettes

# Constants
LED_COUNT = 14  # Number of NeoPixels
SKIP_LED = (
    0  # How many LEDs at the beginning of the chain to skip, use for for Sim testing
)
FPS_LIMIT = 20  # Limit FPS


class Effects:
    def __init__(self):
        self.speed = settings.get("eeh.speed", 5)
        self.preview_speed = None
        self.brightness = settings.get("eeh.brightness", 50)
        self.preview_brightness = None
        self.effect_list = [
            "Rainbow",
            "Cycle",
            "Cycle with Tail",
            "Bounce",
            "Bounce with Tail",
            "Fade",
        ]
        self.effect = settings.get("eeh.effect", "Rainbow")
        self.preview_effect = None
        self.palette = settings.get("eeh.palette", "RGB")
        self.preview_palette = None

        self.palettes = Palettes()

        self.last_cycle_time = time.time()
        self.current_cycle = 1
        self.position = 0 + SKIP_LED
        self.direction = 1

        self.colour_number = (
            0  # TODO: Should not be needed, current_cycle should be used
        )

        self.init_chain()

    def init_chain(self):
        slot = settings.get("eeh.slot", 1)
        slot2 = settings.get("eeh.slot2", "None")

        _pin_mapping = {
            1: 39,
            2: 35,
            3: 34,
            4: 11,
            5: 18,
            6: 3,
        }
        pin = _pin_mapping[slot]
        self.chain = neopixel.NeoPixel(Pin(pin), LED_COUNT + SKIP_LED)

        if slot2 != "None":
            pin2 = _pin_mapping[slot2]
            self.chain2 = neopixel.NeoPixel(Pin(pin2), LED_COUNT + SKIP_LED)
        else:
            self.chain2 = None

    def set_speed(self, speed, preview=0):
        if speed == "11!":
            speed = 11
        if speed != None:
            speed = int(speed)

        if preview == 1:
            self.preview_speed = speed
        else:
            settings.set("eeh.speed", speed)
            settings.save()
            self.speed = speed

    def get_speed(self):
        if self.preview_speed != None:
            return self.preview_speed
        else:
            return self.speed

    def get_speeds(self):
        speeds = list(range(12))
        string_speeds = [str(speed) for speed in speeds]
        # string_speeds[-1] = str(string_speeds[-1]) + "!"
        return string_speeds

    def set_brightness(self, brightness, preview=0):
        if brightness != None:
            brightness = int(brightness)

        if preview == 1:
            self.preview_brightness = brightness
        else:
            settings.set("eeh.brightness", brightness)
            settings.save()
            self.brightness = brightness

    def get_brightness(self):
        if self.preview_brightness != None:
            # print(self.preview_brightness)
            return self.preview_brightness
        else:
            # print(self.brightness)
            return self.brightness

    def get_brightnesses(self):
        brightnesses = list(range(5, 101, 5))
        string_brightnesses = [str(brightness) for brightness in brightnesses]
        return string_brightnesses

    def set_effect(self, effect, preview=0):
        if preview == 1:
            self.preview_effect = effect
        else:
            settings.set("eeh.effect", effect)
            settings.save()
            self.effect = effect

    def get_effect(self):
        if self.preview_effect != None:
            return self.preview_effect
        else:
            return self.effect

    def get_effect_list(self):
        return self.effect_list

    def set_palette(self, palette, preview=0):
        if preview == 1:
            self.preview_palette = palette
        else:
            settings.set("eeh.palette", palette)
            settings.save()
            self.palette = palette

    def get_palette(self):
        if self.preview_palette != None:
            return self.preview_palette
        else:
            return self.palette

    def cycle(self):
        current_time = time.ticks_ms()
        interval = 1000 / FPS_LIMIT

        # Check if enough time has passed since the last event
        if current_time - self.last_cycle_time >= interval:

            # Increment cycle
            self.current_cycle = self.current_cycle + self.get_speed()
            # print(self.current_cycle)
            if self.current_cycle >= 256:
                self.current_cycle = 0

            # print(self.current_cycle)
            # print("effects cycle")
            effect = self.get_effect()
            if effect == "Rainbow":
                self.rainbow()
            elif effect == "Cycle":
                self.bounce(0, 0)
            elif effect == "Cycle with Tail":
                self.bounce(0, 1)
            elif effect == "Bounce":
                self.bounce(1, 0)
            elif effect == "Bounce with Tail":
                self.bounce(1, 1)
            elif effect == "Fade":
                self.fade_between_colors()
            self.last_cycle_time = current_time

    def clear_leds(self):
        for i in range(LED_COUNT):
            self.chain[i + SKIP_LED] = (0, 0, 0)
            if self.chain2 != None:
                self.chain2[i + SKIP_LED] = (0, 0, 0)
        self.chain.write()
        if self.chain2 != None:
            self.chain2.write()
        # Needs altering for actual Hexpasions - remove ' + 1'

    # Function to set a single LED color
    def set_led(self, index, color, brightness=1.0):

        if index >= 0 + SKIP_LED and index < LED_COUNT + SKIP_LED:
            master_brightness = self.get_brightness() / 100

            r = int(color[0] * brightness * master_brightness)
            g = int(color[1] * brightness * master_brightness)
            b = int(color[2] * brightness * master_brightness)
            self.chain[index + SKIP_LED] = (r, g, b)
            if self.chain2 != None:
                self.chain2[index + SKIP_LED] = (r, g, b)

    def set_led_all(self, color):
        for i in range(LED_COUNT):
            self.set_led(i, color)
        self.chain.write()
        if self.chain2 != None:
            self.chain2.write()

    def rainbow(self):
        for i in range(LED_COUNT):
            pixel_index = (i * 256 // LED_COUNT) + self.current_cycle
            self.set_led(i, self.hsv_to_rgb(pixel_index / 256, 1.0, 1.0))
        self.chain.write()
        if self.chain2 != None:
            self.chain2.write()

    # TODO: Needs better name, both bounces and cycles
    def bounce(self, bounce=0, withTail=0):
        palette = self.palettes.get_palette(self.get_palette())

        current_colour = palette[self.colour_number]

        self.clear_leds()
        # print(self.palettes)
        self.set_led(self.position, current_colour)
        if withTail:
            tail1position = get_indices(
                list(range(0, LED_COUNT)), self.position, self.direction * -1
            )
            self.set_led(tail1position, current_colour, 0.25)
            tail2position = get_indices(
                list(range(0, LED_COUNT)), tail1position, self.direction * -1
            )
            self.set_led(tail2position, current_colour, 0.1)
        self.chain.write()
        if self.chain2 != None:
            self.chain2.write()

        # print(self.position)
        if bounce:
            self.position += self.direction
            if self.position < 0 + SKIP_LED or self.position >= LED_COUNT - SKIP_LED:
                self.direction *= -1
                self.position += self.direction
        else:
            if self.position >= LED_COUNT - SKIP_LED:
                self.position = 0
            else:
                self.position = self.position + 1

    # Function to fade between colors
    def fade_between_colors(self):
        # Get active palette colours
        colors = self.palettes.get_palette(self.get_palette())
        sorted_colours = sorted(colors.keys())

        key_before, key_after = keys_before_and_after(colors, self.current_cycle)

        color1 = colors[key_before]
        color2 = colors[key_after]
        # Interpolate colours
        # print(self.current_cycle)
        t = find_percentage(self.current_cycle, key_before, key_after)
        # print("t")
        # print(t)
        color = self.interpolate_color(color1, color2, t)

        # Set LEDs
        self.set_led_all(color)

    # Function to interpolate between two colors
    def interpolate_color(self, color1, color2, percent):
        """
        Interpolates between two RGB colors based on a percentage.

        Arguments:
        color1 : tuple
            RGB tuple representing the first color, e.g., (R, G, B).
        color2 : tuple
            RGB tuple representing the second color, e.g., (R, G, B).
        percent : float
            Percentage indicating the position between color1 and color2.
            Should be between 0.0 and 1.0, where 0.0 returns color1,
            1.0 returns color2, and values in between interpolate between them.

        Returns:
        tuple
            Interpolated RGB color tuple.
        """
        # Ensure percentage is between 0.0 and 1.0
        percent = max(0.0, min(percent, 1.0))

        # Linear interpolation for each RGB component
        interpolated_color = tuple(
            int(color1[i] + (color2[i] - color1[i]) * percent) for i in range(3)
        )

        return interpolated_color

    def hsv_to_rgb(self, h, s, v):
        if s == 0.0:
            return (v, v, v)
        i = int(h * 6.0)  # Assume int() truncates!
        f = (h * 6.0) - i
        p = int(v * (1.0 - s) * 255)
        q = int(v * (1.0 - s * f) * 255)
        t = int(v * (1.0 - s * (1.0 - f)) * 255)
        v = int(v * 255)
        i %= 6
        if i == 0:
            return (v, t, p)
        if i == 1:
            return (q, v, p)
        if i == 2:
            return (p, v, t)
        if i == 3:
            return (p, q, v)
        if i == 4:
            return (t, p, v)
        if i == 5:
            return (v, p, q)


def find_percentage(number, minimum, maximum):
    """
    Finds the percentage of a number between a minimum and maximum value.

    Arguments:
    number : float
        The number for which to find the percentage.
    minimum : float
        The minimum value.
    maximum : float
        The maximum value.

    Returns:
    float
        The percentage between minimum and maximum that the number represents.
    """
    # Ensure number is within the range of minimum and maximum
    number = max(minimum, min(number, maximum))

    # Calculate the percentage
    percentage = (number - minimum) / (maximum - minimum)

    return percentage


def keys_before_and_after(numbers_dict, given_number):
    """
    Finds the keys that are just before and just after a given number in a dictionary.
    If the given number is greater than any key in the dictionary, it returns the first key.
    If the given number is smaller than any key in the dictionary, it returns the last key.

    Arguments:
    numbers_dict : dict
        Dictionary containing integer keys.
    given_number : int
        The number for which to find the keys before and after.

    Returns:
    tuple
        A tuple containing the key before and the key after the given number.
    """
    keys = sorted(numbers_dict.keys())

    key_before = None
    key_after = None

    for key in keys:
        if key <= given_number:
            key_before = key
        if key > given_number:
            key_after = key
            break

    if key_before is None:
        key_before = keys[-1] if keys else None

    if key_after is None:
        key_after = keys[0] if keys else None

    return key_before, key_after


def get_indices(arr, index, direction=1):
    """
    Return the chosen array index and the one after, or before, wrapping around at the end of the array.

    :param arr: List of items.
    :param index: Chosen index.
    :param direction: Direction to move ('forward' or 'backward').
    :return: Tuple of the chosen item and the adjacent item in the array.
    """
    n = len(arr)

    if direction == 1:
        return arr[(index + 1) % n]
    elif direction == -1:
        return arr[(index - 1) % n]
    else:
        raise ValueError("Direction must be '1' or '-1'")
