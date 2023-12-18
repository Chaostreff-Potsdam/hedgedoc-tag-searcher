import re

import psycopg2
import yaml


class Hededoc(object):

    # Back in the CodiMD it was: '###### tags: `features` `cool` `updated`'
    legacy_tag_key = '###### tags:'
    notes_since_query = 'SELECT id, content, "updatedAt" FROM "Notes" WHERE "updatedAt" >= %s;'
    notes_query = 'SELECT id, content, "updatedAt" FROM "Notes";'

    def __init__(self, config):
        self.conn = psycopg2.connect(
            dbname=config["HEDGEDOC_DATABASE"],
            user=config["HEDGEDOC_DB_USER"],
            password=config["HEDGEDOC_DB_PASS"],
            host=config["HEDGEDOC_DB_HOST"])

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
            return set()
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
           
    def get_pad_field(self, uuid, field):
        with self.conn.cursor() as cur:
            try:
                cur.execute(f'SELECT {field} FROM "Notes" WHERE id = %s', (uuid, ))
                return cur.fetchone()[0]
            except:
                return None
    
    def get_pad_title(self, uuid):
        return self.get_pad_field(uuid, "title")