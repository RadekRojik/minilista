#! /usr/bin/env python3
"""
# Created by Radek
"""

from conf import BAT_FILE, POW_FILE, POWER_CHARS


class Power:
    """Třída Power vrací jen stav baterie a nabíjení z adresy v sysu
    Může přijmout parametr 'adresa' a to jinou adresu kam kernel ukládá stav
    baterie. Ještě jde změnit nastav 'baterka' na vlastní značky, kde
    poslední značka znamená napájení.
    """
    def __init__(self, bat_soubor=BAT_FILE, pow_soubor=POW_FILE,
                 baterka=POWER_CHARS):
        # Pomocné proměnné
        self.__b, self.__c = 0, 0
        # Přiřadíme si baterky
        self.baterka = baterka
        # Proměnná momentální kapacity
        self.__capacita: int = 0
        # jemnost určuje kroky v baterce.
        self.__jemnost: int = 100 // (len(self.baterka) - 2)

        # otevřeme soubor s údaji o stavu baterie
        with open(bat_soubor, encoding="utf8") as ff:
            # a budeme ho procházet řádek po řádku
            for i in ff:
                # pokud v řádku bude rovnítko
                if "POWER_SUPPLY_CAPACITY=" in i:
                    # rozdělíme řádek na rovnítku a přiřadíme klíč a hodnotu
                    klic, hodnota = i.split("=", 1)
                    # uložíme aktuální kapacitu
                    self.__capacita = int(hodnota)
                    # a spočítáme si pořadí buřta
                    self.__b = self.__capacita // self.__jemnost

        # otevřeme soubor s údaji o napájení
        with open(pow_soubor, encoding="utf8") as ff:
            # a budeme ho procházet řádek po řádku
            for i in ff:
                # test na status napájení
                if "POWER_SUPPLY_ONLINE=1" in i:
                    # napájíme dáme do Céčka poslední hodnotu baterky
                    self.__c = len(self.baterka) - 1

        # pokud je Céčko větší(jsme v zásuvce) než béčko uložíme do béčka céčko
        if self.__c > self.__b:
            self.__b = self.__c

    def __repr__(self):
        # vrátíme kapacitu s procentem a znakem napájení či 'buřtu'
        return "{}% {}".format(self.__capacita, self.baterka[self.__b])


# print(Power())
