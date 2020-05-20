#!/usr/bin/python3

# Copyright: University of Queensland, 2018
# Contributors: Ben Foley, Nay San

# This is a file for automatically build the word -> sound dictionary
# input: text file, config file
# output: mapping between unique words and their sound, ordered by their appearance

import argparse
import os

INPUT_DIR = "input"
OUTPUT_DIR = "output"
MANUAL_MAP = "manual_map.txt"
LEXICON_NON_ENG = "lexicon_non_eng.txt"


def nonblank_lines(f):
    lines = (line.rstrip() for line in f)  # All lines including the blank ones
    lines = (line for line in lines if line)  # Non-blank lines

    for l in lines:
        line = l.rstrip()
        if not line.startswith("#"):
            yield line


def get_line_count(file_name):
    with open(file_name) as f:
        list = [line for line in nonblank_lines(f)]
        return len(list)


def generate_dictionary(input_filename, config_filename, output_filename):
    print("Generating dictionary")

    # Read the input file
    input_tokens = []
    with open(input_filename, "r") as input_file:
        for line in input_file.readlines():
            token = line.strip()
            if (len(token) > 0):
                input_tokens.append(token)
        # print(input_tokens)

    # Read the config file
    with open(config_filename, "r") as config_file:
        print("Reading l2s")
        sound_mappings = []

        for line in config_file.readlines():
            if (line[0] == '#'):
                continue

            mapping = list(filter(None, line.strip().split(' ', 1)))

            if (len(mapping) > 1):
                sound_mappings.append((mapping[0], mapping[1]))

        # Sort the sound mappings by length of sound mapping
        sound_mappings.sort(key=lambda x: len(x[0]), reverse=True)

        oov_characters = set([])
        output = []

        print("Processing words")
        for token in input_tokens:
            # print(token)

            # Pass comments through, needs to be a list though so it doesn't get joined later
            if (token[0] == '#'):
                output.append(["\n"])
                output.append([token])
                # output.append(["\n"])
                continue

            cur = 0
            res = [token]
            token_lower = token.lower()

            while (cur < len(token_lower)):
                found = False
                for maps in sound_mappings:
                    if (token_lower.find(maps[0], cur) == cur):
                        found = True
                        res.append(maps[1])
                        cur += len(maps[0])
                        break

                if (not found):
                    # unknown sound
                    res.append('(' + token_lower[cur] + ')')
                    oov_characters.add(token_lower[cur])
                    cur += 1
            # Done mapping, add to output list
            output.append(res)

        print("Writing lexicon")

        if os.path.exists(os.path.join(INPUT_DIR, MANUAL_MAP)):
            # If we supply a map of the missed files, we can build it straight into the lex
            with open(os.path.join(INPUT_DIR, MANUAL_MAP)) as f_manual_map:
                manual_map_list = [line for line in nonblank_lines(f_manual_map)]
        else:
            manual_map_list = []

        with open(output_filename, "w") as output_file:
            # output_file.write('!SIL sil\n')
            # output_file.write('<UNK> spn\n')

            # If we have a manual map file, add that first
            #
            if os.path.exists(os.path.join(INPUT_DIR, MANUAL_MAP)):
                print("Using supplied manual map")
                output_file.write("# using supplied manual map \n\n")
                for line in manual_map_list:
                    output_file.write(line + '\n')
            else:
                print("No manual map supplied, make sure you check the output")

            for line in output:
                output_file.write(' '.join(line) + '\n')

        # for character in oov_characters:
        #     print("Unexpected character: %s" % character)

    os.remove(input_filename)

    lexicon_non_eng_count = get_line_count(os.path.join(OUTPUT_DIR, LEXICON_NON_ENG))
    print("%s words in the non-ENG lexicon" % lexicon_non_eng_count)
    print("Done. You now need to add SIL and UNK.")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--words", help="input file with one word in each line", default='output/lexicon_non_eng_tmp.txt')
    parser.add_argument("--config", help="configuration file with one letter -> sound mapping in each line", default='input/letter_to_sound.txt')
    parser.add_argument("--output_file", help="name of the output file", default='output/lexicon_non_eng.txt')

    args = parser.parse_args()
    generate_dictionary(args.words, args.config, args.output_file)
