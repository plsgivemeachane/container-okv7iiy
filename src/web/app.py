from flask import Flask, render_template
from db import get_db, close_db
import sqlalchemy
from logger import log
import requests 
from bardapi.constants import SESSION_HEADERS
from bardapi import Bard

token = "dQhvWFqsmqBZFXIj3awh3yYbM3GZJBM6tGY_HC2Yyk9xnmf7kKG8p_RdQxjaZjHabDAnBA."

session = requests.Session()
session.headers = SESSION_HEADERS
session.cookies.set("__Secure-1PSID", token)
session.cookies.set("__Secure-1PSIDTS", "sidts-CjEBPVxjSshve7oZ2z9UHXnwPrd-X3AbLFV1CmaGVvhUhakO2SaSoBT2addpCtpd2WoYEAA")

bard = Bard(token=token, session=session)

app = Flask(__name__)
app.teardown_appcontext(close_db)


@app.route("/")
def index():
    return bard.get_answer("Hello Bard")['content']


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
