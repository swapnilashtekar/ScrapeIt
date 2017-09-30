from bs4 import BeautifulSoup
from bs4.element import Comment
import urllib
import logging

def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


def text_from_html(body):
    soup = BeautifulSoup(body, 'html.parser')
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)  
    return u" ".join(t.strip() for t in visible_texts)



html = urllib.urlopen(raw_input()).read()
readable_content = text_from_html(html).split(' ')

hash_map = dict()

for word in readable_content:
    print word
    if word.isalnum():
        word = word.strip()

        count = hash_map.get(word, 0)
        hash_map[word] = count + 1
        """
        if word in hash_map:
            hash_map[word] += 1
        else:
            hash_map[word] = 1
        """

print "Printing words having count greater than 1: "
for key in hash_map:
    if hash_map[key] > 1:
        print key, hash_map[key]

