from nltk.tokenize import word_tokenize, sent_tokenize

__author__ = 'chetannaik'

''' Represents the class of snippet item contains - snippet string
    link and list of sentences'''

class SnippetItem:

    snippet = ''
    link = ''
    sent = []
    triples = []

def get_sentences(result):
    if 'items' in result:
        sentences = []
        for item in result[u'items']:
            snippet = item[u'snippet'].replace('\n', '').encode('ascii',
                                                                'ignore')
            link = item[u'link']
            print "link is..",link

            s = SnippetItem()
            s.snippet = snippet
            s.sent = sent_tokenize(snippet)
            s.link = link

            sentences.append(s)
        #ret_data = list(set(sentences))
        ret_data = sentences
    else:
        ret_data = []
    return ret_data


def filter_sentences(sentences, keyword=None):
    valid_sentences = []
    for sentence in sentences:
        tokens = word_tokenize(sentence)
        if is_valid_sentence(sentence, tokens):
            valid_sentences.append(sentence)
    filtered_sentences = []
    if keyword:
        for word in keyword:
            filtered_sentences.extend(
                filter(lambda x: word.lower() in x.lower(), valid_sentences))
    else:
        filtered_sentences = valid_sentences
    return list(set(filtered_sentences))


def is_valid_sentence(sentence, tokens):
    # Sentence has just one full-stop.
    # if sentence.count('.') != 1:
    #     return False

    # Sentence doesn't have the following symbols.
    # if any(symbol in sentence for symbol in ['?', '_', '<']):
    #     return False

    # Sentence length lies in the following range.
    if len(sentence) < 40:
        return False

    # Sentence does not have ALL CAPS tokens of length 2 or greater.
    # if sum(map(lambda x: len(x) >= 2 and x.isupper(), tokens)):
    #     return False

    # Sentence does not have 2 or more tokens which end with "tion".
    # if sentence.endswith("..."):
    #     return False

    # Sentence does not start with character.
    if not sentence[0].isalpha():
        return False

    # Sentence does not start with character.
    if "..." in sentence and sentence.index("...") < 10:
        return False

    # Sentence does not start with capital letter character.
    # if not sentence[0].isupper():
    #     return False

    return True
