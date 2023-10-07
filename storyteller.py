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

def vol_up():
    adjust_volume(5, player)

def vol_down():
    adjust_volume(-5, player)

def next_shuffle(stories):
    if len(stories) < 1:
        global shuffle_list
        random.shuffle(shuffle_list)
    shuffled_story = str(stories.pop())
    media = vlci.media_new(stories_path + shuffled_story)
    print ("Shuffle: Starting playback of " + shuffled_story)
    player.set_media(media)
    player.play()
    player.audio_set_mute(False)
    manual_pause = False
    player.set_pause(0)
    return stories

def play_random():
    global contents
    shuffled_story = str(random.choice(contents))
    media = vlci.media_new(stories_path + shuffled_story)
    print ("Shuffle: Starting playback of " + shuffled_story)
    player.set_media(media)
    player.play()
    player.audio_set_mute(False)
    manual_pause = False
    player.set_pause(0)
    return


def shuffle():
    global shuffle_on
    global shuffle_list
    if not shuffle_on:
        print('Starting shuffle')
        shuffle_on = True
        shuffle_list = next_shuffle(shuffle_list)
        return
    else:
        shuffle_on = False
        print("Ending shuffle")
        player.set_media(None)
        current_story = None
        no_tag_count = 0
        return

def play_pause():
    global manual_pause
    global no_tag_count
    if no_tag_count <= 1:
        manual_pause = not manual_pause
        player.pause()

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
        media = vlci.media_new(stories_path + str(file + '/' + random.choice(contents)))
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
    newvol = max(0,min(80,vol + value))
    player.audio_set_volume(newvol)
    return

btn_shuffle = Button(17)
btn_vol_up = Button(27)
btn_vol_down = Button(22)

stories_path = '/home/pi/stories/'
vlci = vlc.Instance()
player = vlci.media_player_new()
player.audio_set_volume(40)
current_story = None

manual_pause = False
shuffle_on = False
contents = os.listdir(stories_path)
shuffle_list = contents
random.shuffle(shuffle_list)

btn_shuffle.when_released = shuffle
btn_vol_up.when_released = vol_up
btn_vol_down.when_released = vol_down

rfid = RFID()
no_tag_count = 0
last_pos = -0.5
while True:
    text = None
    pos = abs(player.get_position())
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
                if pos == last_pos and shuffle_on:
                    play_random()
                else:
                    last_pos = pos
                continue
            else:
                print("Stopping playback of " + current_story)
                player.set_media(None)
                current_story = text
                no_tag_count = 0
                play_story(text, player)
                last_pos = pos
                pass
        else:
            current_story = text
            play_story(text, player)
            no_tag_count = 0
    else:
        if shuffle_on:
            print(pos)
            if pos == last_pos:
                print('Shuffling to next story...')
                next_shuffle()
            else:
                last_pos = pos
            continue
        if current_story:
            no_tag_count = no_tag_count + 1
            if no_tag_count > 30:
                print("Stopping playback")
                player.audio_set_mute(1)
                player.set_media(None)
                player.audio_set_mute(0)
                current_story = None
                no_tag_count = 0
                if shuffle_on:
                    play_random()
                continue
            elif no_tag_count > 1:
                if abs(player.get_position()) == 1:
                    print("Tag removed and story finished - Stopping playback")
                    player.set_media(None)
                    current_story = None
                    no_tag_count = 0
                    continue
                else:
                    print("Tag removed - pause (" + str(no_tag_count) + ")")
                    player.set_pause(1)
            continue
