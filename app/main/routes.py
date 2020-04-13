from flask import render_template
from flask_login import  login_required
from . import main


#moderator web-page
@main.route("/", methods=["GET","POST"])
@login_required
def moderator():

    return render_template('index.html')


@main.route("/terminals", methods=["GET","POST"])
@login_required
def terminals():

    return render_template('terminals.html')

@main.route("/groups", methods=["GET","POST"])
@login_required
def groups():

    return render_template('groups.html')
