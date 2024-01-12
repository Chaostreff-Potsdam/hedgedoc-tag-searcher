from flask import Blueprint, render_template

from . import plzidx
from . import db

bp = Blueprint('views', __name__)

def remove_duplicates(seq):
	seen = set()
	return [x for x in seq if not (x in seen or seen.add(x))]

@bp.route('/<path:tag_path>', methods=['GET'])
@bp.route('/', defaults={'tag_path': ''}, methods=['GET'])
def pads_with_tags(tag_path):
	if not tag_path:
		return index()
	
	tag_text_list = remove_duplicates(filter(bool, tag_path.split('/')))
	if not tag_text_list:
		pads = []
	else:
		pads = sorted(db.Pad.get_by_taglist(tag_text_list), key=lambda p: p.title)

	return render_template('pads.html', pads=pads, tag_text_list=tag_text_list)

@bp.route('/', methods=['GET'])
def index():
	return render_template('index.html', common_tags=db.Tag.get_most_common())