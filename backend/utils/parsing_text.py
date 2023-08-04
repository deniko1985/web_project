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


if __name__ == "__main__":
    text = """Альбом был тематически разделён на две части. Первую составили более жизнерадостные песни, исполненные в стиле, приближенном к популярной музыке. Вторая часть, состоявшая из семи композиций, была объединена в песенную сюиту под названием «Девятый вал», отсылавшим к одноимённому художественному образу, и представляла собой концептуальный альбом, рассказывавший историю девушки, выброшенной в открытое море за борт корабля, предпринимавшей попытки сохранить своё «я» бодрствующим, дав волю воображению. На пластинке певица затрагивала разнообразные темы. Песни первой половины были написаны под влиянием фильмов ужасов, автобиографической литературы, воспоминаний о детстве и домашних животных, размышлений о взаимоотношении полов и материнстве. Важное место в смысловом и символическом содержании пластинки было уделено теме природы. Сквозной темой, проявлявшейся на протяжении всего альбома, стали отношения Кейт Буш и её семьи."""
    asyncio.run(extrack_keywords(text))
