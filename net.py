#! /usr/bin/env python3

import subprocess
import array
import fcntl
import struct
import socket


class Mycore(dict):
    """Bázová proxy třída na zpracování informací síťových rozhraní
    Třída se chová jako caseinsensitiv slovník. Takže pokud se instance jmenuje
    například wifina, pak je jedno jestli napíšeme:
    * wifina.get('rssi')
    * wifina.get('RsSi')
    * wifina['RSSI']
    * wifina['rSsI']
    pokaždé vrátí stejnou hodnotu. Zatím dostupné klíče:
    *společné:
    iface       - aktivní síťovka
    ap mac   - mac přístupového bodu
    ip           - přidělená ip adresa
    mac       - mac aktivní síťovky
    ap ip      - ip přístupového bodu
    """

    _MAX_DELKA_INTERFACE: int = 16
    _MAX_DELKA_POLE: int = 1024
    _BYTU_ROZHRANI: bytes = b'16s'
    _proc_dev: str = "/proc/net/dev"
    _proc_wireless: str = "/proc/net/wireless"
    _sys_class: str = "/sys/class/net/"
    _iface: str = None
    _SIOCGIWAP: int = 0x8B15  # get access point MAC addresses
    _HWADDR: int = 0x8927  # Get hardware address
    _SIOCGIFADDR: int = 0x8915  # get PA address
    _SIOCGIFDSTADDR = 0x8917  # get remote PA address

    def __init__(self):
        super().__init__()
        # otevření socketu
        self._sock: socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # vytvoříme pole plné nul do kterého bude os zapisovat výsledek
        # podle wirelles.h musí být dlouhé 32bytů
        self._pole: array = array.array('B', b"\0" * self._MAX_DELKA_POLE)

    def __iwreq(self, iface: str) -> bytes:
        """struktura dotazu"""
        return struct.pack(self._BYTU_ROZHRANI, bytes(iface, 'utf8'))

    def _volani(self, dotaz):
        """Volá ioctl"""
        # zjistíme si místo v paměti a jeho délku
        adresa, delka = self._pole.buffer_info()
        # iwreq má v tomto případě obsahovat název zařízení dlouhý 16 bytů a
        # ukazatel na místo o velikosti 32bytů.
        try:
            pointer = self.__iwreq(self._iface) + \
                struct.pack('PH', adresa, delka)
        # try:
            return fcntl.ioctl(self._sock.fileno(), dotaz, pointer)
        except (Exception, OSError):
            return False

    def active(self): pass

    @property
    def remoteip(self):
        """vzdálená IP ke které jsme připojeni"""
        if not self._iface:
            return False
        with open("/proc/net/arp", "r") as jj:
            for i in jj.readlines():
                if self.ap[1] in i:
                    return "AP IP", i.split(" ")[0]
            return False

    @property
    def ip(self):
        """vrátí vlastní IP"""
        if not self._iface:
            return False
        try:
            navrat = struct.unpack("4B", self._volani(self._SIOCGIFADDR)[20:24])
            return "IP", "{}.{}.{}.{}".format(*navrat)
        except (Exception, OSError):
            return False

    @property
    def mac(self):
        if not self._iface:
            return False
        # Tohle mě trvalo fakt dlouho skloubit. Z návratu volání ioctl vezmeme
        # šest bajtů od 18 až po 24 bajt. Ty převedem pomocí unpacku a to
        # vrátíme jako naformátovaný string
        try:
            navrat = struct.unpack("6B", self._volani(self._HWADDR)[18:24])
            return "MAC", "{:02X}:{:02X}:{:02X}:{:02X}:{:02X}:{:02X}".format(
                *navrat)
        except (Exception, OSError):
            return False

    @property
    def ap(self):
        if not self._iface:
            return False
        # MAC adresa AP pointu (k čemu jsme připojeni
        try:
            navrat = struct.unpack("6B", self._volani(
                self._SIOCGIWAP)[
                                         18:24])
            return "AP MAC", "{:02X}:{:02X}:{:02X}:{:02X}:{:02X}:{:02X}".format(
                *navrat)
        except (Exception, OSError):
            return False

    @property
    def _all_ifaces(self) -> set:
        """Vrátí všechna dostupná síťová rozhraní. Načte je z /proc/net/dev"""
        with open(self._proc_dev, "r") as ff:
            ab = set()  # 'ab' je prázdná množina
            for dd in ff.readlines():
                if ":" not in dd:  # pokud na řádku není dvojtečka...
                    continue  # ... ignoruj ho
                # jinak ho zpracuj a přidej do množiny
                ab.add(dd.split(":")[0].lstrip(" ").rstrip(" "))
        return ab

    @property
    def _selekce(self) -> tuple:
        """vrací Entici (tuple). První člen entice obsahuje seznam wifi
        síťovek. Druhý člen obsahuje seznam zbylých (eth) síťovek"""
        wifis = set()  # prázdná množina určená k návratu wifin
        eths = set()  # prázdná množina k návratu ostatních síťovek
        for i in self._all_ifaces:  # projde všechny dostupné síťovky
            self._flag = False
            soubor = self._sys_class + i + "/uevent"  # a přečte jejich uevent
            with open(soubor, "r") as uka:
                for ab in uka.readlines():  # projde řádky ueventu
                    if "wlan" in ab:  # pokud narazí na klíčové slovo wlan,
                        self._flag = True
            if self._flag:
                wifis.add(i)  # uloží název wifi síťovky do množiny
            else:
                eths.add(i)  # uloží název newifi síťovky
        return wifis, eths

    @property
    def info(self) -> dict:
        """Vrátí slovník obsahující informace o aktivní síťovce"""
        aa = {}
        for i in dir(self):
            if not i.startswith("_") and "info" not in i:
                try:
                    key, value = getattr(self, i)
                    if key:
                        aa.setdefault(key, value)  # = a + '"{}":36,'.format(i)
                        self.__setitem__(key, value)
                        # když metoda vrátí hodnoty které nejdou naparsovat, což
                        # udělá nechtěná metoda, vznikne výjimka. Ta je ošetřená
                        # nic nedělánním a program pokračuje dál bez uložení
                        # nechtěných dat.
                except(Exception, BaseException):
                    pass
        # a = a[:-1] + "}"
        return aa

    def get(self, key: str):
        # Dělá funkci caseinsensitiv
        for la, val in self.items():
            if key.lower() == str(la).lower():
                return val
        return

    def __missing__(self, key: str):
        # když nemáme požadovaný klíč, juknem jestli není napsán trochu
        # jinak. Pokud ne vrátí None.
        return self.get(key)

    def open_extern(self, a):
        subprocess.run(['swaymsg', 'exec', 'st', 'nmtui'],
                       stdout=subprocess.DEVNULL)
        return self, a


class Wlan(Mycore):
    """Dědičná třída informující o wlan síti
    dtto jako Mycore
    *+:
    essid       - essid přístupového bodu
    rssi -> int, int - vrací seznam dvou parametrů. První parametr je nastav
    signálu v procentech. A druhý parametr je nastav signálu v dBm.
    """

    # /usr/include/linux/wireless.h
    _SIOCGIWESSID: int = 0x8B1B  # get ESSID
    # SIOCGIWRANGE: int = 0x8B0B  # Get range of parameters
    # _SIOCGIWAP: int = 0x8B15  # get access point MAC addresses
    # SIOCGIWSTATS: int = 0x8B0F  # get /proc/net/wireless stats
    # SIOCGIWFREQ: int = 0x8B05  # get channel/frequency (Hz)
    # SIOCGIWSENS: int = 0x8B09  # get sensitivity (dBm)
    _wireless: str
    __dbm: int

    def __init__(self):
        super().__init__()
        if self.active:  # aktivuje nezbytné proměnné
            pass
        if self.info:
            pass

    @property
    def active(self):
        """Vrátí aktivní připojení nebo None a nastaví _iface"""
        with open(self._proc_wireless, "r") as ff:
            for i in ff.readlines():
                if ":" not in i:
                    continue
                self._wireless = i
                self._iface = i.split(":")[0].lstrip(" ").rstrip(" ")
        return "Iface", self._iface

    @property
    def ifaces(self) -> set:
        """Vrátí dostupné wifi síťovky"""
        return self._selekce[0]

    @property
    def essid(self):
        """vydoluje název essidu"""
        # zavolá ioctl metodou "_volani"
        self._volani(self._SIOCGIWESSID)  # dotaz na Essid
        # výsledek je zapsán v poli, takže nepotřebuje návratovou
        # hodnotu.
        # ESSID vrátí jako string
        kuk = self._pole.tobytes().decode('utf-8').translate(b' ').rstrip()
        if kuk == "":
            return False
        return "ESSID", kuk

    @property
    def rssi(self):
        if not self._iface:
            return False
        self.__dbm = int(self._wireless.split(' ')[6][:-1])
        # fce separuje rssi ze souboru /proc/net/wireless kterýž je
        # "proxy" soubor volání jádra. Stále aktuální. rssi je v dBm.
        # Převede ho na %
        # super signál (mezní nastav)
        perfekt = -20
        # špatný signál (mezní nastav)
        bad = -85
        zwis = perfekt - bad
        # Vzorec na přepočet dBm na % jsem našel u Linuse:
        # https://github.com/torvalds/linux/blob
        # /9ff9b0d392ea08090cd1780fb196f36dbb586529/drivers/net/wireless/intel
        # /ipw2x00/ipw2200.c#L4321
        rsi = (100 * zwis * zwis - (perfekt - self.__dbm) *
               (15 * zwis + 62 * (perfekt - self.__dbm))) / (zwis * zwis)
        if rsi > 100:
            rsi = 100
        elif rsi < 1:
            rsi = 0
        return "Rssi", (int(rsi), self.__dbm)
    
    def __repr__(self):
        if self.essid:
            return "{} {:3}%".format(self.essid[1], self.rssi[1][0])
        else:
            return "Bez wifi"


class Eth(Mycore):
    """Dědičná třída informující o eth síti
    dtto jako Mycore
    """
    # /usr/include/linux/sockios.h
    # Socket configuration controls.
    # SIOCETHTOOL = 0x8946  # Ethtool interface
    # SIOCGIFNAME = 0x8910  # get iface name
    # SIOCGIFCONF: int = 0x8912  # get iface list
    # SIOCGIFFLAGS = 0x8913  # get flags
    # _SIOCGIFADDR: int = 0x8915  # get PA address
    # SIOCGIFDSTADDR = 0x8917  # get remote PA address
    # SIOCGIFBRDADDR = 0x8919  # get broadcast PA address
    # SIOCGIFNETMASK = 0x891b  # get network PA mask
    # SIOCGIFMTU = 0x8921  # get MTU size
    # SIOCGIFHWADDR: int = 0x8927  # Get hardware address

    def __init__(self):
        super().__init__()
        if self.active:
            pass
        if self.info:
            pass

    @property
    def active(self):
        """Vrátí aktivní připojení nebo "lo" a nastaví _iface"""
        for i in self.ifaces:
            with open(self._sys_class + i + "/operstate", "r") as face:
                if "up" in face:
                    self._iface = i
        if not self._iface:
            # print("neni iface na eth")
            self._iface = "lo"
        return "Iface", self._iface

    @property
    def ifaces(self) -> set:
        """vrátí dostupné newifi síťovky"""
        return self._selekce[1]


# wifi = Wlan()


def sit():
    """ fce vracející wifi ssid a sílu signálu"""
    wifi = Wlan()
    if wifi["essid"] is None:
        return "Bez wifi"
    else:
        return "{} {:3}%".format(wifi["essid"],
                                 wifi["rssi"][0])

# a = Wlan()
# b = Eth()
# print(a["Essid"])
# print(a["ifaCE"])
# print(a)
# print(b)
# print(sit())
