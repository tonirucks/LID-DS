import random
from typing import Optional
import pymysql
import sys

db_name = "textDB"

words = open('./words.txt').read().splitlines()
# print(len(words))
host = sys.argv[1]
uname = sys.argv[2]
passwd = sys.argv[3]
db: Optional[pymysql.Connection] = None


def connect_to_db():
    global db
    try:
        if db is None:
            db = pymysql.connect(host, uname, passwd, db_name)
            print("Established")
    except:
        print("Exception while connection")


def insert():
    global db
    word = random.choice(words).replace("'", "")
    sql = "INSERT INTO `texts` (`text`) VALUES ('" + word + "');"
    with db.cursor() as cursor:
        db.begin()
        cursor.execute(sql)
    db.commit()
    print("Insert: " + word)


def query():
    global db
    sql = "SELECT * FROM `texts` ORDER BY RAND() LIMIT 1"
    with db.cursor() as cursor:
        cursor.execute(sql)
    result = cursor.fetchone()
    print("Got: " + result[1])


if __name__ == '__main__':
    while True:
        sys.stdin.readline()
        try:
            if random.random() > 0.5:
                insert()
            else:
                query()
        except Exception as e1:
            connect_to_db()
