#! /usr/bin/env python3
"""
# Created by Radek
"""

import power
import backlight
import net
import cas
import sys
import ast
from time import sleep
from threading import Thread


# Slovník obsahující (název rámce; myšítko) a (třídu, metodu nebo funkci;
# parametry) k vykonání
# myšítko:
# 1 levé
# 2 prostřední
# 3 pravé
# 4 rolování nahoru
# 5 rolování dolu
import zvuk

hauptdic: dict = {("backlight", 4): (backlight.Backlight.nastav, "+2"),
                  ("backlight", 5): (backlight.Backlight.nastav, "-2"),
                  ("sound", 4): (zvuk.Zvuk.setspk, "+1"),
                  ("sound", 5): (zvuk.Zvuk.setspk, "-1"),
                  ("sound", 3): (zvuk.Zvuk.open_extern, ""),
                  ("net", 3): (net.Wlan.open_extern, "")}

# Klíčový slovník kde je klíčem název rámce pro json a hodnotou je třída, která
# přes __repr__ vrací výsledek. Tím se zajišťuje jednoduchý výpis a zároveň
# třída funguje jako instance(self) při vstupu událostí z myši
zobraz: dict = {"sound": zvuk.Zvuk,
                "backlight": backlight.Backlight,
                "net": net.Wlan,
                "power": power.Power,
                "cas": cas.Cas}


def print_line(zprava):  # výpis stringu na st. výstup
    print(zprava, end='\n', file=sys.stdout, flush=True)


def vypis():
    print_line('{ "version": 1, "click_events":true}')
    # začni se nekonečným blokem
    print_line('[')
    # první vnořený blok bude prázdný
    print_line('[]')
    while True:
        # první vnořený blok bude prázdný
        # print_line(', []')
        # počátek vnořeného bloku
        j = ', ['
        # načti vnitřek bloku
        for i in zobraz:
            j = j + '{{"name":"{}","full_text":"{}", "color":"#FFFFFF"}},'. \
                format(i, zobraz[i]())
            # drdr = open("blbydata.txt", "a")
            # drdr.write("{}\n".format(i))
            # drdr.close()
        # smaž poslední čárku
        j = j[:-1]
        # a ukonči blok
        j = j + ']'
        # blok pošli na st. výstup
        print_line(j)
        # a chvilku počkej
        sleep(0.5)


def vstup():
    # Načítání události myši ze st. vstupu
    for gg in sys.stdin:
        # validace řádku pro ast
        if ',{ "name":' not in gg:
            # nesouhlasí, vrať se na začátek smyčky a čekej na další event
            continue
        # ořízni první znak(čárku)
        gg = gg[1:]
        # a převeď json na slovník
        ll = ast.literal_eval(gg)
        try:
            # vykonání metody ze slovníku
            hauptdic[ll["name"], ll["button"]][0](zobraz[ll["name"]](),
                                                  hauptdic[ll["name"],
                                                           ll["button"]][1])
        except(Exception, BaseException):
            # pakliže taková metoda nebo událost není, tak to ignoruj
            pass
        # fi = open("blbydata.txt", "a")
        # fi.write("{}".format(gg))
        # fi.close()


# Protože i3wm a sway načítají bar ze stdout. A události myši ze stdin který
# čeká dokud něco nedostane. Je třeba ty dva procesu vstupu a výstupu oddělit.
v = Thread(target=vstup)
v.start()
vypis()
