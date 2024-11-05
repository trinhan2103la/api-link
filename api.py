from flask import Flask, jsonify, make_response, request, make_response  # type: ignore
from flask_cors import CORS  # type: ignore
import sqlite3

app = Flask(__name__)

db_path = r"C:\Users\ASUS\Documents\Zalo Received Files\SQLiteDatabaseBrowserPortable\listIP.db"
CORS(app)

def get_ping_results_by_ip_type(ip_type):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT ip_type, id_may, status, result, datetime, uptime_start
            FROM pingResults_new
            WHERE ip_type = ?  -- Changed placeholder from id_may to ip_type
            ORDER BY datetime DESC, uptime_start DESC
        """, (ip_type,))  # Added tuple for parameter binding
    
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            result = {
                "ip_type": row[0],
                "id_may": row[1],
                "status": row[2],
                "result": row[3],
                "datetime": row[4],
                "uptime_start": row[5],
            }
            results.append(result)
        
        return {"status": True, "message": f"Data of {ip_type} retrieved successfully", "data": results}
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return {"status": False, "message": "Failed to retrieve results", "data": []}

def get_all_ping_results():
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT ip_type, id_may, status, result, datetime, uptime_start
            FROM pingResults_new
            ORDER BY datetime DESC, uptime_start DESC
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            result = {
                "ip_type": row[0],
                "id_may": row[1],
                "status": row[2],
                "result": row[3],
                "datetime": row[4],
                "uptime_start": row[5],
            }
            results.append(result)
        
        return {"status": True, "message": "Results retrieved successfully", "data": results}
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return {"status": False, "message": "Failed to retrieve results", "data": []}

def get_time_down_ping_ip():
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT ip, ip_type, start_time, end_time
            FROM downtime_records
            ORDER BY start_time DESC, end_time DESC
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            result = {
                "ip": row[0],
                "ip_type": row[1],
                "start_time": row[2],
                "end_time": row[3]
            }
            results.append(result)
        
        return {"status": True, "message": "Results retrieved successfully", "data": results}
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return {"status": False, "message": "Failed to retrieve results", "data": []}


@app.route('/api/<ip_type>', methods=['GET'])
def api_get_ping_results_by_ip_type(ip_type):
    results = get_ping_results_by_ip_type(ip_type)
    if not results["status"]:
        return make_response(jsonify(results), 500)
    return jsonify(results)

@app.route('/api/downtime-records', methods=['GET'])
def get_time_down():
    results = get_time_down_ping_ip()
    if not results["status"]:
        return make_response(jsonify(results), 500)
    return jsonify(results)

@app.route('/', methods=['GET'])
def api_get_all_ping_results():
    results = get_all_ping_results()
    if not results["status"]:
        return make_response(jsonify(results), 500)
    return jsonify(results)


def execute_query(query, args=(), fetch=False):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        print(args)
        print(query)
        cursor.execute(query, args)
        if fetch:
            results = cursor.fetchall()
            conn.close()
            return results
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False

def get_list_ip():
    query = "SELECT TYPE, IP FROM IP"
    rows = execute_query(query, fetch=True)
    if rows is not False:
        results = [{"TYPE": row[0], "IP": row[1]} for row in rows]
        return {"status": True, "message": "Results retrieved successfully", "data": results}
    return {"status": False, "message": "Failed to retrieve results", "data": []}

def add_ip(data):
    query = "INSERT INTO IP (TYPE, IP) VALUES (?, ?)"
    success = execute_query(query, (data['type'], data['ip']))
    if success:
        return {"status": True, "message": "IP added successfully"}
    return {"status": False, "message": "Failed to add IP"}


def delete_ip(data):
    query = "DELETE FROM IP WHERE IP = ?"
    success = execute_query(query, (data['ip'],))
    if success:
        return {"status": True, "message": "IP deleted successfully"}
    return {"status": False, "message": "Failed to delete IP"}

@app.route('/api/list', methods=['GET'])
def api_get_list_ip():
    results = get_list_ip()
    if not results["status"]:
        return make_response(jsonify(results), 500)
    return jsonify(results)

@app.route('/api/list', methods=['POST'])
def api_add_ip():
    data = request.json
    result = add_ip(data)
    if not result["status"]:
        return make_response(jsonify(result), 500)
    return jsonify(result)



@app.route('/api/list', methods=['DELETE'])
def api_delete_ip():
    data = request.json
    result = delete_ip(data)
    if not result["status"]:
        return make_response(jsonify(result), 500)
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True, ssl_context='adhoc', port='8080')