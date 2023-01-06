#!/bin/bash

cd voice_bot 
rasa run -m models --port 5002 &
rasa run actions &
cd ..
python main.py 



