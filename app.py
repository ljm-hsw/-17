from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

DB_PATH = os.path.join(os.path.dirname(__file__), 'data.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS bindings (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT NOT NULL, rfid_uid TEXT NOT NULL UNIQUE, bind_time TEXT NOT NULL)")
    c.execute("CREATE TABLE IF NOT EXISTS checkins (id INTEGER PRIMARY KEY AUTOINCREMENT, rfid_uid TEXT NOT NULL, spot_name TEXT NOT NULL, card_uid TEXT, time TEXT NOT NULL)")
    conn.commit()
    conn.close()

@app.route('/api/bind', methods=['POST'])
def bind():
    data = request.get_json(force=True, silent=True) or {}
    user_id = data.get('user_id', '')
    rfid_uid = data.get('rfid_uid', '')
    if not user_id or not rfid_uid:
        return jsonify({'status': 'error', 'message': 'missing params'}), 400
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO bindings (user_id, rfid_uid, bind_time) VALUES (?, ?, ?)",
                  (user_id, rfid_uid, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()
        conn.close()
        return jsonify({'status': 'success', 'message': 'bind ok'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/get_route/<uid>', methods=['GET'])
def get_route(uid):
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT spot_name, card_uid, time FROM checkins WHERE rfid_uid = ? ORDER BY time DESC", (uid,))
        rows = c.fetchall()
        conn.close()
        result = [{'spot_name': r['spot_name'], 'card_uid': r['card_uid'] or uid, 'time': r['time']} for r in rows]
        return jsonify({'status': 'success', 'data': result})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/checkin', methods=['POST'])
def checkin():
    data = request.get_json(force=True, silent=True) or {}
    rfid_uid = data.get('rfid_uid') or data.get('card_uid') or ''
    spot_name = data.get('spot_name', '')
    device_id = data.get('device_id', '')
    if not rfid_uid or not spot_name:
        return jsonify({'status': 'error', 'message': 'missing rfid_uid/card_uid or spot_name'}), 400
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute("INSERT INTO checkins (rfid_uid, spot_name, card_uid, time) VALUES (?, ?, ?, ?)",
                  (rfid_uid, spot_name, rfid_uid, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()
        conn.close()
        return jsonify({'status': 'success', 'message': 'checkin ok', 'device_id': device_id})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/', methods=['GET'])
def index():
    return jsonify({'status': 'ok', 'message': 'wlv backend running'})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=8000, debug=False)
