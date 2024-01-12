from flask import Blueprint, render_template

import plzidx

bp = Blueprint('dashboard', __name__)

@bp.route('/pads/<path:tag_path>', methods=['GET'])
@bp.route('/pads/', defaults={'tag_path': ''}, methods=['GET'])
def pads_with_tags(tag_path):
	tags = list(filter(bool, tag_path.split('/')))
	return plzidx.plzidx.most_common_tags(tags)