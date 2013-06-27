import email, getpass, imaplib, os
from pymongo import MongoClient
from email.header import decode_header, make_header
from bs4 import BeautifulSoup

from email.Header import decode_header
import email
from base64 import b64decode
import sys
from email.Parser import Parser as EmailParser
from email.utils import parseaddr
from StringIO import StringIO

from dateutil import parser

import datetime



class NotSupportedMailFormat(Exception):
    pass


def parse_attachment(message_part):

    try:
        content_disposition = message_part.get("Content-Disposition", None)
        if content_disposition:
            dispositions = content_disposition.strip().split(";")
            if bool(content_disposition and dispositions[0].lower() == "attachment"):
    
                file_data = message_part.get_payload(decode=True)
                attachment = StringIO(file_data)
                attachment.content_type = message_part.get_content_type()
                attachment.size = len(file_data)
                attachment.name = None
                attachment.create_date = None
                attachment.mod_date = None
                attachment.read_date = None
    
                for param in dispositions[1:]:
                    name,value = param.split("=")
                    name = name.lower()
    
                    if name == "filename":
                        attachment.name = value
                    elif name == "create-date":
                        attachment.create_date = value  #TODO: datetime
                    elif name == "modification-date":
                        attachment.mod_date = value #TODO: datetime
                    elif name == "read-date":
                        attachment.read_date = value #TODO: datetime
                return attachment
    except:
        print "MISSED AN ATTACHMENT"

    return None

def parse(content):
    #p = EmailParser()
    #msgobj = p.parse(content)
    msgobj = content
    messagedate = parser.parse(msgobj['Date'])
    if msgobj['Subject'] is not None:
        decodefrag = decode_header(msgobj['Subject'])
        subj_fragments = []
        for s , enc in decodefrag:
            if enc:
                try:
                    s = unicode(s , enc).encode('utf8','replace')
                except:
                    print "CANNOT DECODE"

            subj_fragments.append(s)
        subject = ''.join(subj_fragments)
    else:
        subject = None

    attachments = []
    body = None
    html = None
    for part in msgobj.walk():
        attachment = None#parse_attachment(part)
        if attachment:
            attachments.append(attachment)
        elif part.get_content_type() == "text/plain":
            try:
                if body is None:
                    body = ""
                body += unicode(
                    part.get_payload(decode=True),
                    "Latin-1" if part.get_content_charset() is None else part.get_content_charset(),
                    'replace'
                ).encode('utf8','replace')
            except:
                print "CANNOT DECODE"
        elif part.get_content_type() == "text/html":
            try:
                if html is None:
                    html = ""
                html += unicode(
                    part.get_payload(decode=True),
                    "Latin-1" if part.get_content_charset() is None else part.get_content_charset(),
                    'replace'
                ).encode('utf8','replace')
            except:
                print "CANNOT DECODE"
    return {
        'date' : messagedate,
        'subject' : subject,
        'body' : body,
        'html' : html,
        'from' : parseaddr(msgobj.get('From'))[1],
        'to' : parseaddr(msgobj.get('To'))[1],
        'attachments': attachments,
    }


def decodeEmailString(o) :
    text, encoding = decode_header(o)[0]
    if encoding==None:
        return text.encode('utf8')
    else:
        return text.decode(encoding).encode('utf8')
    uc = str(o).decode('cp1252')
    return uc.encode('utf8')

detach_dir = './files' # directory where to save attachments (default: current)
user = "mihai@rosoftlab.net"
pwd = "qLoOLpYeVBTaTo2"

# connecting to the gmail imap server
m = imaplib.IMAP4_SSL("imap.gmail.com")
m.login(user,pwd)
m.select("[Gmail]/All Mail") # here you a can choose a mail box like INBOX instead
# use m.list() to get all the mailboxes

resp, items = m.search(None, "ALL") # you could filter using the IMAP rules here (check http://www.example-code.com/csharp/imap-search-critera.asp)
items = items[0].split() # getting the mails id

counter = 0

errors_text = 0
errors_part = 0   

client = MongoClient()
db = client.mails6
mails = db.alltextmail

#mails.find( { qty: { $in: [ 5, 15 ] } } )

#mongomails = mails.find()

items = [item for item in items if mails.find_one({"id": item}) is None]

#for mongomail in mails.find():
#    if items[mongomail['id']] is not None:
#        del items[mongomail['id']]

for emailid in items:
    try:
        resp, data = m.fetch(emailid, "(RFC822)") # fetching the mail, "`(RFC822)`" means "get the whole stuff", but you can ask for headers only, etc
        email_body = data[0][1] # getting the mail content
        mail = email.message_from_string(email_body) # parsing the mail content to get a mail object
    
        parsedmail = parse(mail)
        parsedmail['id'] = emailid
        print parsedmail['from']
        
        mongoid = mails.insert(parsedmail)
        print "inserted "+str(mongoid)
    except:
        print "missed an email"
            
    
print "part errors: " + str(errors_part) + " text errors: " + str(errors_text)
    


