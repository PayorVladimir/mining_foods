from flask import jsonify, request, g, Response
from .. import db
from . import api
from ..models import Terminal, Log, Client
from .errors import forbidden, bad_request, not_found
from flask_login import current_user, login_user, logout_user, login_required
import datetime
from sqlalchemy import desc


@api.route('logs/', methods=['POST', 'GET'])
@login_required
def get_logs():
   client_id = request.args.get("client_id")
   terminal_id = request.args.get("terminal_id")
   logs = []

   if client_id is not None and client_id != "":
      client = Client.query.get_or_404(client_id)
      logs = client.logs

   if terminal_id is not None and terminal_id != "":
      terminal = Terminal.query.get_or_404(terminal_id)
      logs = terminal.logs

   rows= [log.to_json() for log in logs]
   rows.reverse()

   return jsonify({ "total": logs.count(),"rows": rows })