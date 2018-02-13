#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This downloads all the required phrases from Polly.
# The phrases are included in the GitHub repo, so you only need to run this
# if you change the questions, or want to change the choice of Polly voice.
#

import sys
sys.path.insert(0,'..')
import os, boto3, re, json, voice, questions
from playsound import playsound

defaultRegion = 'us-east-1'
defaultUrl = 'https://polly.us-east-1.amazonaws.com'

def loadQuestions():
    json_data=open("data/questions.json").read()
    questionObjects = json.loads(json_data)
    questions = {}
    for q in questionObjects:
        questions[q["q"]] = True
        for answer, answerStatement in q["a"].iteritems():
            questions[answerStatement] = True

        for incorrectAnswer, answerStatement in q["incorrect"].iteritems():
            questions[answerStatement] = True

    return questions

def connectToPolly(regionName=defaultRegion, endpointUrl=defaultUrl):
    return boto3.client('polly', region_name=regionName, endpoint_url=endpointUrl)

def speak(polly, filename,  text):
    voice="Emma"
    resp = polly.synthesize_speech(OutputFormat='mp3', Text=text, VoiceId=voice)
    soundfile = open(filename, 'w')
    soundBytes = resp['AudioStream'].read()
    soundfile.write(soundBytes)
    soundfile.close()
    # playsound(filename)

def doObjects():
    objects = questions.get_all_answers()

    for statement in objects:
        if statement[0] in ['a', 'e', 'i', 'o', 'u']:
            fullStatement = 'an ' + statement
        else:
            fullStatement = 'a ' + statement
        download_statement(statement, fullStatement)

def doPhrases():
    phrases = voice.load_phrases()
    for key, listOfPhrases in phrases.iteritems():
        for phrase in listOfPhrases:
            download_statement(phrase, phrase)

def doQuestions():
    questions = loadQuestions()
    for q, v in questions.iteritems():
        download_statement(q, q)

def download_statement(statementName, statement):
    filename = voice.message_to_filename(statementName)
    if not os.path.isfile(filename):
        print '[' + filename + '] '
        speak(polly, filename, statement)

polly = connectToPolly()
doObjects()
doPhrases()
doQuestions()
