from flask import Flask, render_template
from db import get_db, close_db
import sqlalchemy
from logger import log
import requests 
from bardapi.constants import SESSION_HEADERS
from bardapi import Bard

token = "dQhvWFqsmqBZFXIj3awh3yYbM3GZJBM6tGY_HC2Yyk9xnmf7kKG8p_RdQxjaZjHabDAnBA."

def seassionCookieSet(session):
    session.cookies.set("__Secure-1PSID", token)
    session.cookies.set("__Secure-1PSIDTS", "sidts-CjEBPVxjSshve7oZ2z9UHXnwPrd-X3AbLFV1CmaGVvhUhakO2SaSoBT2addpCtpd2WoYEAA")

    return session

sessions = []

# session = requests.Session()
# session.headers = SESSION_HEADERS
# bard = Bard(token=token, session=session)

app = Flask(__name__)
app.teardown_appcontext(close_db)


@app.route("/")
def index():
    return "Hello World"

@app.route('/chat', methods=['POST'])
def process_json():
   content_type = request.headers.get('Content-Type')
   if (content_type == 'application/json'):
       json = request.get_json()
       # We will have a session code and thing with very normal
       sessionID = json['session']
       prompt = json['prompt']
       if not sessionID in sessions:
           newSessions = requests.Session()
           newSessions.headers = SESSION_HEADERS
           newSessions = seassionCookieSet(newSessions)
           bard = Bard(token=token, session=newSessions)
           sessions[sessionID] = bard
           bard.get_answer(prompt)['content']
           return bard
       else:
           return sessions[sessionID].get_answer(prompt)['content']
   else:
       return 'Content-Type not supported!'


@app.route("/health")
def health():
    log.info("Checking /health")
    db = get_db()
    health = "BAD"
    try:
        result = db.execute("SELECT NOW()")
        result = result.one()
        health = "OK"
        log.info(f"/health reported OK including database connection: {result}")
    except sqlalchemy.exc.OperationalError as e:
        msg = f"sqlalchemy.exc.OperationalError: {e}"
        log.error(msg)
    except Exception as e:
        msg = f"Error performing healthcheck: {e}"
        log.error(msg)

    return health
