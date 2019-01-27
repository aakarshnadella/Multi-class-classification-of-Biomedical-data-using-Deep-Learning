# -*- coding: utf-8 -*-
"""
Created on Sat Jul 14 14:11:29 2018

@author: anadella
"""

import os,glob
import pymysql
import re
import nltk
import Bio
from Bio import Entrez
import pandas as pd
import time
nltk.__version__
from nltk.stem import *
nltk.download()

#************************************
#Collecting abstracts from PubMed

#provide your email-id
Entrez.email = "*********@gmail.com"
#collect required number of PMID's of the aricles by changing retmax value 
esearch_query = Entrez.esearch(db="pubmed", term="Tobacco and Lung Cancer", retmode="text",retmax = 5000)
esearch_result = Entrez.read(esearch_query)
print(len(esearch_result['IdList']))
#create a dataframe to collect the abstracts
Abstractdf = pd.DataFrame(columns = ["Text"])

for identifier in esearch_result['IdList']:
    time.sleep(1) #as pubmed accepts only 3 hits per sec.
    pubmed_entry = Entrez.efetch(db="pubmed", id=identifier, retmode="xml")
    result = Entrez.read(pubmed_entry)
    try:
        article = result['PubmedArticle'][0]['MedlineCitation']['Article']
    except IndexError:
        article = "Null"
    except Exception as error:
        print ("An exception was thrown!")
        print (str(error))
    except:
        pass
    if 'Abstract' in article:
        abstract = article['Abstract']['AbstractText']
        Abstractdf = Abstractdf.append({'Text': i for i in abstract}, ignore_index=True)

print(len(Abstractdf))

#Saving collected abstracts into csv file
Abstractdf.to_csv("AbstractMelanoma.csv", sep=',', encoding='utf-8')

#************************************
#STEP : 1
#Cleaning abstracts and extracting only the sentences with action words

#Function to clean sentences
strip_special_chars = re.compile("[^A-Za-z0-9 ]+")
def cleanSentences(raw_tweets):
    remove_urls = re.sub(r'http\S+','',raw_tweets)
    remove_usernames = re.sub(r'@\w*','',remove_urls)
    string = remove_usernames.lower().replace("<br />", " ")
    string.replace('[^\w\s]','')
    return re.sub(strip_special_chars, "", string.lower()) 

#Dictionary of action words
my_dictionary = ["activates",  "activation","activated", "induced", "activator","inhibits", "inhibited", "inhibiting", "inhibition", "inhibitor","phosphorylates","binds","binding","attenuated","catalyst","catalyses","hydrolysis","hydrolyzes","cleaves","adhesion","donates","regulates","regulated", "regulate", "regulating", "induce", "induces", "induced", "creates","becomes","transports","exports","releases","suppresses", "suppressed", "suppressors","upregulate","upregulates", "promotes"]
stemmer = PorterStemmer()
dict= []
for i in my_dictionary:
    temp = stemmer.stem(i)
    if temp not in dict:
        dict.append(temp)
data = pd.read_csv("Abstract.csv")

#dataframe to collect the required sentences
ReqSentences = pd.DataFrame(columns = ["Text"]) 
for i in range(len(data["Text"])):
    text = data["Text"][i]
    sent = nltk.sent_tokenize(text)
    for foo in sent:
        cleansent = cleanSentences(foo)
        seq = nltk.word_tokenize(cleansent)
        for text in seq:
            for sub in dict:
                if sub in text:
                    ReqSentences = ReqSentences.append({'Text': foo}, ignore_index=True)
                break

ReqSentences = ReqSentences.drop_duplicates("Text")
print(len(ReqSentences))

#Saving cleaned abstracts into csv file
ReqSentences.to_csv("ReqSentences.csv", sep=',', encoding='utf- 8')


#************************************

#STEP : 2
#Training the Parts of Speech Tagger

Medposttagger = []
def split_at(s, c, n):
    words = s.split(c)
    return c.join(words[:n]), c.join(words[n:])

#Using medpost tagged sentences for training the tagger.
folder_path = 'medpost\\tagged'
for filename in glob.glob(os.path.join(folder_path, '*.ioc')):
  with open(filename, 'r') as f:
    content =  [n for n in f.readlines() if not n.startswith('P')]
    for i in content:
        token = nltk.word_tokenize(i)
        inner = []
        for each in token:
            inner.append(split_at(each, '_', 1))
        Medposttagger.append(inner)

#Convert words.db file into words.txt file for easy accessing in medpost folder.
#Training the tagger with more words from the Medpost database
folder_path = 'medpost\\'
for filename in glob.glob(os.path.join(folder_path, '*.txt')):
  with open(filename, 'r') as f:      
    content =  [n for n in f.readlines()]
    for i in content:
        token = nltk.word_tokenize(i)
        foo = split_at(token[1], ':', 1)
        temp = split_at(foo[0], '_', 1)
        inner =[]
        inner.append(temp)
        Medposttagger.append(inner)
        
print(len(Medposttagger))
#Taining using combined tagger.
t0 = nltk.DefaultTagger("NN")
t1 = nltk.UnigramTagger(Medposttagger, backoff=t0)
t2 = nltk.BigramTagger(Medposttagger, backoff=t1)


#*********************************************
#STEP : 3

#Running trained tagger on our data and collecting only Noun forms


data = pd.read_csv('ReqSentences.csv', encoding = 'latin-1')
tagged=[]
POStagger = pd.DataFrame(columns = ["Word","POStag"])
for i in range(len(data)):
    line = data["Text"][i]
    token = nltk.word_tokenize(str(line))
    temp = t2.tag(token)
    for j in range(len(temp)):
        if temp[j][1] in ('NN','NNP', 'NNS'):
            if temp[j] not in tagged:
                tagged.append(temp[j])
                POStagger = POStagger.append({"Word":temp[j][0],"POStag" :temp[j][1]},ignore_index = True)
    
print(len(tagged))


#Parts of speech tagger containing the words and their parts of speech(only NN.NNS and NNP)
POStagger.to_csv(r'POStagger.csv', sep=',')

#*********************************************

#STEP : 4
#Accessing UMLS database to find out the Semantic type associated with the noun forms collected

r = re.compile(r'\bgene\b | \bprotein\b | \bgeneome\b', flags=re.I | re.X)
Semantictypelist  = []
errorList = []
count = 0
for i in range(len(tagged)):
    count = count+1
    print(count)
    innerpair = []
    innerpair.append(tagged[i][0])
    gene = '%'+ tagged[i][0] + '%'
    temp = "'"+gene+"'"
    db = pymysql.connect(host = "localhost", user = "root", password = "", database = "umls")
    cursor = db.cursor()
    q = "SELECT DISTINCT CUI, STR FROM mrconso where STR LIKE "
    l = " LIMIT 3"
    a = q + temp  + l
    query = (a)
    try:        
        cursor.execute(query)
        CUI = []
        for a in cursor:       
            flag1 = 0
            xx = r.findall(a[1])
            if xx:
                flag1 = 1
                break
            else :
                if a[0] not in CUI:
                    CUI.append(a[0])
        inner = []
        if flag1 :
            inner.append(xx[0])
            innerpair.append(inner)
        else :              
            for j in range(len(CUI)):
                flag2 = 0
                q = "SELECT STY FROM mrsty where CUI =  "
                temp = CUI[j]
                temp1 = "'" + temp + "'"
                a = q + temp1
                query = (a)
                cursor.execute(query)
                for b in cursor:
                    yy = r.findall(str(b))
                    if yy:
                        inner.append(yy[0])
                        flag2 = 1
                        break
                    else :
                        inner.append(b[0])
                if flag2:
                    break
            if len(inner):
                innerpair.append(inner)
        Semantictypelist.append(innerpair)
    except :
        errorList.append(tagged[i][0])
        
Semanticdf = pd.DataFrame(Semantictypelist, columns=['Word','SemanticType'] ) 
POStag = {}
for i in tagged:
    POStag[i[0]]=i[1]
temp = []  
for i in range(len(Semantictypelist)):
    t = Semantictypelist[i][0]
    temp.append(POStag[t])       
se = pd.Series(temp)
Semanticdf['POStag'] = se.values

#Creating csv file containing only proteins and genes with their semantic type and POS tag
proteinlist = pd.DataFrame(columns = ["Word","SemanticType","POStag"])
for i in range(len(Semanticdf)):
    yy = r.findall(str(Semanticdf["SemanticType"][i]))
    if len(yy):
        proteinlist = proteinlist.append({"Word":Semanticdf["Word"][i],"SemanticType":Semanticdf["SemanticType"][i],"POStag" :Semanticdf["POStag"][i]},ignore_index = True) 
print(len(proteinlist))

proteinlist.to_csv(r'proteingenelist.csv', sep=',')


#************************************************************
#STEP : 5

#Generating final dataset of sentences with more than one gene or protein and the action between them

semanticdict = {}               
for i in range(len(proteinlist)):
    semanticdict[proteinlist["Word"][i]] = str(proteinlist["SemanticType"][i])

finaldataset = pd.DataFrame(columns = ["Gene","Action","Sentence"])

#data = pd.read_csv('ReqSentences.csv', encoding = 'latin-1')
for i in range(len(data)):
    sen = data["Text"][i]
    token = nltk.word_tokenize(str(sen))
    list1 = []
    for word in token:
        if word in my_dictionary:
            if word not in list1:
                list1.append(word)
    temp = t2.tag(token)
    tagged = []
    for j in range(len(temp)):
        if temp[j][1] in ('NN','NNP', 'NNS'):
            if temp[j] not in tagged:
                tagged.append(temp[j]) 

    templist2 = [] 
    for i in range(len(tagged)):   
        if tagged[i][0] in list(proteinlist["Word"]):
            yy = str(semanticdict[tagged[i][0]])[1:-1]
            templist2.append(str(tagged[i][0]) + " : " + str(r.findall(str(yy)))) 
  
    for j in range(len(list1)):
        if len(templist2) > 1:
            finaldataset = finaldataset.append({"Gene":templist2,"Action":list1[j],"Sentence":sen},ignore_index = True) 
  
print(len(finaldataset))

#Saving final dataset into csv file
finaldataset.to_csv(r'finaldataset.csv', sep=',')

#********************************************************************

#STEP : 6
#dataset generation for Visualizing the gene-protein interaction in Cytoscape
import pandas as pd
import ast

#Provide the File generated at the end of STEP : 5
data = pd.read_csv('finaldataset.csv', encoding = 'latin-1')
Visualization = pd.DataFrame(columns = ["Gene1","Action","Gene2"])

for i in range(len(data)):
    x = data["Gene"][i]
    action = data["Action"][i]    
    x =ast.literal_eval(x)
    k = x[0].split(":")
    for i in range(1,len(x),1):
        m = x[i].split(":")
        Visualization = Visualization.append({"Gene1":k[0],"Action":action,"Gene2":m[0]},ignore_index = True)

#saving the gene - protein- action Dataset 
Visualization.to_csv(r'Visualization.csv', sep=',')

*****************************************************************






