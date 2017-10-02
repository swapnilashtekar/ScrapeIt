from bs4 import BeautifulSoup
from bs4.element import Comment
import urllib
import logging
import pymysql
from datetime import datetime
import json, time, re, string
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

"""
Logging
"""

logger = logging.getLogger('ScrapeIt Project')
format = "%(asctime)s   [%(levelname)s]  [%(lineno)d] %(message)s"
logging.basicConfig(format=format, level=logging.INFO)


def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


def text_from_html(body):
    soup = BeautifulSoup(body, 'html.parser')
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)  
    return u" ".join(t.strip() for t in visible_texts)


def insert_data(epoch, input_url, word, word_count):
    conn = pymysql.connect(host=hostname,
                            user=username,
                            password=passwd,
                            port=port,
                            db=dbname,
                            charset='utf8mb4')

    logger.debug("dataDate : {0} input_web : {1} word : {2} word type : {3} count : \
        {4}".format(epoch, input_url, word, type(word), word_count))

    try:
        with conn.cursor() as cursor:
            # Create a new record
            sql = "INSERT INTO `wordCountTable` (`epoch`, `url`, `word`, `wordCount`) "\
                "VALUES (%s, %s, %s, %s)"

            cursor.execute(sql, (epoch, input_url, word, word_count))

            logger.debug("Data inserted!")
        conn.commit()

    finally:
        conn.close()

logger.info("Enter the website to scrape: ")
input_url = raw_input()
html = urllib.urlopen(input_url).read()
logger.debug(text_from_html(html))
readable_content = text_from_html(html).split(' ')
logger.debug("Readable content found if : ".format(readable_content))
logger.info("Number of words read are : {}".format(len(readable_content)))
hash_map = dict()
cant_read = []
for word in readable_content:
    #print word, type(word), word.encode('utf-8')
    exclude_punctuations = string.punctuation
    #if word.isalnum():
    #if isinstance(word,unicode ):
    for c in exclude_punctuations:
        word = word.replace(c, "")

    word = word.strip().lower()
    word = word.decode('unicode_escape').encode('ascii','ignore')
    if len(word.encode('utf-8')) > 0:
        count = hash_map.get(word, 0)
        hash_map[word] = count + 1
    else:
        cant_read.append(word)

logger.debug("Excluded words are : {0} \n Number of excluded words \
    are : {1}".format(cant_read, len(cant_read)))
logger.debug("Printing words having count greater than 0: ")
for key in hash_map:
    if hash_map[key] > 0:
        logger.debug("{0} {1}".format(key, hash_map[key]))


with open('db_config.json', 'r') as f:
    try:
        logger.info("Loading database config file")
        db_config = json.load(f)
    except:
        logger.warn("Error with loading database config!")

#db connection details
hostname = db_config['host']
dbname = db_config['dbname']
username = db_config['username']
passwd = db_config['password']
port = db_config['port']

logger.debug("DB connection details are : \n hostname : {0} \n dbname : {1} \n username : {2} \n \
    password : {3} \n port : {4}".format(hostname, dbname, username, passwd, port))

epoch = datetime.now().strftime('%s')
logger.info(epoch)
logger.debug("Inserting data in database")

for key in hash_map:
    if hash_map[key] > 0:
        insert_data(epoch, input_url, key, hash_map[key])