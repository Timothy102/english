import json
import urllib.request

import argparse
from deep_translator import PonsTranslator

english_file = 'new-words.txt'
deutsch_file = '../deutsch/besede.txt'

eInput = "nove.txt"
dInput = "../deutsch/nove.txt"


def performTranslation(word, deutsch = True):
    if deutsch: language = 'german'
    else: language = 'english'
    pons = PonsTranslator(source= language, target='slovenian')
    return pons.translate(word, return_all=True)

def parseArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-de", type=bool, default=False,
                        help="German or English boolean")
    
    args = parser.parse_args()
    return args

def conc(s):
    t = ""
    for k in s: t+= k + ", "
    return t[:len(t)-2]


def get_words(file = eInput):
    l = []
    with open(file, 'r') as f:
        for row in f: l.append(row)
    return l

def langToStr(de = True):
    return 'German' if de else "English"

def request(action, **params):
    return {'action': action, 'params': params, 'version': 6}

def invoke(action, **params):
    requestJson = json.dumps(request(action, **params)).encode('utf-8')
    response = json.load(urllib.request.urlopen(urllib.request.Request('http://localhost:8765', requestJson)))
    if len(response) != 2:
        raise Exception('response has an unexpected number of fields')
    if 'error' not in response:
        raise Exception('response is missing required error field')
    if 'result' not in response:
        raise Exception('response is missing required result field')
    if response['error'] is not None:
        raise Exception(response['error'])
    return response['result']

def main():
    args = parseArguments()
    if args.de: 
        input_file, file = dInput, deutsch_file
        deck_name = "nemščina"
    else: 
        input_file, file = eInput, english_file
        deck_name = "english"

    words = get_words(input_file)
    cc = conc(words).replace('\n', '')
    
    completed = True
    not_translated = []

    for word in words:
        try: 
            translated = conc(performTranslation(word, args.de)[:2])
            with open(file, 'a') as f:
                printed = word.strip() + " -- " + translated.strip() + "\n"
                print(printed)
                f.write(printed)


            note = {
                "deckName" : deck_name,
                "modelName" : "Basic",
                "fields": {
                    "Front" : word.strip(),
                    "Back" : translated.strip()
                }
            }
            invoke('addNote', note = note)
        except: 
            print(f"{word.strip()} could not have been translated into {langToStr(de = args.de)}")
            not_translated.append(word.strip())
            completed = False
            pass

    
    print(f"Completed the following words: {cc} into {langToStr(de = args.de)}")
    print(f"Could not translate the following: {conc(not_translated)}")


if __name__ == "__main__":
    main()