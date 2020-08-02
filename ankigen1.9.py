#!/bin/env python

"""
Ankigen is quick anki cards generator.

--help - help
no-tr - no translate
ctc= - count of trying to connect
file= - file path

That's it.


"""





import os
import requests
import re
import sys
import readline # Решает проблему с ^[[D & Co

def get_lang(string): 
    for char in string:
        char_ord = ord(char)
        if 1072 <= char_ord <= 1103:
            return 'ru'
        if 97 <= char_ord <= 122:
            return 'en'
    print('Bad string: There is no cyrillic nor latinic chars')
    sys.exit(1)

def get_word_ipa(word):
    ipa_dict = {'' : '', 'as' : 'əz', 'b' : 'bi:', 'i' : 'aɪ', 'B' : 'bi:' }
    try:
        ipa = ipa_dict[word]
    except KeyError:
        is_apostrophe = False
        if word[-2:] == "'s":
            word = word[:-2]
            is_apostrophe = True
        
        for i in range(count_trying_connect): # Rewrite it. It's mess.
            try:
                ipa = requests.get('https://wooordhunt.ru/word/'+word).text
            except Exception:
                if i == count_trying_connect:
                    print('Internet problem')
                    exit(1)
        
        
        
        try:
            ipa = re.findall(r'<span title="американская транскрипция слова .*?" class="transcription"> .*?</span>', ipa)[0]
            ipa = re.findall(r'\|.*?\|', ipa)[0][1:-1]
            if is_apostrophe:
                ipa += 's'
        except IndexError:
            ipa = '???'
    return ipa
    
    
def get_string_ipa(string):
    words = re.split(r'[\s,.\/-?()]', string) # I added braekets here
    for word in words:
        ipa = get_word_ipa(word)
        string = string.replace(word, ipa)
    return string

def unbold(string):
    return string[4:-6]

def get_translate(string, lang_from): 
    if lang_from == 'en':
        raw_translate_list = os.popen('trans en:ru "'+string+'"').readlines()
    else:
        raw_translate_list = os.popen('trans ru:en "'+string+'"').readlines()
    for i in range(len(raw_translate_list)):
        if not(raw_translate_list[i].split()):
            break
    default = raw_translate_list[i+1]
    default = unbold(default).lower()
    raw_translate_list = ['\n'] + raw_translate_list[i+3:] + ['\nProposed translate: ' + default + '\n']
    complete_translate_string = ''
    for string in raw_translate_list:
        complete_translate_string += string
    return (complete_translate_string, default)


# Обработчик параметров
req_transcription = True
count_trying_connect = 3

transcription = ''
ipa_string = ''


i = 1
while True:

    try:
        current_arg = sys.argv[i]
    except IndexError:
        break

    if current_arg == '--help':
        print(sys.modules[__name__].__doc__)
        sys.exit(0)
        
    elif current_arg == 'no-tr':
        req_transcription = False
    
    elif current_arg[:4] == 'ctc=':
        try:
            count_trying_connect = int(current_arg[5:])
        except Exception:
            print('Bad argument: after -ctc= should be number')
            exit(1)
            
    elif current_arg[:5] == 'file=':
        file_path = current_arg[5:]


    i += 1


if not(file_path):
    print('There is no file path')
    exit(1)

try:
    with open(file_path, 'a') as f:
        pass
except Exception:
    print('Bad argument: bad path')
    exit(1)

string = input('String: ')
string.replace('\t','')
string = string.lower()
lang_from = get_lang(string)


if lang_from == 'ru':
    ru_string = string
    output, default =  get_translate(ru_string, lang_from)
    print(output)
    en_string = input('Translate: ').lower()
    if not(en_string):
        en_string = default
    
    if req_transcription:
        ipa_string = get_string_ipa(en_string)
        print('Transcription: '+ipa_string) # Ещё добавить \n для красаты?
    
    en_example = input('English example: ')
    ru_example = input('Russian example: ')
    with open(file_path, 'a') as f: # А если туда нет доступа или ещё чё? Там вроде какие то специальные кода завершения надо. А как с правами доступа работать?
        print(en_string, ipa_string, en_example, ru_string, ru_example, sep='\t', file = f)

elif lang_from == 'en':
    en_string = string
    
    if req_transcription:
        ipa_string = get_string_ipa(en_string)
        print('Transcription: '+ipa_string)
    
    output, default =  get_translate(en_string, lang_from)
    print(output)
    ru_string = input('Translate: ') # Добавить \n?
    if not(ru_string):
        ru_string = default
    en_example = input('English example: ')
    ru_example = input('Russian example: ')
    with open(file_path, 'a') as f:
        print(en_string, ipa_string, en_example, ru_string, ru_example, sep='\t', file = f)
