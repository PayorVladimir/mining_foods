from flask import render_template, send_file, request
from flask_login import  login_required
from ..models import Terminal, Log, Client, Permission, Setting
from . import main
import pandas as pd
from io import BytesIO
import datetime
from datetime import date
from sqlalchemy import or_, Date, cast

#moderator web-page
@main.route("/", methods=["GET","POST"])
@login_required
def moderator():

    return render_template('index.html')


@main.route('/stats/terminal/<int:id>', methods=['GET'])
def terminal_stats_excel(id):


    terminal = Terminal.query.get_or_404(id)

    logs_total = Log.query.filter(Log.terminal_id == id)

    if  "date" in request.args:
        date_str = request.args.get("date")
        date = datetime.datetime.strptime(date_str, '%d-%m-%Y').date()
        logs_total = logs_total.filter(cast(Log.time_stamp, Date) == date)
    else:
        logs_total = logs_total.filter(cast(Log.time_stamp, Date) == date.today())


    #выполняем запрос

    logs = logs_total.all()

    json_data = [l.to_json() for l in logs]

    print(logs)

    df = pd.json_normalize(json_data)
    df = df.filter(['client_card', 'client_group_name', 'client_name', 'terminal_name', 'time_stamp'])
    df.columns = ['№ пропуска', 'Группа пользователей', 'ФИО', 'Терминал', 'Дата и время']

    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Выгрузка')
    writer.save()
    writer.save()
    output.seek(0)
    return send_file(output, attachment_filename='Выгрузка_{terminal}_{date}.xlsx'.format(terminal = terminal.description, date = datetime.datetime.now().strftime("%d_%m_%y") ), as_attachment=True)

@main.route("/stats", methods=["GET","POST"])
@login_required
def statistics():

    terminals = Terminal.query.all()

    res = []

    for terminal in terminals:
        if terminal.logs.count() >0:
            if Log.query.filter(cast(Log.time_stamp, Date) == date.today()).filter(Log.terminal_id == terminal.id).count() >0:
                res.append(terminal)


    return render_template('stats.html', terminals= res, today = datetime.datetime.now().date().strftime('%Y-%m-%d'))


@main.route("/terminals", methods=["GET","POST"])
@login_required
def terminals():

    return render_template('terminals.html')

@main.route("/groups", methods=["GET","POST"])
@login_required
def groups():

    return render_template('groups.html')
