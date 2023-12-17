#!/usr/bin/env python

import datetime
import re

import psycopg2
import yaml

import config


class HededocDB(object):

    # Back in the CodiMD it was: '###### tags: `features` `cool` `updated`'
    legacy_tag_key = '###### tags:'
    notes_since_query = 'SELECT id, title, shortid, content, "updatedAt" FROM "Notes" WHERE "updatedAt" >= %s;'
    notes_query = 'SELECT id, title, shortid, content, "updatedAt" FROM "Notes";'

    def __init__(self):
        self.conn = psycopg2.connect(dbname=config.dbname, user=config.user, password=config.password, host=config.host)

    def get_notes_since(self, minimum_datetime=None):
        with self.conn.cursor() as cur:
            if minimum_datetime is None:
                cur.execute(self.notes_query)
            else:
                cur.execute(self.notes_since_query, (minimum_datetime, ))
            return cur.fetchall()

    def parse_yaml_tags(self, document):
        if not isinstance(document, dict):
            return []
        return filter(bool, map(str.strip, document.get("tags", "").split(",")))

    def parse_legacy_tags(self, line):
        tags_part = line.split(self.legacy_tag_key)[1]
        return re.findall(r'`([^`]+)`', tags_part)

    def extract_tags(self, text):
        res = []
        # In CodiMD we used # and backticks
        if not text:
            return res
        for line in text.split("\n"):
            if self.legacy_tag_key in line:
                res.extend(self.parse_legacy_tags(line))
        # HedgeDoc encourages YAML-Metadata
        try:
            for doc in yaml.load_all(text, Loader=yaml.Loader):
                if (tags := self.parse_yaml_tags(doc)):
                    res.extend(tags)
        except yaml.error.YAMLError:
            pass
        return set(res)

    def __del__(self):
        self.conn.close()


def test():
    db = HededocDB()
    given_datetime = datetime.datetime(1970, 1, 1, 0, 0, 0)
    for idx, title, shortid, content, updatedAt in db.get_notes_since(given_datetime):
        tags = db.extract_tags(content)
        if tags:
            print(idx, shortid, title, tags)


if __name__ == "__main__":
    test()
