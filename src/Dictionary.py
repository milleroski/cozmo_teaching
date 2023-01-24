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

    # TODO: Maybe allow users to add their own vocabulary list?
    # with open('Combined.txt', 'r') as _:
    #     for line in _:
    #         line = line.strip()
    #         if line:
    #             lines.append(line)

    with open('../text_files/EnglishWords.txt', encoding='utf8') as _:
        for line in _:
            line = line.strip()
            if line:
                lines.append(line)

    # Split every line in the list in order to extract the title and the definition of each word
    for line in lines:

        line = line.split(" - ", 1)
        title = line[0]
        # line = line.split(") ", 1)
        # title = line[0]
        # title = title.split(" (")[0]

        if len(line) > 1:  # Some words don't have definitions
            definition = line[1]
            add_element(this_dict, title, definition)
        # Should I ignore the empty titles?

    return this_dict
    # counter = 0
    # Print every key:value pair in the dictionary
    # for title, definition in this_dict.items():
    #     counter = counter + 1
    #     print("{}:{}".format(title, definition))
    #
    # print("")
    # print(this_dict.get("Apple")[0])
    # print(counter)


dictionary = load_dictionary()


# print(len(dictionary))
# dictKeys = list(dictionary.keys())
#
# for x in range(len(dictKeys)):
#     print(dictKeys[x])

# counter = 0
# while True:
#     print(dictionary.get(dictKeys[counter])[0])
#     counter += 1
# counter = 0
# for title, definition in dictionary.items():
#         counter = counter + 1
#         print("{}:{}".format(title, definition))
