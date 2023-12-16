#!/usr/bin/env python

import psycopg2

import config

conn = psycopg2.connect(dbname=config.dbname, user=config.user, password=config.password, host=config.host)

if __name__ == "__main__":
    cur = conn.cursor()
    cur.execute('SELECT * FROM "Notes"')
    records = cur.fetchall()
    print(records)
