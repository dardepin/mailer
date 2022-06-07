#v 0.1
#recv mail
#make skip some mails by number
import poplib
import getpass
import sqlite3
from sqlite3 import Error
import email
import config

def storemail(uid, content):
    #print(content[1])
    try:
        db = sqlite3.connect(config.maildb)
        cur = db.cursor()
        sql_exec = '''INSERT INTO MAILS (uid, body) VALUES (?, ?);'''
        cur.execute(sql_exec, (uid, content))
        db.commit()
        db.close()
    except Error as e:
        print(e)
    return

def checkuid(uid):
    try:
        db = sqlite3.connect(config.maildb)
        cur = db.cursor()
        cur.execute("SELECT * FROM mails WHERE uid=?", (uid,))
        rows = cur.fetchall()
        if len(rows):
            print("Mail record with uid: ", uid, " is allready in database")
            return False
        db.close()
    except Error as e:
        print(e)

    return True

def recvmail(mail, idx, size):
    mailuid = str(mail.uidl(idx).split()[2])[2:-1]

    print("Recieving mail #", idx, " with uid: ", mailuid, " and size: ", size)
    if(checkuid(mailuid)):
        mailcontent = mail.top(idx, size)
        mailcontent = ' '.join(map(str, mailcontent[1]))

        content = email.message_from_string(mailcontent)
        #X-Rcpt-To: yaltch-sergeev_aa@med.cap.ru
        #X-Return-Path: www-data@ticket.med.cap.ru

        storemail(mailuid, mailcontent)
    return

def checkmail(mail):
    maillist = mail.list()[1] #[b'1 5093', b'2 6706', b'3 43115', b'4 5083']

    for i in range (len(maillist)):

        mailidx = int(maillist[i].split()[0]) #1
        mailsiz = int(maillist[i].split()[1]) #5093
        recvmail(mail, mailidx, mailsiz)

    return

def opendatabase():
    try:
        db = sqlite3.connect(config.maildb)
        #create table if not exists
        db.execute('''CREATE TABLE IF NOT EXISTS `MAILS` (
	`id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    `uid` TEXT NOT NULL,
	`from` TEXT,
	`to` TEXT,
	`body` TEXT NOT NULL);''')
        db.close()
    except Error as e:
        print(e)

opendatabase()

mail = poplib.POP3(config.mailserver, config.mailport)
mail.set_debuglevel(True)
mail.getwelcome()
if config.mailuser == '':
    config.mailuser = getpass.getuser()
mail.user(config.mailuser)
if config.mailpassword == '':
    config.mailpassword = getpass.getpass()
mail.pass_(config.mailpassword)

checkmail(mail)
mail.quit()
