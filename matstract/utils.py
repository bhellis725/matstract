import os
import json
from pymongo import MongoClient
from elasticsearch import Elasticsearch
from os import environ as env
import certifi


def open_db_connection(user_creds=None, local=False, access="read_only", db="tri_abstracts"):
    if 'MATSTRACT_HOST' in env and local:
        if db == "tri_abstracts":
            db = env['MATSTRACT_DB']
        uri = "mongodb://%s:%s/%s" % (
            env['MATSTRACT_HOST'], env['MATSTRACT_PORT'], db)
        db_creds = {'db': db }
    else:
        try:
            if user_creds is not None:
                db_creds_filename = user_creds
            else:
                db_creds_filename = os.path.join(
                    os.path.dirname(os.path.abspath(__file__)), '_config.json')
            with open(db_creds_filename) as f:
                db_creds = json.load(f)["mongo"]
        except:
            if access == "read_only":
                db_creds = {"user": os.environ["ATLAS_USER"],
                            "pass": os.environ["ATLAS_USER_PASSWORD"],
                            "rest": os.environ["ATLAS_REST"],
                            "db": db}
            elif access == "annotator":
                db_creds = {"user": os.environ["ANNOTATOR_USER"],
                            "pass": os.environ["ANNOTATOR_PASSWORD"],
                            "rest": os.environ["ATLAS_REST"],
                            "db": db}

        uri = "mongodb://{user}:{pass}@{rest}".format(**db_creds)

    mongo_client = MongoClient(uri, connect=False)
    db = mongo_client[db_creds["db"]]
    return db


def open_es_client(user_creds=None, access="read_only"):
    if 'ELASTIC_HOST' in env:
        hosts = [env['ELASTIC_HOST']]
        http_auth = (env['ELASTIC_USER'], env['ELASTIC_PASS'])
        return Elasticsearch(hosts=hosts, http_auth=http_auth)
    else:
        if user_creds is not None:
            db_creds_filename = user_creds
        else:
            db_creds_filename = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), '_config.json')
        with open(db_creds_filename) as f:
            db_creds = json.load(f)

        hosts = db_creds["elastic"]["hosts"]
        http_auth = (db_creds["elastic"]["user"], db_creds["elastic"]["pass"])

    es_client = Elasticsearch(hosts=hosts, http_auth=http_auth, use_ssl=True, ca_certs=certifi.where())
    return es_client


