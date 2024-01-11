from flask import Blueprint, render_template

import plzidx

bp = Blueprint('dashboard', __name__)

@bp.route('/<starttag>', methods=('GET', 'POST'))
def index(starttag):
	return "Most common tags with '" + starttag + "': " + plzidx.plzidx.most_common_tags(starttag)
    #return render_template('dashboard.html')