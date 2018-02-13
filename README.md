# dee

Meet Dee, the *DeepLens Educating Entertainer*.

Dee is a prototype for how image recognition can be used to make educational tools.
It's designed to work with young or less-abled children who may struggle to interact
with computers using voice or keyboard/touchscreen.

## What does it do?

Dee asks the user questions, by speaking. The user answers the question by showing
the relevant picture.

This version works eight pictures - four animals (bird, cow, horse and sheep) and four forms of transport (aeroplane, bicycle, bus and motorbike). The easiest thing to do is print the attached PDF from which you can make eight cards to show.

## What you need

* An AWS [DeepLens](https://aws.amazon.com/deeplens/)
* A speaker to attach to the DeepLens
* A printout of [cards.pdf](../blob/master/cards.pdf)

## What model does it use?

This uses the standard 'deeplens-object-detection' model.
