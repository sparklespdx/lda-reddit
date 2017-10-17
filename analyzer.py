import os
import pprint
import praw
from nltk.tokenize import RegexpTokenizer
from nltk.stem.porter import PorterStemmer

from stop_words import get_stop_words
from gensim import corpora, models
import gensim

from scraper import ScrapedSubmission, ScrapedComment


r = praw.Reddit(client_id=os.environ.get('PRAW_CLIENT_ID'),
                client_secret=os.environ.get('PRAW_CLIENT_SECRET'),
                user_agent='PRAW/Python 3.6.2')


def tokens_factory(id):
    # Need to control for 1000+ words per document
    post = ScrapedSubmission(r, id)
    post.comments = post.get_comments()

    # Need to mess around with a better match or standard tokenizer
    # We're also getting the end letter of words chopped off, might be here.
    tokenizer = RegexpTokenizer(r'\w+')
    post.tokens = []

    for c in post.comments:
        raw = c.body.lower()
        post.tokens += tokenizer.tokenize(raw)

    return post


def stop_and_stem(post):
    # We're using Porter algorithm for no real reason, probably build another.
    p_stemmer = PorterStemmer()
    # End letter of words is getting chopped, might also be here.
    post.stopped_tokens = [i for i in post.tokens if i not in get_stop_words('en')]
    post.stemmed_tokens = [p_stemmer.stem(i) for i in post.stopped_tokens]
    return post


def dtmatrix(posts):
    texts = [i.stemmed_tokens for i in posts]
    dictionary = corpora.Dictionary(texts)
    corpus = [dictionary.doc2bow(text) for text in texts]
    return posts, dictionary, corpus


def run_model(posts, dictionary, corpus):
    return posts, gensim.models.ldamodel.LdaModel(corpus, num_topics=2, id2word=dictionary, passes=20)


# Testing
test_submission = '764fue'
p = tokens_factory(test_submission)
p = stop_and_stem(p)
posts, dictionary, corpus = dtmatrix([p])
posts, ldamodel = run_model(posts, dictionary, corpus)
print(ldamodel.print_topics(num_topics=2, num_words=4))
