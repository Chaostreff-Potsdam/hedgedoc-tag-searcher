import re

import psycopg2
import yaml


class Hededoc(object):

    # Back in the CodiMD it was: '###### tags: `features` `cool` `updated`'
    legacy_tag_key = '###### tags:'
    notes_query = 'SELECT id, content, title, alias, shortid, "updatedAt" FROM "Notes" WHERE (permission IN %s) AND (length(content) > 0)'
    notes_since_clause = ' AND ("updatedAt" >= %s)'

    def __init__(self, config):
        self.conn = psycopg2.connect(
            dbname=config["HEDGEDOC_DATABASE"],
            user=config["HEDGEDOC_DB_USER"],
            password=config["HEDGEDOC_DB_PASS"],
            host=config["HEDGEDOC_DB_HOST"])
        self.permission_filter = config["PAD_PERMISSION_FILTER"]

    def get_notes_since(self, minimum_datetime=None):
        with self.conn.cursor() as cur:
            if minimum_datetime is None:
                cur.execute(self.notes_query + ";", (self.permission_filter, ))
            else:
                cur.execute(self.notes_query + self.notes_since_clause + ";", (self.permission_filter, minimum_datetime, ))
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
            return set()
        for line in text.split("\n"):
            if self.legacy_tag_key in line:
                res.extend(self.parse_legacy_tags(line))
        # HedgeDoc encourages YAML-Metadata _at the start_ of the document
        try:
            doc = next(yaml.load_all(text, Loader=yaml.Loader))
            res.extend(self.parse_yaml_tags(doc))
        except (StopIteration, yaml.error.YAMLError):
            pass
        return set(res)

