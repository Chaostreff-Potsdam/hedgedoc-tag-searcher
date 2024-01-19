import re

import psycopg2
import yaml

class Hededoc(object):

    # Back in the CodiMD it was: '###### tags: `features` `cool` `updated`'
    legacy_tag_key = '###### tags:'
    notes_query = 'SELECT id, content, title, alias, shortid, "updatedAt" FROM "Notes" WHERE (permission IN %s) AND (length(content) > 0)'
    notes_since_clause = ' AND ("updatedAt" >= %s)'

    note_content_query = 'SELECT content FROM "Notes" WHERE id = %s'
    note_update_content_stmt = 'UPDATE "Notes" SET content = %s WHERE id = %s'

    line_delim = "\n"
    yaml_delim = "---"

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
        for line in text.split(self.line_delim):
            if self.legacy_tag_key in line:
                res.extend(self.parse_legacy_tags(line))
        # HedgeDoc encourages YAML-Metadata _at the start_ of the document
        try:
            doc = next(yaml.load_all(text, Loader=yaml.Loader))
            res.extend(self.parse_yaml_tags(doc))
        except (StopIteration, yaml.error.YAMLError):
            pass
        return set(res)

    def get_pad_content(self, uuid):
        with self.conn.cursor() as cur:
            try:
                cur.execute(self.note_content_query, (uuid, ))
                return cur.fetchone()[0]
            except:
                return None
    
    def append_tag(self, uuid, tag, dry_run):
        content = self.get_pad_content(uuid)
        tagger = HedgedocTagger(content, tag)
        if tagger.try_add_tag():
            if not dry_run:
                with self.conn.cursor() as cur:
                    cur.execute(self.note_update_content_stmt, (tagger.new_text, uuid, ))
                    self.conn.commit()
            return tagger.new_text
        else:
            return None


class HedgedocTagger(object):

    line_delim = Hededoc.line_delim
    yaml_delim = Hededoc.yaml_delim
    legacy_tag_key = Hededoc.legacy_tag_key

    def __init__(self, text, tag):
        self.text = text
        self.tag = tag
        self.new_text = None
        self.has_added = False

    def _legacy_tag_iter(self):
        for line in self.text.split(self.line_delim):
            if not self.has_added and self.legacy_tag_key in line:
                newline_a, newline_b = line.split(self.legacy_tag_key, 1)
                yield "".join([newline_a, self.legacy_tag_key, f' `{self.tag}`', newline_b])
                self.has_added = True
            else:
                yield line

    def _try_add_legacy_tag(self):
        self.new_text = self.line_delim.join(self._legacy_tag_iter())
        return self.has_added

    def tagged_yaml_prefix(self, doc):
        doc["tags"] = ", ".join([self.tag] + list(filter(bool, map(str.strip, doc.get("tags", "").split(",")))))
        yamled_doc = yaml.dump(doc).rstrip(self.line_delim)
        return self.line_delim.join([self.yaml_delim, yamled_doc, self.yaml_delim])

    def _try_add_yaml_tag(self):
        yaml_line_delim = self.yaml_delim + self.line_delim
        rest_of_doc = self.text
        doc = {}
        if self.text.strip().startswith(yaml_line_delim):
            try:
                doc = next(yaml.load_all(self.text, Loader=yaml.Loader))
                if isinstance(doc, dict):
                    # Search for second yaml delim (supposedly at the end of the yaml doc)
                    rest_of_doc = self.text.split(self.line_delim + yaml_line_delim, 1)[1]
            except yaml.error.YAMLError:
               pass
        
        self.new_text = self.line_delim.join([self.tagged_yaml_prefix(doc), rest_of_doc])
        return True

    def try_add_tag(self):
        if not self.text:
            return False
        
        return self._try_add_legacy_tag() or self._try_add_yaml_tag()
