import operator
import re
from collections import Counter
from functools import reduce


def words(text): return re.findall(r'\w+', text.lower())


def words_n_nums(text): return re.findall(r'\w+|\d+', text.lower())


def triples(words):
    triples = {}
    i = 0
    while i in range(len(words) - 2):
        triples[words[i] + ' ' + words[i + 1]] = int(words[i + 2])
        i += 3
    return triples


WORDS = Counter(words(open('big.txt').read()))
PHRASES = triples(words_n_nums(open('count_2w.txt').read()))


def Pword(word, N=sum(WORDS.values())):
    """Probability of `word`."""
    return WORDS[word] / N


def Pphrase(word, before=None, M=sum(PHRASES.values())):
    if before:
        try:
            # print(f'----word={word} before={before}----')
            return PHRASES[before + ' ' + word] / M
        except Exception:
            print(f'-------word = {word} before = {before}-------')

            return 1 / M

    return Pword(word)


def text_correction(text):
    "Spell-correct all words in text."
    result = ''
    tokens = words(text)
    for i in range(len(tokens)):
        if i > 0 and known(tokens[i - 1]):
            result += ' ' + phrase_correction(before=tokens[i - 1], word=tokens[i])
        else:
            result += ' ' + phrase_correction(word=tokens[i])
    return result


def word_correction(word):
    """Most probable spelling correction for word."""
    return max(candidates(word), key=Pword)


def phrase_correction(word, before=None):
    max = -1
    result = ''
    c = candidates(word)
    for item in c:
        p = Pphrase(item, before)
        print(f'before = {before}, word = {item}, p = {p}, max = {max}')
        if p and p > max:
            max = p
            result = item
            print(f'UPDATED: before = {before}, word = {item}, p = {p}, max = {max}')
            print("")
    return result


def candidates(word):
    """Generate possible spelling corrections for word."""
    return known([word]) or known(edits1(word)) or known(edits2(word)) or [word]


def known(words):
    """The subset of `words` that appear in the dictionary of WORDS."""
    return set(w for w in words if w in WORDS)


def edits1(word):
    """All edits that are one edit away from `word`."""
    letters = 'abcdefghijklmnopqrstuvwxyz'
    splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    deletes = [L + R[1:] for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]
    replaces = [L + c + R[1:] for L, R in splits if R for c in letters]
    inserts = [L + c + R for L, R in splits for c in letters]
    return set(deletes + transposes + replaces + inserts)


def edits2(word):
    """All edits that are two edits away from `word`."""
    return (e2 for e1 in edits1(word) for e2 in edits1(e1))


def segment(text):
    "Return a list of words that is the best segmentation of text."
    if not text: return []
    candidates = ([first] + segment(rem) for first, rem in splits(text))
    return max(candidates, key=Pwords)


def splits(text, L=20):
    "Return a list of all possible (first, rem) pairs, len(first)<=L."
    return [(text[:i + 1], text[i + 1:])
            for i in range(min(len(text), L))]


def Pwords(words):
    "The Naive Bayes probability of a sequence of words."
    return product(Pword(word) for word in words)


def product(nums):
    "Return the product of a sequence of numbers."
    return reduce(operator.mul, nums, 1)


# print(text_correction("London ia a caapitak"))
print(Pphrase("is", "london"))
print(Pphrase("in", "london"))
print(Pphrase("a", "london"))
