from machine import RTC

time = RTC()

def setCurrentTime(year, month, day, hour, min, sek):
    time.init((year, month, day, hour, min, sek, 0, 0))
