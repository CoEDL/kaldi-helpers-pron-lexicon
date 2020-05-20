# Pronunciation builder for Eng + non-English wordlists

This script builds pronunciation lexicon files from a single wordlist containing English and non-English words. The pronunciation lexicons are intended to be used with the `Kaldi` speech recognition toolkit, via the `kaldi-helpers` wrapper scripts. Pronunciations for English words are obtained from the NLTK CMU Pronouncing Dictionary, and a letter to sound file is used to generate pronunciations for non-English words.

## Requirements

Requires Python 3, NLTK and the NLTK CMUdict corpus. Run the NLTK interactive installer to get the CMUdict corpus. See https://www.nltk.org/data.html

## Preparation

To begin the process, the minimal files required are
- a wordlist text file containing ENG and non-ENG words (one word per line)
- a letter-to-sound file, mapping characters from the non-ENG orthography to pronunciation symbols, e.g.
```
th TH
d D
x K
```

## Running the scripts

1. Add the `wordlist.txt` file and `letter_to_sound.txt` file to the `input` directory.

2. Run the `run_cmu_dict.py` script to identify ENG words using CMUdict. This also builds an ENG pronunciation lexicon and a temporary non-ENG lexicon in the hope that all is good.
```
python3 run_cmu_dict.py
```

3. It is unlikely that the first iteration will be correct though. Review the wordlists that have been generated in the `output` directory.  Identify words in each list that you want to treat differently from the first automatic run and add them to one or the other of the "override files". When you re-run the script, these override files will force specific words into either the ENG or non-ENG lexicons.

4. Look through the ENG wordlist.

  4.1. If you see a word that you would prefer to generate a non-ENG pronunciation for, add this word to either the `exclude.txt` or `ambiguous.txt` file. These two override files are treated the same, there are two options just to help conceptually group the words.

  4.2. Add any acronyms that you want to manually deal with to the `manual.txt` file. Note that these don't get added to either lexicon file. To add pronunciations for these words, add the word and its pronunciation to `manual_map.txt`.

5. Now look in the non-ENG wordlist.

  5.1. For any words that you want to make ENG pronunciations for, add them to the `missed.txt` file. Also add the word and its pronunciation to `missed_map.txt`

6. Re-run the script. Again, review the ENG and non-ENG wordlists and update the override files as required. Repeat as necessary until you are satisfied with the allocation of words to either wordlist.

7. Now build the non-ENG lexicon from the temp lexicon by running the following command. This script will split the words in the wordlist and replace each character with the corresponding pronunciation symbol from the `letter_to_sound.txt` file.  
```
python3 run_prn_dict.py
```

8. After running the script, manually merge the two lexicon files and use them in your language tool of choice.


## Input file details

`ambiguous.txt`
- This file contains words that could be either ENG or non-ENG
- These words will be included in the temporary non-ENG lexicon

`exclude.txt`
- For words that have been wrongly identified by CMU as ENG, but are actually non-ENG
- These words will be included in the temporary non-ENG lexicon

`manual.txt`
- Words we know will have to be manually done (acronyms etc)
- These will be written into the temp non-ENG lexicon

`manual_map.txt` (optional)
- Manually written pron rules for the words in manual.txt
- These are not written to the temp non-ENG lexicon, but are written into the final non-ENG lexicon by `make_prn_dict.py`

`missed.txt`
- Eng words that CMU missed
- Add them to ENG lexicon for manual mapping

`missed_map.txt` (optional)
- Manually written pron rules for the words in missed.txt
- These will be written into the EN lexicon if a missed_map isn't supplied.

`wordlist.txt`
- The corpus text file generated by `kaldi-helpers`

`letter_to_sound.txt`
- The l2s map


## Output file details

`lexicon_en.txt`
- English pronunciation lexicon, generated by `run_cmu_dict.py`

`lexicon_non_eng_tmp.txt`
- Temp word list, generated by `run_cmu_dict.py`
- Read by `run_prn_dict.py` then removed when done

`lexicon_non_eng.txt`
- Non-english pronunciation lexicon, generated by `run_prn_dict.py`

`words_en.txt`
- Wordlist of ENG words, generated by `run_cmu_dict.py`

`words_non_eng.txt`
- Wordlist of non-ENG words, generated by `run_cmu_dict.py`
