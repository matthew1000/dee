#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This has the question and answer logic.
# You can run it on the command line to test the behaviour.
#
import json, sys, random, os, voice, time, calendar, threading
from random import shuffle

questions_json=open("data/questions.json").read()
questions = json.loads(questions_json)
FREQUENCY_TO_REPEAT_QUESTION = 10
TIMES_TO_REPEAT_QUESTION = 2

previous_question = None
current_question = None
question_last_said = None
question_repeat_count = None

question_order = []
def pick_question(previous_question):
    global question_order

    # We make a random order of questions to minimise the repetition:
    if len(question_order) == 0:
        question_order = range(len(questions))
        shuffle(question_order)

    question_number = question_order.pop()
    return questions[question_number]

def say_question():
    global question_last_said
    question_last_said = calendar.timegm(time.gmtime())
    voice.say(current_question["q"])

def consider_repeating_question():
    global question_repeat_count
    if current_question == None:
        return
    if question_repeat_count < TIMES_TO_REPEAT_QUESTION:
        now = calendar.timegm(time.gmtime())
        if now - FREQUENCY_TO_REPEAT_QUESTION > question_last_said:
            question_repeat_count = question_repeat_count + 1
            say_question()

def answer_positively(question, answer):
    voice.say(answer)
    voice.say(question["a"][answer])
    say_do_another()

def answer_negatively(question, answer):
    voice.say(answer)
    if answer in question["incorrect"]:
        voice.say(question["incorrect"][answer])
    else:
        voice.say(question["incorrect"]["default"])

def say_do_another():
    voice.say_phrase('do_another')

def intro():
    voice.say_phrase('intro')
    ask_question()

def mark_answer(answer):
    if answer in current_question["a"]:
        answer_positively(current_question, answer)
        ask_question()
        return True
    else:
        answer_negatively(current_question, answer)
        return False

def get_all_answers():
    global questions
    all_answers = {}
    for q in questions:
        for answer,statement in q["a"].iteritems():
            all_answers[answer] = True

    return all_answers.keys()


def ask_question():
    global current_question, previous_question, question_repeat_count
    previous_question = current_question
    current_question = pick_question(previous_question)
    question_repeat_count = 0
    say_question()

    if __name__ == "__main__":
        while True:
            answer = raw_input("Answer: ")
            was_it_right = mark_answer(answer)
            if was_it_right:
                break

if __name__ == "__main__":
    # intro()
    ask_question()
    # threading.Thread(target=ask_question, args=()).start()
    # while True:
    #     time.sleep(4)
    #     print '...'
    #     consider_repeating_question()
