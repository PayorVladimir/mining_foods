from flask import jsonify, request, g, Response
from .. import db
from . import api
from ..models import Terminal, Log, Client
from .errors import forbidden, bad_request, not_found
from flask_login import current_user, login_user, logout_user, login_required
import datetime
from datetime import timedelta
from sqlalchemy import or_, Date, cast, desc

@api.route('logs/', methods=['POST', 'GET'])
@login_required
def get_logs():
   page = request.form["page"]
   rows = request.form["rows"]
   query = None
   logs = []

   # общий запрос  логов

   if "query" in request.form:
      query = request.form["query"]

   if query is not None and query != "":

      logs = Log.query.filter(
          or_(Log.terminal_name.like("%{}%".format(query)), (Log.info.like("%{}%".format(query))), (Log.client_card.like("%{}%".format(query))), (Log.client_name.like("%{}%".format(query))))).paginate(
            page=int(page), error_out=False, per_page=int(rows)).items
   else:
      logs = Log.query.paginate(page=int(page), error_out=False, per_page=int(rows)).items

   #запрос логов для терминала или пользователя

   client_id = request.args.get("client_id")
   terminal_id = request.args.get("terminal_id")


   if client_id is not None and client_id != "":
      client = Client.query.get_or_404(client_id)
      logs = client.logs

   if terminal_id is not None and terminal_id != "":
      terminal = Terminal.query.get_or_404(terminal_id)
      logs = terminal.logs

   rows= [log.to_json() for log in logs]


   return jsonify({ "total": len(Log.query.all()) ,"rows": list(reversed(rows)) })


@api.route('stats/', methods=[ 'GET'])
@login_required
def get_stats():
   daily_usage = []
   for days_to_subtract in range (0, 7):
      date_usage = datetime.datetime.today() - timedelta(days=days_to_subtract)

      daily_usage.append(Log.query.filter(cast(Log.time_stamp, Date) == date_usage.date()).count())




   return jsonify({"total": len(daily_usage), "rows": list(reversed(daily_usage)) })

