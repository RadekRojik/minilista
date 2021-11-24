#! /usr/share/env python3

import subprocess
# import wobproxy
from conf import SOUND_MIC, SOUND_SPK

# Piktogramy. První piktogram má vždy znamenat 'mute' zařízení a další
# stupňující se hlasitost. Na počtu nezáleží avšak minimum jsou dva
# včetně mute piktogramu.
# print(chr(int("1f507",16)))
# MIC = ("", "")
# REPR = ("🔇", "🔈", "🔉", "🔊")


class Zvuk:
    """Bohužel linux je dost roztříštěný a nemá co se týče zvuku žádné
    jednotnější API. Já mám pulseaudio. Blbý je, že PA nemá
    funkční přístup ani přes d-bus. A ve sračkách typu systemd se hrabat
    nebudu. Takže jsem si ovládání napsal voláním přímo pacmd(sosání
    informací) a pactl(nastavování) přes subprocess.
    Zkoušel jsem to i přes /proc/asound/. Což funguje díky PA velice těžce.
    Nehledě na to, že PA dovoluje zesílení nad 100%, což ostatní těžce nesou(
    asound to ořízne, wobi zhavaruje)
     # Použití:
        zvukovka = Zvuk()
        print("Mic: {}".format(zvukovka.getmic()))
        print("Rep: {}".format(zvukovka.getspk()))
         Nebo:
        print(zvukovka.getall())
         Anebo:
        print(zvukovka)
         Anebo:
        print(Zvuk())
        p = Zvuk()
        Zvuk().spk = "+2"  # zesílení o dvě procenta
        Zvuk().spk = "mute"
        Zvuk().mic = "MUTE"
        print(Zvuk().spk)
        print(Zvuk().mic)
     """
    def __init__(self):
        self.MIC_CALL = "list-sources"  # vstupní periferie
        self.SPK_CALL = "list-sinks"  # výstupní periférie
        self.MIC_VOL = "set-source-volume"  # nastavení vstupů
        self.MIC_MUTE = "set-source-mute"  # nastavení mute vstupu
        self.SOURCE = "@DEFAULT_SOURCE@"  # defaultní vstup
        self.SPK_VOL = "set-sink-volume"  # nastavení výstupů
        self.SPK_MUTE = "set-sink-mute"  # mute výstupu
        self.SINK = "@DEFAULT_SINK@"  # defaultní výstup
        self.piktogramy = ()
        # self.volani = volani
        # self.__delka = len(self.piktogramy)-1
        self.__delka = 0  # len(self.piktogramy) - 1
        self.__flag = False  # flag ukazuje či jsme v aktuální periferii
        self.__pos = 1
        self.__levy = 0
        self.__pravy = 0
        self.__volume = 0
        self.__table = {32: None, 37: None}  # znaky translate tabulky

    def __getitem(self, volani):
        # metoda vrací volume a mute aktuální periférie
        self.__delka = len(self.piktogramy) - 1
        descriptor = subprocess.run(["pacmd", volani],
                                    stdout=subprocess.PIPE,
                                    check=True, text=True)
        for i in descriptor.stdout.splitlines():
            if "* index:" in i:  # hvězdička a index ukazuje na aktuálně
                # používanou periferii. Pokud na ně narazíme
                self.__flag = True  # nastavíme flag na načítání informací
                # z výstupu
            if self.__flag:
                if "muted: yes" in i:  # pokud je periférie muted. Nastav
                    # piktogram z nulté pozice. A nastav flag aby se nenačítali
                    # další falešné informace.
                    self.__pos = 0
                    self.__flag = False
                elif "volume:" in i:  # najdeme řádky s "volume"
                    if "base" not in i:  # vyloučíme nechtěný volume info
                        # Načteme info levého kanálu
                        self.__levy = int(i.translate(self.__table).
                                          split("/")[1])
                        # Info pravého kanálu
                        self.__pravy = int(i.translate(self.__table).
                                           split("/")[3])
                        # Uděláme z nich průměr
                        self.__volume = (self.__levy + self.__pravy) // 2
                        # A nastavíme pozici piktogramu
                        self.__pos = int(self.__volume // (100 /
                                                           self.__delka) + 1)
                        if self.__pos == 0:
                            self.__pos = 1
                        elif self.__pos > self.__delka:
                            self.__pos = self.__delka

        if self.__flag:
            # pokud je flag pravdivý vrátíme průměr volume a piktogram "síly"
            return "{:3}% {:}".format(self.__volume,
                                      self.piktogramy[self.__pos])
        else:
            # flag není, výstup je mute. Pošlem jen prví mute piktogram
            # formátovaný aby nelítali informace na liště sem tam.
            return "{:>6}".format(self.piktogramy[0])

    @staticmethod
    def __vola(a, b, c):
        # nastavovací metoda
        subprocess.run(['pactl', a, b, c])
        return

    @property
    def mic(self):
        # optáme se na vstupní zařízení
        return self.getmic()

    def getmic(self):
        # optáme se na vstupní zařízení
        self.piktogramy = SOUND_MIC
        return self.__getitem(self.MIC_CALL)

    @mic.setter
    def mic(self, a: str):
        # nastavíme vstup
        a = a.lower()
        if "+" in a:  # při plusu přidáme
            self.__vola(self.MIC_VOL, self.SOURCE, a+"%")
        elif "-" in a:  # při mínusu ubereme
            self.__vola(self.MIC_VOL, self.SOURCE, a+"%")
        elif "mute" in a:  # při mute přepneme mute
            self.__vola(self.MIC_MUTE, self.SOURCE, "toggle")
        return

    @property
    def spk(self):
        # optáme se na výstup
        return self.getspk()

    def getspk(self):
        # optáme se na výstup
        self.piktogramy = SOUND_SPK
        return self.__getitem(self.SPK_CALL)

    @spk.setter
    def spk(self, a: str):
        self.setspk(a)
        return 
    
    def setspk(self, a: str):
        # nastavíme výstup
        a = a.lower()
        if "+" in a:  # při plusu přidáme zvuk
            self.__vola(self.SPK_VOL, self.SINK, a + "%")
        elif "-" in a:  # při mínusu ubereme zvuk
            self.__vola(self.SPK_VOL, self.SINK, a + "%")
        elif "mute" in a:  # při mute přepneme mute zvuku
            self.__vola(self.SPK_MUTE, self.SINK, "toggle")
        else:
            return
        self.getrepr()
        return

    def getall(self):
        # ukaž nastavení výstupu a vstupu zároveň
        m = self.getmic()
        r = self.getspk()
        return r + m

    def getrepr(self):
        self.getspk()
        # wobproxy.wob(self.__volume)
        return self.__volume

    def open_extern(self, a):
        subprocess.run(['swaymsg', 'exec', 'pavucontrol'],
                       stdout=subprocess.DEVNULL)
        return self, a

    def __repr__(self):  # proxy getall
        return self.getall()


# Zvuk().spk="+2"
