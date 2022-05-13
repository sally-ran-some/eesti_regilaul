# %% [markdown]
# ## Materials 
# At the start, we have audio and annotated textgrids of **regilaul** songs, annotated for ictus/off-ictus and phrase text, then force-aligned using Praat's built in eSpeak forced aligner for Estonian to word and then segment. Then, we use the estnltk vabamorf package to syllabify the words so that we can annotate the textgrid further with syllable quantity (Estonian has 3) and whether or not it is accented at the word level. We end up with a dataframe containing the data from three of the(Interval) tiers of the textgrid, acquiring duration data for words, individual segments, and (eventually) syllables. 

# %%

import parselmouth
from estnltk.vabamorf.morf import syllabify_word
import tgt
import string
#test method on a single TextGrid:
gridDir2 = "/Users/sarah/qp_final/txtgridtest/69.TextGrid"


def get_duration_labels(textgrid, tiername1,tiername2,tiername3):
    tmp = tgt.read_textgrid(textgrid)
    mytier = tmp.get_tier_by_name(tiername1)
    other = tmp.get_tier_by_name(tiername2)
    ictus = tmp.get_tier_by_name(tiername3)
    segments = []
    word_dur = mytier.intervals
    
    for interval in word_dur:
        h = interval.start_time
        t = interval.end_time
        b = t-h 
        l = interval.text
        tmpseg = [other.get_annotations_between_timepoints(h,t)]
        s = syllabify_word(l,as_dict=True)
        i = 0 
        for list in tmpseg:
            n = 0 
            while i < len(s):
                item = s[i]
                shape = item.get('syllable')
                q = item.get('quantity')
                a = item.get('accent')
                geminate = False
                for char in shape.strip(string.punctuation):
                    if geminate: continue
                    if n < len(list): 
                        myinterval = list[n]
                        c = myinterval.text
                        d = myinterval.start_time
                        g = myinterval.end_time
                        tmpick = ictus.get_annotations_between_timepoints(d,g,left_overlap=True,right_overlap=True)
                        if len(tmpick) == 0: ick = "off"
                        else: ick = "ictus"
                        #segment duration
                        j = g-d  
                        #segment midpoint for later measurements
                        mid = g - (j/2)
                        if "ː" in c: 
                            row = [l,b,shape,q,a,c,j,mid,ick]
                            segments.append(row)
                            geminate = True
                            
                        elif char == c: 
                        
                            row = [l,b,shape,q,a,c,j,mid,ick]
                            segments.append(row)
                        else :
                            can = "(" + char + ") " + c
                            row = [l,b,shape,q,a,can,j,mid,ick]
                            segments.append(row)
                        n+=1               
                i+= 1 

            
           


    nu_df = pd.DataFrame(segments,columns=["word","word_dur","syll","quantity","stress","segment","seg_duration","seg_midpoint","ictus"])
    return nu_df

syl_dur_df = get_duration_labels(gridDir2,"word","word/phon","ictus")
syl_dur_df.head()



# %% [markdown]
# ## Adding Spectral data
# now that we have the duration data from the textgrid, we can query specific timepoints for information about the acoustic signal. The following function uses the midpoint (which we snagged while we were making the dataframe above) and get the first three formants(Hz) for each segment. 

# %%

import parselmouth

test = "/Users/sarah/qp_final/wavs/069.wav"

def get_formants(syl_dur_df, wave):
    song = parselmouth.Sound(wave)
    formant = song.to_formant_burg()
    f1 = []
    f2 = []
    f3 = []
    for float in syl_dur_df.seg_midpoint:
        time = float
        f1.append(formant.get_value_at_time(1,time))
        f2.append(formant.get_value_at_time(2, time))
        f3.append(formant.get_value_at_time(3,time))
    syl_dur_df["f1"] = f1
    syl_dur_df["f2"] = f2
    syl_dur_df["f3"] = f3
    return syl_dur_df
nu_df = get_formants(syl_dur_df,test)
nu_df.head()


# %%
from os.path import join
#runs a for loop over a directory using the above-specified functions

test = "/Users/sarah/qp_final/txtgridtest/"
songs = "/Users/sarah/qp_final/songs/"

for fn in os.listdir(test):
    if '.TextGrid' not in fn: 
        continue 
    n = fn.strip('.TextGrid') 
    wave = join(songs, n + '.wav')
    data_file = open("ictus_forms_" + n +".csv",'w')
    #make a dataframe with the interval tiers of the textgrid
    tmp = pd.DataFrame(get_duration_labels(join(test,fn), "word","word/phon","ictus"))
    #add the formant data to the dataframe
    nu_df = get_formants(tmp,wave)
    print(nu_df.head())
    # nu_df.to_csv(data_file)
    # data_file.close()

# %% [markdown]
# # Now we put it into a big pile!
# 
# Here we concatenate all the data we have so far into one large pandas dataframe. At this point, we can keep annotating songs for the corpus, and as textgrids are finished we can run the scripts above to add them into the larger dataset. We're also gonna take the opportunity to add some metadata to the dataframes: fileid(song) and performer initials as potential grouping factors. 

# %%

import os 
import pandas as pd 
import statsmodels .formula.api as smf
folder = "/Users/sarah/qp_final/data_glob/"
meta =  pd.read_csv("/Users/sarah/qp_final/song_metadata.csv")


songs_dfs = []
for fn in os.listdir(folder):
    if '.csv' not in fn: continue
    whole_name = os.path.join(folder,fn)
    song_df = pd.read_csv(whole_name)
    fileid1 = fn.strip('ictus_forms_')
    fileid = int(fileid1.strip('.csv'))
    row = meta.index[meta['track'] == fileid].tolist()
    performer = meta.performer[row[0]]
    for index in song_df:
        song_df['fileid'] = fileid
        song_df['performer'] = performer

        
    songs_dfs.append(song_df)

big_frame = pd.concat(songs_dfs, ignore_index=True)
print(big_frame.describe())
big_frame

# %%
#for the present paper, we are only interested in the vowel durations: 
#set of Estonian vowels to filter the dataframe:
vowels = ["i","ɪ","y","e","ɛ","ø","æ","a","ɑ","ɵ","o","ʊ","u","ʎ" ]
vowel_df = big_frame[big_frame.segment.isin(vowels)].copy()
print(vowel_df.describe())
vowel_df.head()


# %%
#make sure quantity is read as a categorical variable
vowel_df['quantity'] = vowel_df['quantity'].astype('object')
vowel_df['stress'] = vowel_df['stress'].astype('object')
print("vowel duration and stressed/unstressed: \n" , vowel_df.groupby('stress')['seg_duration'].mean())
print("vowel duration and syllable quantity: \n" , vowel_df.groupby('quantity')['seg_duration'].mean())
print("vowel duration and ictus/off-ictus \n" , vowel_df.groupby('ictus')['seg_duration'].mean())

# %%
import pandas as pd 
import statsmodels .formula.api as smf

#is ictus (song prominence) a good predictor for vowel duration?

ickmodel = smf.ols("seg_duration ~ ictus", data=vowel_df).fit()
ickmodel.summary()


# %% [markdown]
# well, the intercept coefficient is significant (p<0.05), so vowels that are in the ictus position are predictably longer than those in the off-ictus or weaker positions in the song. The R squared is still pretty small, though. Let's see the residuals. 

# %%
ickmodel.fittedvalues
resid_series = pd.Series(ickmodel.resid)
print("min: " ,resid_series.min(), "q1: ", resid_series.quantile(0.25), "median: " ,resid_series.median(),"q3: " , resid_series.quantile(0.75),"max: " ,resid_series.max())
pd.Series(ickmodel.resid).plot.density();

# %% [markdown]
# ok, we're nearly normal, if not a bit spikier around the mean than preferable. Still, so far it looks like there is a linear relationship between vowel duration and metrical position in the song. 
# 
# Let's see how quantity is shaking out: 

# %%
qmodel = smf.ols("seg_duration ~ quantity", data=vowel_df).fit()
qmodel.summary()

# %% [markdown]
# Well, we have significant p values for the first (Q1) and third (Q3) coefficients, but not the second (Q2). This makes sense, since the quantity contrast is indicated by the duration ratios of the syllables. Q3, however, never appears in an unstressed position in a word, so only needs to be contrasted with Q2, while Q1 and Q2 both appear in stressed and unstressed positions and need to be differentiated from each other. The adj r-squared here is a little bit better than the ictus model above, and we do have statistical significance for the model overall (p<0.0000)

# %%
qmodel.fittedvalues
qresid_series = pd.Series(qmodel.resid)
print("min: " ,qresid_series.min(), "q1: ", qresid_series.quantile(0.25), "median: " ,qresid_series.median(),"q3: " , qresid_series.quantile(0.75),"max: " ,qresid_series.max())
pd.Series(qmodel.resid).plot.density();

# %%
stressmodel = smf.ols("seg_duration ~ stress", data=vowel_df).fit()
stressmodel.summary()

# %% [markdown]
# here we have significant effects for both coefficients. It looks like word-level stress predicts a shorter vowel duration, with a negative slope. 

# %%
stress_q_model = smf.ols("seg_duration ~ stress + quantity", data=vowel_df).fit()
stress_q_model.summary()

# %% [markdown]
# so far, this is the best model we have as far as adj r-squared goes. It is explaining the most variation so far, and it is unlikely with the low p value that the model is complete trash. We didn't lose significance for any of our coefficients from single factor models. 

# %%
stress_q_model.fittedvalues
stressresid_series = pd.Series(stress_q_model.resid)
print("min: " ,stressresid_series.min(), "q1: ", stressresid_series.quantile(0.25), "median: " ,stressresid_series.median(),"q3: " , stressresid_series.quantile(0.75),"max: " ,stressresid_series.max())
pd.Series(stress_q_model.resid).plot.density();




