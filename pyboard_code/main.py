import machine, utime, _thread
import wifi, animations, webSrv, songs

# touch pins: 4, 0, 2, 15, 13, 12, 14, 27, 33, 32
# value error on 0, 2. 13, 4: 50%
touch_pin = 15
touch = machine.TouchPad(machine.Pin(touch_pin))
touch_val = 1000
touch_threshold = 180

# ldr specific values
ldr_pin = 36
ldr = machine.ADC(machine.Pin(ldr_pin))

# thread specific values
_thread.replAcceptMsg(True)
animation_thread = 100
wait_before_start_thread = 2000

sound_thread = 100
alarm_song = "Tetris"

# alarm-clock specific values
rtc = machine.RTC()
timer = machine.Timer(1)

# will become True if alarm is running so touch is used to disable alarm
is_alarm_running = False

# blink once to signalize that system's up
animations.blink(count = 2, time_on=50)

def handleAnimations(animation_name=None):
    """ stopps running animation thread and creates a new thread.
    If animation_name is given, it creates a thread with animations.start(animation_name)
    if animation_name == None it creates a thread with animations.next()
    animation_name: (String) name of the animation to start
    """
    global animation_thread
    _thread.notify(0, _thread.EXIT)

    if animation_name == None:
        utime.sleep_ms(50)
        animation_thread = _thread.start_new_thread("animation", animations.next, () )
    else:
        print("starting animation {}".format(animation_name))
        utime.sleep_ms(wait_before_start_thread)
        animation_thread = _thread.start_new_thread("animation", animations.start, (animation_name,))

def handleSoundThread(song):
    """ stopps running sound thread and starts a new thread with value saved in 'song'
    song: (String) name of the song to start
    """
    global sound_thread

    _thread.notify(sound_thread, _thread.EXIT)
    utime.sleep_ms(wait_before_start_thread)
    sound_thread = _thread.start_new_thread("song", songs.find_song, (song,))

def convertDateOrTimeToTuple(s):
    """ splits given String by '.' or ':'. If resulting List has len = 4 it is
    interpreted as date and will be converted in (yyyy, mm, dd). if value for year
    has two digits, 2000 is added.
    s: string in format hh:mm or dd.mm.yy(yy)
    return: Tuple (hh, mm) or (yyyy, mm, dd)
    """
    if s.find(".") >= 0:
        s_list = list(int(i) for i in  s.split("."))
    else:
        s_list = list(int(i) for i in s.split(":"))
    print("converted: {}".format(s_list))
    if len(s_list) == 3:
        s_list.reverse()
        print("reversed: {}".format(s_list))
        if len(str(s_list[0])) == 2:
            s_list[0] += 2000

    return tuple(s_list)


def setSystemTime(date, time):
    """converts date and time (String) in integer values and sets system time
    date: date as String (dd.mm.yy)
    time: time as String (hh:mm)
    """
    #date = convertDateOrTimeToTuple(date)
    #time = convertDateOrTimeToTuple(time)
    if date.find(":") >= 0:
        date_list = list(int(i) for i in  date.split(":"))
    else:
        date_list = list(int(i) for i in date.split("."))
    date_list.reverse()
    print("reversed: {}".format(date_list))
    if len(str(date_list[0])) == 2:
        date_list[0] += 2000
    date = tuple(date_list)

    if time.find(".") >= 0:
        time = tuple(int(i) for i in  time.split("."))
    else:
        time = tuple(int(i) for i in time.split(":"))

    print("initializing time: {}".format(date+time))
    rtc.init(date+time)


def _timer_callback(timer):
    """ Timer callback function to start playing alarm_song
    and start "blink" animation
    timer: according timer
    """
    global is_alarm_running
    handleSoundThread(alarm_song)
    handleAnimations("blink")
    is_alarm_running = True

def setAlarmTime(time):
    """ calculates period to alarm from given time + system time
    time: time as String (hh:mm) when alarm should run
    """
    seconds_per_day =  60 * 60 * 24
    time = convertDateOrTimeToTuple(time)

    curr_time_toup = utime.localtime()
    curr_time_sec = utime.mktime(curr_time_toup)

    alarm_time_sec = utime.mktime(curr_time_toup[0:3] + time + curr_time_toup[5:])

    period_sec = alarm_time_sec - curr_time_sec
    if period_sec < 0:
        period_sec += seconds_per_day

    timer.init(period = period_sec*1000, mode = timer.ONE_SHOT, callback= _timer_callback )

while True:
    # read touch pin
    try:
        touch_val = touch.read()
    except ValueError:
        # if ValueError occures print on terminal and blink 3 times in red
        print("ValueError while reading touch_pin")
        animations.blink(color=0xff0000, count=3, time_on=50, time_off=50)

    # if touch is registered
    if touch_val < touch_threshold:
        if is_alarm_running:
            # if alarm is running stop sound and animation thread,
            # set is_alarm_running to False
            handleSoundThread("")
            is_alarm_running = False
        else:
                # if no alarm is running print output and start function
                # handleAnimations() without argument to start next animation
            print("touched!! value: {}".format(touch_val))
            handleAnimations()

    # read threadMessage from microWebSrv
    msg = _thread.getmsg()
    # check if message is String
    if msg[0] == 2:
        # convert String in dictionary
        values_dict = eval(msg[2])

        # call function according to value of "button"
        if values_dict["button"] == "light":
            handleAnimations(animation_name = values_dict["light"])
        elif values_dict["button"] == "sound":
            alarm_song = values_dict["sound"]
            handleSoundThread(values_dict["sound"])
        elif values_dict["button"] == "datetime":
            setSystemTime(values_dict["date"], values_dict["time"])
        elif values_dict["button"] == "alarm":
            setAlarmTime(values_dict["alarm"])

    # read value of ldr, map to value range of brightness and set brightness of LED Strip
    animations.set_brightness(int(ldr.read() / 1100 * 255))
    # sleep to avoid system crash
    utime.sleep_ms(200)
