import nltk
import codecs
import os
from os.path import join 
from estnltk import Text
from estnltk.default_resolver import DEFAULT_RESOLVER

from estnltk.default_resolver import make_resolver
from estnltk.vabamorf.morf import syllabify_words
import csv

song_files = "/Users/sarah/Git/eesti_regilaul_corpus/audio/ictus_tier/nlp/lyrics/"
syllout = "/Users/sarah/Git/eesti_regilaul_corpus/audio/ictus_tier/nlp/today/"

resolver = make_resolver(
                 disambiguate=False,
                 guess=False,
                 propername=False,
                 phonetic=True,
                 compound=True,
                 slang_lex=True)
tokenizer = nltk.RegexpTokenizer(r"\w+")

# def songToSyll(song_dir,output):
for filename in os.listdir(song_files):
    name = filename.strip('.txt')
    f = codecs.open(join(song_files, filename),'r',encoding="utf-8",errors="surrogateescape")
    song_x = f.readlines()
    songDict = {}
    for line in song_x:
        song = Text(line)
        song.tag_layer('words')
        syll = syllabify_words(song.words.text,as_dict=False)
        songDict.update({line : syll})
    print(songDict)
    


        #song.tag_layer(resolver=resolver)['morph_analysis']
        #song.tag_layer('sentences')
    #s = csv.writer(open(join(output,name+'_sil.csv'),"w"))
    # song.morph_analysis
        # song_syll = {}
        # for line in song_x:
        #     wordlist = []
        #     for word in line: 
        #         tmp = Text(word)
                
        #         tmp.tag_layer(resolver=resolver)['morph_analysis']
        #         wordlist.append(syllabify_words(tmp.words.text,as_dict=True))
        #     song_syll.update([(line,wordlist)])
        # open file for writing, "w" is writing
       # w = csv.writer(open(join(output,name+"_sillies.csv"), "w"))
        # loop over dictionary keys and values
      

#songToSyll(song_files,syllout)
