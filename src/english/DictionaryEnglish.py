import os


# Simple function to add an element to the dictionary
def add_element(dictionary, key, value):
    if key not in dictionary:
        dictionary[key] = []
    dictionary[key].append(value)


def load_dictionary():
    # Declare a list and a dictionary
    this_dict = {}
    lines = []

    # Read the dictionary text file and write it into list, also, get rid of unnecessary lines
    with open(os.path.abspath("../temp/EnglishWords.txt"), encoding='utf8') as _:
        for line in _:
            line = line.strip()
            if line:
                lines.append(line)

    # Split every line in the list in order to extract the title and the definition of each word
    for line in lines:

        line = line.split(" - ", 1)
        title = line[0]

        if len(line) > 1:  # Some words don't have definitions
            definition = line[1]
            add_element(this_dict, title, definition)

    return this_dict


dictionary = load_dictionary()
