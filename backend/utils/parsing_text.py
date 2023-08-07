import nltk
from nltk.corpus import wordnet as wn
from nltk.stem.wordnet import WordNetLemmatizer
from pymorphy2 import MorphAnalyzer
from collections import Counter
import asyncio

# nltk.download('all')


async def get_lemma(word):
    lemma = wn.morphy(word)
    if lemma is None:
        return word
    else:
        return lemma


async def get_lemma2(word):
    return WordNetLemmatizer().lemmatize(word)


async def extrack_keywords(text: str, lang: str):
    if lang == "ru":
        lang = "russian"
    else:
        lang = "english"
    morph = MorphAnalyzer()
    ru_stop = set(nltk.corpus.stopwords.words(lang))
    tokens = nltk.word_tokenize(text)
    tokens = [token for token in tokens if token not in ru_stop]
    lemmas = [morph.parse(token)[0].normal_form for token in tokens if token.isalpha()]
    # freq_dist = nltk.FeatDict(lemmas)
    freq_dist = Counter(lemmas)
    keywords = [word for word, freq in freq_dist.most_common(5)]
    print(keywords)
    return keywords
