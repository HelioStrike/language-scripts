from bs4 import BeautifulSoup
import jieba
import re
import requests

text_to_feed = """
Put your text in here!
Review README.md to ensure your text complies with the expected format.
"""

deck_name = "You Anki flashcard deck name."

# URL prefix for a Mandarin-English dictionary to search for the meaning of a
# certain Mandarin word in English.
MDBG_SEARCH_URL = "https://www.mdbg.net/chinese/dictionary?page=worddict&wdrst=1&wdqb="

# AnkiConnect server url (on your local machine). By default, it is this value.
ANKICONNECT_URL = "http://127.0.0.1:8765"

def main(): 
    mandarin_texts = filter_mandarin_texts(text_to_feed)

    # This method decomposes texts into words.
    # I'm avoiding using this method at the moment because it generates too many
    # words, but I might decide on using it later.
    #
    # mandarin_texts = fetch_words_from_mandarin_texts(text_to_feed)

    if len(mandarin_texts) == 0:
        print("No mandarin text was detected.")
        return

    meanings, pinyins, failed_list = fetch_meanings_and_pinyins_for_mandarin_texts(mandarin_texts)

    if len(failed_list) > 0:
        print("These words need extra care: %s\n" % ", ".join(failed_list))

    if len(meanings) == 0:
        print("No cards to add.")
        return

    while(True):
        print("These words can be fed into anki:\n")
        for index, text in enumerate(meanings):
            print("%i) %s - (%s) %s\n" % (index, text, pinyins[text], meanings[text]))

        print("Enter a number to prevent it from being fed in, or key in 'y' to proceed with the feeding (ON NOM NOM!!!).")
        command = input()

        if command == 'y':
            break
        elif command.isnumeric():
            index_to_remove = int(command)
            if index_to_remove < 0 or index_to_remove >= len(meanings.keys()):
                print("A weird index was provided?")
            else:
                key_to_remove = list(meanings.keys())[index_to_remove]
                meanings.pop(key_to_remove, None)
                pinyins.pop(key_to_remove, None)
        else:
            print("Couldn't make sense of your command.. sorry~")

        print("Maybe you'd like to give it another jab?\n")
        

    print('Feeding %i cards to Anki!' % len(meanings))
    feed_to_anki(meanings, pinyins)
    print('Feeding complete!')

# On passing a text, the function returns a list, containing groups of Mandarin
# alphabet that were found.
def filter_mandarin_texts(text):
    mandarin_texts = []
    for captured in re.findall(r'[\u4e00-\u9fff]+', text):
        mandarin_texts.append(captured)
    return mandarin_texts

# Decomposes texts (list of strings) into individual words.
def fetch_words_from_mandarin_texts(mandarin_texts):
    mandarin_words = []
    for mandarin_text in mandarin_texts:
        seg_list = jieba.cut(mandarin_text, cut_all=False)
        mandarin_words += seg_list
    return mandarin_words

# Takes a list of mandarin texts and returns:
# 1. A dict from the text to their meaning.
# 2. A dict from the text to their pinyin.
# 3. A list of texts for which we weren't able to fetch texts for.
def fetch_meanings_and_pinyins_for_mandarin_texts(mandarin_texts):
    meanings = {}
    pinyins = {}
    failed_list = []
    for mandarin_text in mandarin_texts:
        search_query_url = MDBG_SEARCH_URL + mandarin_text
        response = requests.get(search_query_url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            defs_div = soup.find('div', class_='defs')
            pinyin_div = soup.find('div', class_='pinyin')

            if defs_div and pinyin_div and not "No results found searching for" in soup.get_text():
                pinyin_syllables = pinyin_div.find_all('span')
                complete_pinyin = ''.join(syllable.text.strip() for syllable in pinyin_syllables)

                print("Fetched meaning and pinyin for text: %s" % mandarin_text)
                meanings[mandarin_text] = defs_div.text.strip()
                pinyins[mandarin_text] = complete_pinyin
            else:
                print("Error: Could not find meaning for text: %s" % mandarin_text)
                failed_list.append(mandarin_text)
        else:
            print("Error: Failed to retrieve MDBG website content for text: %s" % mandarin_text)
            failed_list.append(failed_list)

    return meanings, pinyins, failed_list

# Feeds the meaning and pinyin dictionaries to anki connect.
def feed_to_anki(meanings, pinyins):
    for index, mandarin_text in enumerate(meanings):
        response = requests.post(ANKICONNECT_URL, json={
            "action": "addNote",
            "version": 6,
            "params": {
                "note": {
                    "deckName": deck_name,
                    "modelName": "Basic",
                    "fields": {
                        "Front": mandarin_text,
                        "Back": "%s - %s" % (pinyins[mandarin_text], meanings[mandarin_text])
                    },
                }
            }
        })

        if response.status_code == 200:
            response_json = response.json()

            if response_json["error"]:
                print("Failed to upload note for: %s, with error: %s" % (mandarin_text, response.json()["error"]))
            else:
                print("Uploaded note for: %s" % mandarin_text)
        else:
            print("Failed to upload note for: %s. AnkiConnect might not be listening for the connection." % mandarin_text)

if __name__=="__main__": 
    main()
