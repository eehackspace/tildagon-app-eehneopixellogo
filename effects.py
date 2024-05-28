import time
import neopixel
from machine import Pin

from .palettes import Palettes

# Constants
LED_COUNT = 12  # Number of NeoPixels
SKIP_LED = (
    1  # How many LEDs at the beginning of the chain to skip, usefor for Sim testing
)
PIN = 21  # Pin connected to the NeoPixels

FPS_LIMIT = 50  # Limit FPS


class Effects:
    def __init__(self):
        self.speed = 5
        self.preview_speed = None
        self.effect_list = ["Rainbow", "Bounce", "Fade"]
        self.effect = "Fade"
        self.preview_effect = None
        self.palette = "RGB"
        self.preview_palette = None

        self.palettes = Palettes()

        self.last_cycle_time = time.time()
        self.current_cycle = 240
        self.position = 0 + SKIP_LED
        self.direction = 1
        self.chain = neopixel.NeoPixel(Pin(PIN), LED_COUNT + SKIP_LED)
        # print("effects init")

    def set_speed(self, speed, preview=0):
        if speed == "11!":
            speed = 11

        if preview == 1:
            self.preview_speed = speed
        else:
            self.speed = speed

    def get_speed(self):
        if self.preview_speed != None:
            return self.preview_speed
        else:
            return self.speed

    def get_speeds(self):
        speeds = list(range(12))
        speeds[-1] = str(speeds[-1]) + "!"
        return speeds

    def set_effect(self, effect, preview=0):
        if preview == 1:
            self.preview_effect = effect
        else:
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
            self.palette = palette

    def get_palette(self):
        if self.preview_palette != None:
            return self.preview_palette
        else:
            return self.palette

    def cycle(self):
        current_time = time.time()
        interval = 1 / FPS_LIMIT
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
            elif effect == "Bounce":
                self.bounce()
            elif effect == "Fade":
                self.fade_between_colors()
            self.last_cycle_time = current_time

    def clear_leds(self):
        for i in range(LED_COUNT):
            self.chain[i + SKIP_LED] = (0, 0, 0)
        self.chain.write()
        # Needs altering for actual Hexpasions - remove ' + 1'

    # Function to set a single LED color
    def set_led(self, index, color, brightness=1.0):
        r = int(color[0] * brightness)
        g = int(color[1] * brightness)
        b = int(color[2] * brightness)
        self.chain[index + SKIP_LED] = (r, g, b)
        self.chain.write()

    def set_led_all(self, color):
        for i in range(LED_COUNT):
            self.chain[i + SKIP_LED] = color
        self.chain.write()

    def rainbow(self):
        for i in range(LED_COUNT):
            pixel_index = (i * 256 // LED_COUNT) + self.current_cycle
            self.set_led(i, self.hsv_to_rgb(pixel_index / 256, 1.0, 1.0))

    def bounce(self):
        palette = self.palettes.get_palette(self.get_palette())
        self.clear_leds()
        # print(self.palettes)
        self.set_led(self.position, palette)
        self.set_led(self.position - self.direction, palette, 0.25)
        self.set_led(self.position - self.direction * 2, palette, 0.1)
        # print(self.position)
        self.position += self.direction
        if self.position < 0 or self.position >= LED_COUNT:
            self.direction *= -1
            self.position += self.direction

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
