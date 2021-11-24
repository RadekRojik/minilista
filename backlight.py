#! /usr/bin/env python3

from conf import BACKLIGHT_FILE, BACKLIGHT_CHARS, BR, MBR
# import wobproxy


class Backlight:
    """
    monit = Backlight()
    monit.nastav("max")
    monit.nastav("+2")
    """
    def __init__(self, znaky=BACKLIGHT_CHARS):
        self.brightness: int = 0
        self.max_brightness: int = 0
        self.navrat: str = ""
        self.znaky: list = znaky
        self.aktual: int = 0
        with open(BACKLIGHT_FILE+BR, encoding="utf8") as ff:
            self.brightness = int(ff.readline())
        with open(BACKLIGHT_FILE+MBR, encoding="utf8") as ff:
            self.max_brightness = int(ff.readline())
        d = self.brightness // round(self.max_brightness / len(self.znaky))
        self.navrat = "{: =3d}% {}".format(self.value, self.znaky[d])

    @property
    def value(self):  # vrátí aktuální hodnotu v procentech
        return self.brightness * 100 // self.max_brightness

    def nastav(self, po: str):
        """Za znaménkem (+ -) je hodnota v procentech o kolik se má podsvit
        nastavit. Pokud překročí zadané meze nastaví se povolené maximum
        respektive minimum. Zadané meze se dají překročit jednoduše, proto je to
        takto ošetřeno.
        """
        if po.startswith("+"):
            self.aktual = self.value + int(po.split("+")[1:][0])
            a = round(self.max_brightness / 100 * self.aktual)
            if a > self.max_brightness:
                a = self.max_brightness
        elif po.startswith("-"):
            self.aktual = self.value - int(po.split("-")[1:][0])
            a = round(self.max_brightness / 100 * self.aktual)
            if a < 0:
                a = 0
        elif po == "max":
            a = self.max_brightness
            self.aktual = 100
        elif po == "min":
            a = 0
            self.aktual = 0
        else:
            return
        self.zapis(a)  # poznámka no.1.

    @staticmethod
    def zapis(a: int):
        with open(BACKLIGHT_FILE+BR, "w") as br:
            br.write(str(a))
            # wobproxy.wob(self.aktual)
        return

    def __repr__(self):
        return self.navrat


# ####################
# Použití:
# monit = Backlight()
# monit.nastav("min")
# print(monit.value)
