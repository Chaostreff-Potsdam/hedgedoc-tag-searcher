from flask import Blueprint, render_template

from . import plzidx

bp = Blueprint('views', __name__)

def remove_duplicates(seq):
	seen = set()
	return [x for x in seq if not (x in seen or seen.add(x))]

@bp.route('/pads/<path:tag_path>', methods=['GET'])
def pads_with_tags(tag_path):
	tag_text_list = remove_duplicates(filter(bool, tag_path.split('/')))
	related_tags, pads = plzidx.most_common_tags_and_pads(tag_text_list)

	return render_template('pads.html', related_tags=related_tags, pads=pads, tag_text_list=tag_text_list)

@bp.route('/pads/', methods=['GET'])
@bp.route('/')
def index():
	return render_template('index.html', common_tags=plzidx.most_common())