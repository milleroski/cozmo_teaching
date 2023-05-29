# cozmo_teaching
Repository for my Bachelors thesis project using ANKI Cozmo for language learning. 

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
