# /usr/bin/python3

# Copyright: University of Queensland, 2018
# Contributors: Ben Foley

# This script prepares pronunciation lexicons for a multiple-language wordlist

import nltk
import re
import os

corpus_cmu = nltk.corpus.cmudict.dict()

en_words_list = []
non_en_words_list = []

INPUT_DIR = "input"
AMBIGUOUS = "ambiguous.txt"
EXCLUDE = "exclude.txt"
MANUAL = "manual.txt"
MANUAL_MAP = "manual_map.txt"
MISSED = "missed.txt"
MISSED_MAP = "missed_map.txt"
WORDLIST = "wordlist.txt"

OUTPUT_DIR = "output"
LEXICON_EN = "lexicon_en.txt"
LEXICON_NON_ENG = "lexicon_non_eng_tmp.txt"
WORDS_EN = "words_en.txt"
WORDS_NON_ENG = "words_non_eng.txt"

AMBIGUOUS_MSG = AMBIGUOUS + " - supplied ambiguous words"
EXCLUDE_MSG = EXCLUDE + " - supplied words excluded from CMU"
MANUAL_MSG = MANUAL + " - supplied words to check manually (acronyms etc)"
MISSED_MSG = MISSED + " - supplied words missed by CMU, do these manually"
MISSED_MAP_MSG = MISSED_MAP + " - supplied map of words missed by CMU"
EN_WORDS_MSG = "CMU found these ENG words"
NON_EN_WORDS_MSG = "CMU did not see these words"

ambiguous_list = []
exclude_list = []
manual_list = []
missed_list = []
missed_map_list = []


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


def get_duplicate_lines():
    filename1 = os.path.join(OUTPUT_DIR, WORDS_EN)
    filename2 = os.path.join(OUTPUT_DIR, WORDS_NON_ENG)

    with open(filename1) as f1, open(filename2) as f2:
        for line in set(line.strip() for line in f1).intersection(line.strip() for line in f2):
            if line:
                print(line)


def get_missing_lines():
    filename1 = os.path.join(INPUT_DIR, WORDLIST)
    filename2 = os.path.join(OUTPUT_DIR, WORDS_EN)
    filename3 = os.path.join(OUTPUT_DIR, WORDS_NON_ENG)

    with open(filename1) as f:
        wordlist = set(line for line in nonblank_lines(f))

    with open(filename2) as f:
        words_en = set(line for line in nonblank_lines(f))

    with open(filename3) as f:
        words_non_eng = set(line for line in nonblank_lines(f))

    set_a = wordlist - (words_en | words_non_eng)
    if len(set_a):
        print("These words are in the input wordlist but missing from the generated files.")
        for n in set_a:
            print(n)

    set_b = (words_en | words_non_eng) - wordlist
    if len(set_b):
        print("OMG, somehow we have added words that aren't in the input wordlist.")
        for n in set_b:
            print(n)


def write_data_to_file(data, comment):
    f.write("\n# %s \n\n" % comment)
    for line in data:
        f.write(line + "\n")


# - - - - - - - - - - - - - - - -  Prep


print("Cleaning output dir")

for parent, dirnames, filenames in os.walk(OUTPUT_DIR):
    for fn in filenames:
        if fn.lower().endswith('.txt'):
            os.remove(os.path.join(parent, fn))


# - - - - - - - - - - - - - - - -  Input


print("Reading input files")

# This is a list of words that can be English or non-ENG
if os.path.exists(os.path.join(INPUT_DIR, AMBIGUOUS)):
    with open(os.path.join(INPUT_DIR, AMBIGUOUS)) as f:
        ambiguous_list = [line for line in nonblank_lines(f)]
        ambiguous_list.sort()
else:
    print("no ambiguous file supplied")

# This is a list of non-ENG words that NLTK thought were English
if os.path.exists(os.path.join(INPUT_DIR, EXCLUDE)):
    with open(os.path.join(INPUT_DIR, EXCLUDE)) as f:
        exclude_list = [line for line in nonblank_lines(f)]
        exclude_list.sort()
else:
    print("no exclude file supplied")

# This is a list of words that will need manual prons made
if os.path.exists(os.path.join(INPUT_DIR, MANUAL)):
    with open(os.path.join(INPUT_DIR, MANUAL)) as f:
        manual_list = [line for line in nonblank_lines(f)]
        manual_list.sort()
else:
    print("no manual file supplied")

# This is a list of Eng words we know that NLTK missed. We'll do them manually too
if os.path.exists(os.path.join(INPUT_DIR, MISSED)):
    with open(os.path.join(INPUT_DIR, MISSED)) as f:
        missed_list = [line for line in nonblank_lines(f)]
        missed_list.sort()

    if os.path.exists(os.path.join(INPUT_DIR, MISSED_MAP)):
        # If we supply a map of the missed files, we can build it straight into the lexicon
        with open(os.path.join(INPUT_DIR, MISSED_MAP)) as f_missed_map:
            missed_map_list = [line for line in nonblank_lines(f_missed_map)]
    else:
        print("no missed-map file supplied")
else:
    print("no missed file supplied")


# Read in the corpus
with open(os.path.join(INPUT_DIR, WORDLIST)) as f:
    # Strip blank lines (wordlist from the pipeline has double newlines)
    filtered = filter(lambda x: not re.match(r'^\s*$', x), f)
    # Clean the line ending
    wordlist_dirty = [line for line in nonblank_lines(filtered)]

    # Strip ambiguous words, exlusion words that we know are non-ENG,
    # and words we know we need to do manually
    wordlist = list(set(wordlist_dirty) - set(ambiguous_list) - set(exclude_list) - set(manual_list) - set(missed_list))
    wordlist.sort()


# Look for a word in CMU, get its ENG pronunciation
print("Checking CMU")
for line in wordlist:
    if line in corpus_cmu:
        ph = corpus_cmu[line][0]
        ph = [re.sub("\d", "", w) for w in ph]
        ph.insert(0, line)
        en_words_list.append(ph)
    else:
        # Not found, add it to non-ENG list for later l2s generation
        non_en_words_list.append(line)


# - - - - - - - - - - - - - - - -  Output


print("Writing lexicon files")


with open(os.path.join(OUTPUT_DIR, LEXICON_EN), "w") as f:

    # Write missed words
    if os.path.exists(os.path.join(INPUT_DIR, MISSED_MAP)):
        # If we have supplied map file, use words and pron from it
        write_data_to_file(missed_map_list, MISSED_MAP_MSG)
    else:
        # Otherwise, write the plain missed words file
        write_data_to_file(missed_list, MISSED_MSG)

    # Write the CMU data
    f.write("\n# CMU ENG words found \n\n")
    for line in en_words_list:
        # Join word and pron into one line
        f.write(" ".join(line) + "\n")


with open(os.path.join(OUTPUT_DIR, LEXICON_NON_ENG), "w") as f:

    # if we have the manual map, don't write the manual words here,
    # run_prn_dict.py script will append the manual map
    # after building prons for the rest of non-ENG words
    if not os.path.exists(os.path.join(INPUT_DIR, MANUAL_MAP)):
        write_data_to_file(manual_list, MANUAL_MSG)

    write_data_to_file(ambiguous_list, AMBIGUOUS_MSG)
    write_data_to_file(exclude_list, EXCLUDE_MSG)
    write_data_to_file(non_en_words_list, NON_EN_WORDS_MSG)


print("Writing wordlists")


with open(os.path.join(OUTPUT_DIR, WORDS_EN), "w") as f:

    write_data_to_file(missed_list, MISSED_MSG)

    f.write("\n# %s \n\n" % EN_WORDS_MSG)
    for line in en_words_list:
        f.write(line[0] + "\n")


with open(os.path.join(OUTPUT_DIR, WORDS_NON_ENG), "w") as f:

    write_data_to_file(ambiguous_list, AMBIGUOUS_MSG)
    write_data_to_file(exclude_list, EXCLUDE_MSG)
    write_data_to_file(manual_list, MANUAL_MSG)
    write_data_to_file(non_en_words_list, NON_EN_WORDS_MSG)


# - - - - - - - - - - - - - - - -  Verification


print("Verifying")

# read input wordlist, count the number of lines
# read output wordlist, likewise
# compare counts to see if we have duplicated or missed words

wordlist_count = get_line_count(os.path.join(INPUT_DIR, WORDLIST))
lexicon_en_count = get_line_count(os.path.join(OUTPUT_DIR, LEXICON_EN))
lexicon_non_eng_count = get_line_count(os.path.join(OUTPUT_DIR, LEXICON_NON_ENG))
words_en_count = get_line_count(os.path.join(OUTPUT_DIR, WORDS_EN))
words_non_eng_count = get_line_count(os.path.join(OUTPUT_DIR, WORDS_NON_ENG))

print("%d, %d words in generated ENG wordlist and lexicon" % (words_en_count, lexicon_en_count))
print("%d, %d words in generated non-ENG wordlist and temp lexicon" %
      (words_non_eng_count, lexicon_non_eng_count))
if words_non_eng_count - lexicon_non_eng_count:
    print("A difference here may be because missed map entries will be added by run_prn_dict.py")

print("%d total generated words (ENG + non-ENG)" %
      (words_en_count + words_non_eng_count))
print("%d words in input wordlist" % wordlist_count)

if ((words_en_count + words_non_eng_count) - wordlist_count) == 0:
    print("OK, wordlist counts match")
else:
    print("Eek! Wordlist counts differ by %d" %
          ((words_en_count + words_non_eng_count) - wordlist_count))
    print("Checking for duplicates")
    get_duplicate_lines()
    print("Checking for missing words")
    get_missing_lines()


print(". . . .")
print("Done")
print("You now need to build the non-ENG lexicon")

if os.path.exists(os.path.join(INPUT_DIR, MISSED_MAP)):
    print("Missing ENG word map was supplied, it has been included in %s " % LEXICON_EN)
else:
    print("Missing ENG word map was NOT supplied, do it manually in %s" % LEXICON_EN)

if os.path.exists(os.path.join(INPUT_DIR, MANUAL_MAP)):
    print("Manual non-ENG word map was supplied, it is not in the %s, but will be included in the lexicon when you run run_prn_dict.py script" % LEXICON_NON_ENG)
else:
    print("Manual non-ENG word map was NOT supplied, %s will include words to manually check after running the run_prn_dict.py script" % LEXICON_NON_ENG)

