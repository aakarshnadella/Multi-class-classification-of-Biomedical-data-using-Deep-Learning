from gensim.models import Word2Vec
import re
import nltk
strip_special_chars = re.compile("[^A-Za-z0-9 ]+")
#cleaning each sentence to remove punctuations
def cleanSentences(raw_tweets):
    remove_urls = re.sub(r'http\S+','',raw_tweets)
    remove_usernames = re.sub(r'@\w*','',remove_urls)
    string = remove_usernames.lower().replace("<br />", " ")
    string.replace('[^\w\s]','')
    return re.sub(strip_special_chars, "", string.lower()) 
#collection of sentences
data = ["TDZ treatment induced nuclear condensation, Mitochondrial membrane potential loss, Mitochondrial Cytochrome c release, activation of Caspase-9 and Caspase-3 substantiating mitochondrial pathways of apoptosis in cells!."]

#Tokenizing each sentence and passing as a list of words to word2vec
sentences = []
for i in data:
    t = cleanSentences(i)
    print(t)
    temp = nltk.word_tokenize(t)
    sentences.append(temp)
    
# train model
model = Word2Vec(sentences, size = 10, min_count=1)# By changing size we get required number of dimensions
# summarize the loaded model
print(model)
# summarize vocabulary
words = list(model.wv.vocab)
print(words)
# access vector for one word
print(model['membrane'])
print(model['apoptosis'])

    