from bs4 import BeautifulSoup
from bs4.element import Comment
import urllib
import logging
import pymysql
from datetime import datetime
import json

"""
Logging
"""
logger = logging.getLogger('LTV Project')
format = "%(asctime)s   [%(levelname)s]  [%(lineno)d] %(message)s"
logging.basicConfig(format=format, level=logging.INFO)


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


def insert_data(dataDate, hash_map):
    conn = pymysql.connect(host=hostname,
                             user=username,
                             password=passwd,
                             port=port,
                             db=dbname,
                             charset='utf8mb4')

    try:
        with conn.cursor() as cursor:
            # Create a new record
            sql = "INSERT INTO `wordCount` (`dateOnly`, `word`, `count`) "\
                "VALUES (%s, %s, %s)"

            cursor.execute(sql, (dataDate, word, count))

            logger.info("Data inserted!")
        conn.commit()

    finally:
        conn.close()


html = urllib.urlopen(raw_input()).read()
readable_content = text_from_html(html).split(' ')

hash_map = dict()

for word in readable_content:
    #print word
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

logger.info("Printing words having count greater than 1: ")
for key in hash_map:
    if hash_map[key] > 0:
        print key, hash_map[key]


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

logger.info("DB connection details are : \n hostname : {0} \n dbname : {1} \n username : {2} \n password : {3} \n port : {4}".format(hostname, dbname, username, passwd, port))


dataDate = datetime.now().strftime('%Y%m%d')
logger.info(dataDate)
logger.info("Inserting data in database")

for key in hash_map:
    if hash_map[key] > 0:
        insert_data(dataDate, hash_map)

"""
try:
  cnx = mysql.connector.connect(user='scott',
                                database='testt')
except mysql.connector.Error as err:
  if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
    logger.error("Something is wrong with your user name or password")
  elif err.errno == errorcode.ER_BAD_DB_ERROR:
    logger.error("Database does not exist")
  else:
    logger.error(err)
else:
  cnx.close()
"""

