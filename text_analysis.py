# venv---------------------------------- source ~/Desktop/text_analysis/bin/activate
# create scrapy project------------------ scrapy startproject article_extractor
# project ------------------------------ ~/Desktop/text_analysis/text_analysis/article_extractor/article_extractor
# run project scrapy crawl article  -o output.json --logfile=log.txt

import scrapy
import os
import pandas as pd
import codecs
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import string
import time
import gc



class ArticleSpider(scrapy.Spider):
    name = 'article'
    
    positive_score=0

    def start_requests(self):
        y_requests=[]

        #Deleting existing excel file
        if os.path.exists('output.xlsx'):
            os.remove('output.xlsx')

        # Load URLs from the Excel file
        excel_file = 'Input.xlsx'  # Update with your Excel file path
        df = pd.read_excel(excel_file)
        

        for index, row in df.iterrows():

            url_id = str(row['URL_ID'])  # Assuming 'URL_ID' is the column name for URL IDs
            u = row['URL']  # Assuming 'URL' is the column name for URLs

            y_requests.append(scrapy.Request(url=u, callback=self.parse, meta={'url_id': url_id,'url':u}))

            

        return y_requests
            
            
            
        
    
    def read_stop_words_type(self,file_path):
        stop_words = []
        with codecs.open(file_path, 'r', encoding='latin-1') as file:
            for line in file:
                word = line.strip(' ').split()[0]  # Get the first word from each line
                stop_words.append(word)
        
                
            
        return stop_words

    
    def get_all_stop_words(self):
        stop_words = []
        file_prefix=".//StopWords//"
        files=['StopWords_Auditor.txt',
               'StopWords_Currencies.txt',
               'StopWords_DatesandNumbers.txt',
               'StopWords_Generic.txt',
               'StopWords_GenericLong.txt',
               'StopWords_Geographic.txt',
               'StopWords_Names.txt']
        
        for file in files:
            file_path = file_prefix + file  
            stop_words = self.read_stop_words_type(file_path)     
        return stop_words

    def remove_stopwords(self,text, custom_stopwords=[]):
        stop_words=[]
    # Add custom stop words to the set
        stop_words=custom_stopwords
    # Tokenize the text
        words = nltk.word_tokenize(text)
    # Remove stop words
        y=[x.lower() for x in stop_words]
        filtered_words = [word for word in words if word.lower() not in y]
    # Join the words back into a string
        filtered_text = ' '.join(filtered_words)
        return filtered_text
    

    def word_count(self,text):
        # Tokenize the text into words
        words = word_tokenize(text)
        # Remove punctuation marks from each word
        words = [word.translate(str.maketrans('', '', string.punctuation)) for word in words]
        # Remove stop words
        stop_words = set(stopwords.words('english'))
        words = [word for word in words if word.lower() not in stop_words]
        # Count the remaining words
        word_count = len(words)

        return words,word_count
    

    def count_syllables(self,word):
        vowels = 'aeiou'
        count = 0
        endings_to_ignore = ['es', 'ed']

        # Count the number of vowels in the word
        for i in range(len(word)):
            if word[i] in vowels:
                count += 1
                # Handle exceptions for certain endings
                if i < len(word) - 1 and word[i:i+2] in endings_to_ignore:
                    count -= 1
        # Ensure that at least one syllable is counted
        if count == 0:
            count = 1
        return count
    
    def count_personal_pronouns(self,text):
        # Define the regex pattern to match the personal pronouns
        pronoun_pattern = r'\b(I|we|my|ours|us)\b'
        # Compile the regex pattern
        regex = re.compile(pronoun_pattern, flags=re.IGNORECASE)
        # Find all matches in the text
        matches = regex.findall(text)
        # Count the number of matches
        count = len(matches)
        return count
    
    def average_word_length(self,text):
        # Tokenize the text into words
        words = text.split()
       # Calculate the total number of characters in all the words
        total_characters = sum(len(word) for word in words)
        # Calculate the total number of words
        total_words = len(words)
        # Calculate the average word length
        if total_words > 0:
            average_length = total_characters / total_words
        else:
            average_length = 0
        return average_length

    def parse(self, response):
        # Extract article title and text
        title = response.css('h1.entry-title::text').get() #TITLE
        paragraphs = response.css('p::text').getall() # PARAGRAPHS
  
        # strong and li
        article_para = '\n'.join(paragraphs)

        # Get URL from URL
        ur = response.meta['url']
        
        # Get URL_ID from URL
        url_id = response.meta['url_id']

        # Create a directory to store extracted text files
        output_dir = 'extracted_articles'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Save extracted text to a file
        output_file = os.path.join(output_dir, f"{url_id}.txt")
        if os.path.exists(output_file):
            os.remove(output_file)
        with open(output_file, 'w', encoding='utf-8') as file:
            if(title):
                file.write(title)
            if(article_para):
                file.write(article_para)
            

        """ !!!  Building stop words !!!"""

        stopwords=self.get_all_stop_words()


        """ !!! Building prerequisite for positive and negative score !!! """

        pos_dict_words=[]
        neg_dict_words=[]
        with codecs.open(".//MasterDictionary//positive-words.txt", 'r', encoding='latin-1') as file:
            for line in file:
                word = line.strip(' ').split()[0]  # Get the first word from each line
                if(word.lower not in stopwords):
                    pos_dict_words.append(word)

        with codecs.open(".//MasterDictionary//negative-words.txt", 'r', encoding='latin-1') as file:
            for line in file:
                word = line.strip(' ').split()[0]  # Get the first word from each line
                if(word.lower not in stopwords):
                    neg_dict_words.append(word)


        '!!! Removing StopWORDS !!!'

        directory='.//extracted_articles'

        with open(os.path.join(directory, f"{url_id}.txt"), 'r') as file:
            file_contents = file.read()
        
        filtered_text= self.remove_stopwords(file_contents,stopwords)
        
        """ Manual filtering"""
        filtered_text= filtered_text.replace('© All Right Reserved , Blackcoffer ( OPC ) Pvt . Ltd','')
        filtered_text= filtered_text.replace('Contact us :','')

        



        """ !!!  positive and negative score, polarity_score, subjectivity_score !!!"""

        positive_score=0
        negative_score=0

        for wr in filtered_text.split(" "):
            if(wr in pos_dict_words):
                positive_score= positive_score +1
            if(wr in neg_dict_words):
                negative_score= negative_score +1

        polarity_score= (positive_score - negative_score)/ ((positive_score + negative_score) + 0.000001)
        subjectivity_score=(positive_score + negative_score)/ ((len(filtered_text.split(" "))) + 0.000001)

        
 

        """ !!! Average Sentence Length = the number of words / the number of sentences 

            Percentage of Complex words = the number of complex words / the number of words  

            Fog Index = 0.4 * (Average Sentence Length + Percentage of Complex words)  !!! """
        
        avg_sen_len = len(filtered_text)/len(filtered_text.split("."))

        words, wc = self.word_count(filtered_text)
        complex_words=0

        for c in words:
            if(len(c)>2):
                complex_words= complex_words +1

        percentage_complex= complex_words/(len(filtered_text.split(" ")))

        fog_index = 0.4 * (avg_sen_len + percentage_complex)



        """  !!!   Average Number of Words Per Sentence = the total number of words / the total number of sentences  !!! """
        avg_word_per_sen = len(filtered_text.split(" "))/len(filtered_text.split("."))
        

        
        

        """ !!!  SYLLABLE PER WORD   !!!"""
        syllables_count=0
        for w in words:
            syllables_count=  syllables_count + self.count_syllables(w)

        

        """ !!!  PERSONAL PRONOUN COUNT   !!!"""
        personal_promoun_count=self.count_personal_pronouns(filtered_text)

        
        """ !!!  AVERAGE WORD LENGTH   !!!"""
        average_word_length=self.average_word_length(filtered_text)

        
        try:
            df_existing = pd.read_excel('output.xlsx')
        except FileNotFoundError:
            df_existing = pd.DataFrame()

        data = {
            "URL_ID": [url_id],
            "URL": [ur],
            "Positive Score": [positive_score],
            "Negative Score": [negative_score],
            "Polarity Score": [polarity_score],
            "Subjectivity Score": [subjectivity_score],
            "Average Sentence Length": [avg_sen_len],
            "Percentage of Complex Words": [percentage_complex],
            "FOG Index": [fog_index],
            "Average Words Per Sentence": [avg_word_per_sen],
            "Complex Words": [complex_words],
            "Word Count": [wc],
            "Syllables Count": [syllables_count],
            "Personal Pronoun Count": [personal_promoun_count],
            "Average Word Length": [average_word_length]
                }
        
        
        try:
            df_existing = pd.read_excel('output.xlsx')
        except FileNotFoundError:
            df_existing = pd.DataFrame()

        # Append the new data as a new row to the DataFrame
        df_new = pd.DataFrame(data, index=[0])

        # Concatenate the existing DataFrame with the new data
        df_concat = pd.concat([df_existing, df_new], axis=0, ignore_index=True)

        #   Write the DataFrame to an Excel file
        df_concat.to_excel('output.xlsx', index=False)

        gc.collect()









