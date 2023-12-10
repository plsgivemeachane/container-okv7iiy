from flask import Flask, render_template, request
from db import get_db, close_db
import sqlalchemy
from logger import log
import requests, pickle
from bardapi.constants import SESSION_HEADERS
from bardapi import Bard

token = "dQhvWFqsmqBZFXIj3awh3yYbM3GZJBM6tGY_HC2Yyk9xnmf7Is7I50ubX7rYVwIkUtLPIg."
# Get your proxy url at crawlbase https://crawlbase.com/docs/smart-proxy/get/
proxy_url = "http://KSEeVxog5zzqey9Leo4d2A@smartproxy.crawlbase.com:8012" 
proxies = {"http": proxy_url, "https": proxy_url}
sessions = {}

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
    global sessions
    content_type = request.headers.get('Content-Type')

    try:
        import os
        if (content_type == 'application/json'):
            json = request.json
            # We will have a session code and thing with very normal
            sessionID = json.get('session')
            prompt = json.get('prompt')
            # print(sessions)
            # Get the session with file
            if not os.path.exists(f"{sessionID}.ses"):
                print("HERE")
                newSessions = requests.Session()
                newSessions.headers = SESSION_HEADERS
                newSessions.cookies.set("__Secure-3PSID", token)
                bard = Bard(token=token, session=newSessions, proxies=proxies)
                print("Adding Session")
                # sessions[sessionID] = bard
                with open(f"{sessionID}.ses", 'wb') as f:
                    pickle.dump(newSessions.cookies, f)
                answer = bard.get_answer(prompt)['content']
                return answer
            else:
                session = requests.session()  # or an existing session
                with open(f"{sessionID}.ses", 'rb') as f:
                    session.cookies.update(pickle.load(f))
                bard = Bard(token=token, session=session, proxies=proxies)
                return bard.get_answer(prompt)['content']
        else:
            return 'Content-Type not supported!'
    except Exception as e:
        return str(e)


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
