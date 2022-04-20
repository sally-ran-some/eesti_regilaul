from cProfile import run
import nltk
import codecs
import os
from os.path import join 
from estnltk import Text
from estnltk.default_resolver import DEFAULT_RESOLVER
import string
from estnltk.default_resolver import make_resolver
from estnltk.vabamorf.morf import syllabify_words
import csv

song_files = "/Users/sarah/qp_final/lyrics/"
syllout = "/Users/sarah/qp_final/today/"


resolver = make_resolver(
                 disambiguate=False,
                 guess=False,
                 propername=False,
                 phonetic=True,
                 compound=True,
                 slang_lex=True)
tokenizer = nltk.RegexpTokenizer(r"\w+")

def songToSyll(song_dir,output):
    for filename in os.listdir(song_dir):
        if '.txt' not in filename: continue
        f = codecs.open(join(song_dir, filename),'r',encoding="utf-8",errors="surrogateescape")
        song_x = f.readlines()
        f.close()
        songDict = {}
        for line in song_x:
            song = Text(line)
            song.tag_layer('words')
            syll = syllabify_words(song.words.text,as_dict=False)
            songDict.update({line : syll})
        w = csv.writer(open(join(output,filename), 'w'))
        for key, value in songDict:
            tmp = nltk.word_tokenize(key)
            tmp = tmp.strip(string.punctuation)
            w.writerows(tmp, value)
            
            

songToSyll(song_files,syllout)
       

