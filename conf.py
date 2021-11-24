#! /usr/bin/env python3
"""
# Created by Radek
"""


# Power
BAT_FILE = "/sys/class/power_supply/BAT0/uevent"
POW_FILE = "/sys/class/power_supply/ADP0/uevent"
POWER_CHARS = ("", "", "", "", "", "")

# Backlight
BACKLIGHT_FILE = "/sys/class/backlight/amdgpu_bl0"
BR: str = '/brightness'
MBR: str = '/max_brightness'
BACKLIGHT_CHARS = "", ""

# Wifi
WIFI_NET = "/sys/class/net"
WIFI_DEV = "/proc/net/dev"
WIFI_WIRELESS = "/proc/net/wireless"

# Sound
SOUND_MIC = ("", "")
SOUND_SPK = ("🔇", "🔈", "🔉", "🔊")
