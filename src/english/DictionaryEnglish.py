import os


# Simple function to add an element to the dictionary
def add_element(dictionary, key, value):
    if key not in dictionary:
        dictionary[key] = []
    dictionary[key].append(value)


def get_synonyms(text: str):
    synonyms = text.split(" + ")
    word = synonyms[0]

    for i, synonym in enumerate(synonyms):
        synonyms[i] = synonym.replace(" ", "")

    return word, synonyms


def load_dictionary():
    # Declare a list and a dictionary
    this_dict = {}
    lines = []

    file_directory = os.path.dirname(__file__)
    word_directory = os.path.join(file_directory, '../../text_files/EnglishWords.txt')

    # Read the dictionary text file and write it into list, also, get rid of unnecessary lines
    with open(word_directory, encoding='utf8') as _:
        for line in _:
            line = line.strip()
            if line:
                lines.append(line)

    # Split every line in the list in order to extract the title and the definition of each word
    for line in lines:

        line = line.split(" - ", 1)
        word, synonyms = get_synonyms(line[0])

        if len(line) > 1:  # Some words may not have definitions
            definition = line[1]
            add_element(this_dict, word, definition)
            add_element(this_dict, word, synonyms)

    # Dictionary structure: {word: definition, synonyms}
    return this_dict


if __name__ == "__main__":
    test_dict = load_dictionary()
    print(test_dict)
