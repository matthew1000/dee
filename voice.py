#
# A library for speaking, using the pre-recorded Polly phrases.
#
import os, json, re, random
from playsound import playsound
phrase_json_file=json.loads(open("data/phrases.json").read())

def say_phrase(phrase):
    options = phrase_json_file[phrase]
    if not options or len(options) == 0:
        play_missing(phrase)
    else:
        say(random.choice(options))

def say(msg):
    filename = message_to_filename(msg)

    if os.path.isfile(filename):
        print "[" + msg + "]"
        playsound(filename)
    else:
        play_missing(msg)

def play_missing(msg):
    print "[" + msg + "] - NO RECORDING!"
    missing_file = 'phrases/missing_speech.mp3'
    print "Now playing " + missing_file
    try:
        playsound(missing_file)
    except Exception as e:
        print "Cannot play missing message: " + str(e)

def message_to_filename(s):
    return 'phrases/' + re.sub('\s+', '_', re.sub('[^A-Za-z0-9_\s]', '', s)) + '.mp3'

def load_phrases():
    return phrase_json_file
