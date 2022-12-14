#create a streamlit app
import streamlit as st
#also gets rid of pandas future warning
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
#FILES TO IMPORT
import pandas as pd #pip install pandas
from googletrans import Translator #pip install googletrans==4.0.0rc1
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer #pip install vaderSentiment
import nltk #pip install nltk
from nltk.corpus import stopwords #pip install nltk corpus
nltk.download('stopwords')
#TODO: INSTALL OPENPYXL: to open excel files
#pip install openpyxl
#these come with python so don't need to install
import os 
import sys
import csv
import time
import string
from collections import Counter
import base64
#set up the translator
translator = Translator()

def analysis(file):
    
    df = pd.read_excel(file, header=0, names=['User', 'Comment'])
        #for every row in the dataframe
        #add a new column called Translation
    # create a progress bar that goes through the length of the file
    my_bar = st.progress(0)
    
    df['Translation'] = ""
    df['compound'] = ""

    for index, row in df.iterrows():
        #if the name is not empty and the comment is not empty increase the counter by 1
        if row['User'] and row['Comment']:
            #translate the comment from indonesian to english
            comment = str(row['Comment'])
            try:
                if comment != "\n":
                    try:
                        language = translator.detect(comment).lang
                        if type(language) == list:
                            language = language[0]
                        translated = translator.translate(text = comment, src = language, dest = "en").text
                        
                    except Exception as e:
                        print(e)
                        print(language)
                        try:
                            if type(language) == list:
                                language = language[0]
                            translated = translator.translate(text = comment, src = "id", dest = "en").text
                        except Exception as e:
                            translated = comment
                #send to most_common_words(str, filename) to get the most common words for postive, negative, and neutral campagins
            except Exception as e: #sometimes you have to try again to make it work
                print(e)
                #wait 5 seconds
                time.sleep(5)
                #translate the comment from indonesian to english
                try:
                    language = translator.detect(comment).lang
                    if type(language) == list:
                        language = language[0]
                    translated = translator.translate(text = comment, src = language, dest = "en").text
                except Exception as e:
                    print(e)
                    print(language)
                    try:
                        translated = translator.translate(text = comment, src = "id", dest = "en").text
                    except Exception as e:
                        translated = comment
            
            #add the translated comment to the dataframe
            df.at[index, 'Translation'] = translated
            #update the progress bar
            analyzer = SentimentIntensityAnalyzer()
            #get the sentiment score
            score = analyzer.polarity_scores(translated)
            #add the sentiment score to the dataframe
            df.at[index, 'compound'] = score['compound']

        
        my_bar.progress(index/len(df))
    df['sentiment'] = ['positive' if c > 0.05 else 'negative' if c < -.05 else 'neutral' for c in df['compound']]
    # remove the first column
    df = df.drop(df.columns[0], axis=1)
    return df
# Create a title and sub-title
st.image("YIGH-Blue.png")
st.title("Campaign Analysis Tool")
st.subheader("This tool will help you analyze your campaign performance")
st.write("Just upload your excel file below with the following columns: 'User' , 'Comment'")

# Create a place to upload a file
uploaded_file = st.file_uploader("Choose a file")

#once it is uploaded, read it into a dataframe
if uploaded_file is not None:
    if uploaded_file.name.endswith('.xlsx'):
        df = analysis(uploaded_file)
        #display the dataframe
        st.subheader("Here is your data")
        # Display the dataframe
        st.write(df)
        # MAKE A PLACE TO DOWNLOAD THE DATAFRAME NAMED after the file
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "Press to Download",
            csv,
            "file.csv",
            "text/csv",
            key='download-csv'
            )
        # st.markdown(get_table_download_link(df), unsafe_allow_html=True)

        st.subheader("Here are some key insights from your campaign:")
        average = df['compound'].mean()
        #get the number of comments
        number = df['compound'].count()
        #get the percentage of positive comments
        positive = df[df['sentiment'] == 'positive']['sentiment'].count() / number
        #get the percentage of negative comments
        negative = df[df['sentiment'] == 'negative']['sentiment'].count() / number
        #get the percentage of neutral comments
        neutral = df[df['sentiment'] == 'neutral']['sentiment'].count() / number

        #write all of these
        st.write("The average sentiment score for your campaign is: ", average)
        st.write("The number of comments for your campaign is: ", number)
        st.write("The percentage of positive comments for your campaign is: ", positive)
        st.write("The percentage of negative comments for your campaign is: ", negative)
        st.write("The percentage of neutral comments for your campaign is: ", neutral)

        my_stopwords = ["...", "€", "..", "."]
        #find the 5 most common words
        dict = {}
        words = df['Translation'].str.cat(sep=' ')
        words = words.split()
        words = [word.lower() for word in words]
        words = [word for word in words if word not in stopwords.words('english')]
        words = [word for word in words if word not in string.punctuation]
        dict = {}
        for word in words:
            if word not in my_stopwords:
                if word in dict:
                    dict[word] += 1
                else:
                    dict[word] = 1

        most_common = Counter(dict).most_common(5)
        st.write("Most common words: {}\n".format(most_common))

        most_common_just_words = []
        for word in most_common:
            most_common_just_words.append(word[0])
        #find the 5 most common words for positive comments
        poswords = df[df['sentiment'] == 'positive']['Translation'].str.cat(sep=' ')
        poswords = poswords.split()
        poswords = [word.lower() for word in poswords]
        poswords = [word for word in poswords if word not in stopwords.words('english')]
        poswords = [word for word in poswords if word not in string.punctuation]
        posdict = {}
        for word in poswords:
            if word not in my_stopwords:
                if word not in most_common_just_words:
                    if word in posdict:
                        posdict[word] += 1
                    else:
                        posdict[word] = 1

        #write the 5 most common words for positive comments to analysis.txt

        st.write("Most common words for positive comments: {}\n".format(Counter(posdict).most_common(5)))


        #find the 5 most common words for negative comments
        negwords = df[df['sentiment'] == 'negative']['Translation'].str.cat(sep=' ')
        negwords = negwords.split()
        negwords = [word.lower() for word in negwords]
        negwords = [word for word in negwords if word not in stopwords.words('english')]
        negwords = [word for word in negwords if word not in string.punctuation]
        negdict = {}
        for word in negwords:

            if word not in my_stopwords:
                if word not in most_common_just_words:
                    if word in negdict:
                        negdict[word] += 1
                    else:
                        negdict[word] = 1

        #write the 5 most common words for negative comments to analysis.txt

        st.write("Most common words for negative comments: {}\n\n".format(Counter(negdict).most_common(5)))
    else:
        st.warning("Please upload an excel file")


    

