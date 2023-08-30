# cozmo_teaching
This is a repository for my Bachelors thesis project using ANKI Cozmo for language learning. 

## How to launch
This script runs on Python UP TO PYTHON 3.7.7, IT WILL NOT RUN ON HIGHER PYTHON VERSIONS.    
Go into the main directory of the project (a.k.a. cozmo_teaching)  
Connect your phone through usb and activate adb by typing  
`adb usb` into cmd     
Afterwards run the program as a python module.  
So for example, if you want to run cozmo_main.py, which is in src/english you run  
`python -m src.english.cozmo_main`  
Another example, if you want to run face_detection.py you input which is in src you run  
`python -m src.face_detection`   


## Usage tutorial

Cozmo interacts with you through speech detection.  
If the cube flashes red, it means that you can't tap it and that the speech detection is not ready yet.
Once the cube lights flash green you can tap the cube to switch it's color to blue.
This indicates that the speech detection is listening for your voice.


## Text file editing
This is a tutorial for editing the vocabulary and dialogue exercises.  
All the files you need to edit are in the text_files folder.


### Vocabulary:
Every question is in a single line.
A line requires the following two things -- a word, and a definition. Optionally, you can add synonyms that still
count as the correct answer.

So it follows the following format:  
word1 - definition1  
word2 - definition2

If you want to include alternative answers (synonyms) then you format it like:  
word1 + synonym1 + ... + synonymN - definition1  
word2 + synonym1 + ... + synonymN - definition2

### Dialogue:
Every line is one line that Cozmo will say out loud. After the user is done responding to the previous line, Cozmo says
the next line.

Format:  
line1  
line2  
...  
lineN
