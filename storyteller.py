import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522 as RFID
import vlc
import os
import random
from gpiozero import Button
import re
import signal
import sys

def signal_handler(signal, frame):
    print("\nCleaning up and quitting...")
    GPIO.cleanup()
    sys.exit(0)

btn_play_pause = Button(17)
btn_vol_up = Button(27)
btn_vol_down = Button(22)
manual_pause = False

def vol_up():
    adjust_volume(10, player)

def vol_down():
    adjust_volume(-10, player)

def play_pause():
    global manual_pause
    global no_tag_count
    if no_tag_count <= 1:
        manual_pause = not manual_pause
        player.pause()

btn_play_pause.when_released = play_pause
btn_vol_up.when_released = vol_up
btn_vol_down.when_released = vol_down

stories_path = '/home/pi/stories/'
vlci = vlc.Instance()
player = vlci.media_player_new()
current_story = None

def read_tag():
    rfid = RFID()
    try:
        id, text = rfid.read()
    finally:
        GPIO.cleanup()
    if 'text' in locals():
        return text
    else:
        return None

def play_story(tagname, player):
    """
    We can just have the tagname be the file or directory
    and check which it is before processing
    """
    global manual_pause
    file = stories_path + str(tagname)
    print ("Starting playback of " + tagname)
    if os.path.isdir(file):
        contents = os.listdir(file)
        media = vlci.media_new(stories_path + str(filerandom.choice(contents)))
        player.set_media(media)
    elif os.path.isfile(file):
        media = vlci.media_new(file)
        player.set_media(media)
    else:
        raise Exception('No file or directory found at ' + file)
    player.play()
    player.audio_set_mute(False)
    manual_pause = False
    player.set_pause(0)
    return

def adjust_volume(value, player):
    vol = player.audio_get_volume()
    newvol = max(0,min(100,vol + value))
    player.audio_set_volume(newvol)
    return

rfid = RFID()
no_tag_count = 0
while True:
    text = None
    try:
        id, data = rfid.dump_ul_no_block()
        text = re.search("(?<=\<s\>).+(?=\</s\>)",data).group()
    except:
        pass
    if text:
        text = text.strip()
        if current_story:
            if current_story == text:
                print("Continuing playback of " + text)
                no_tag_count = 0
                if not manual_pause:
                    player.set_pause(0)
                continue
            else:
                print("Stopping playback of " + current_story)
                player.set_media(None)
                current_story = text
                no_tag_count = 0
                play_story(text, player)
                pass
        else:
            current_story = text
            play_story(text, player)
            no_tag_count = 0
    else:
        if current_story:
            no_tag_count = no_tag_count + 1
            if no_tag_count > 30:
                print("Stopping playback")
                player.audio_set_mute(1)
                player.set_media(None)
                player.audio_set_mute(0)
                current_story = None
                no_tag_count = 0
                continue
            elif no_tag_count > 1:
                print("Tag removed - pause (" + str(no_tag_count) + ")")
                player.set_pause(1)
            continue