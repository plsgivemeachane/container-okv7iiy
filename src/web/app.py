from flask import Flask, render_template
from db import get_db, close_db
import sqlalchemy
from logger import log
from bardapi import BardCookies

cookie_dict = {
    "__Secure-1PSID": "dQizb195ybo1-3d0hl1vq2G3Ef86-3KAfSwQwyWlW6Sn5H-FjMMGXImZN1QCbHUbcoHZ7w.",
    "__Secure-1PSIDTS": "sidts-CjEBPVxjSshve7oZ2z9UHXnwPrd-X3AbLFV1CmaGVvhUhakO2SaSoBT2addpCtpd2WoYEAA",
}
bard = BardCookies(cookie_dict=cookie_dict)

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
