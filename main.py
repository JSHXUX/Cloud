import json
import sqlite3
from http.server import BaseHTTPRequestHandler, HTTPServer


DB_FILE = "database.db"
TABLE_NAME = "bakugans"


def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                name TEXT PRIMARY KEY NOT NULL,
                attribute TEXT NOT NULL,
                gPower INTEGER NOT NULL
            )
        """
        )
        conn.commit()


class RequestHandler(BaseHTTPRequestHandler):


    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header("Content-type", "application/json")
        self.end_headers()


    def do_GET(self):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        route_args = self.path.strip("/").split("/")
        response = {"error": "Internal server error"}
        status = 500
        
        if len(route_args) == 2 and route_args[0] == "bakugan":
            name = str(route_args[1])
            cursor.execute(f"SELECT * FROM {TABLE_NAME} WHERE name = ?", (name,))
            row = cursor.fetchone()

            if row:
                response = {"name": row[0], "attribute": row[1], "gPower": row[2]}
                status = 200
            else:
                response = {"error": "Item not found"}
                status = 404

        elif len(route_args) == 1 and route_args[0] == "bakugan":
            cursor.execute(f"SELECT * FROM {TABLE_NAME}")
            rows = cursor.fetchall()

            response = [{"name": row[0], "attribute": row[1], "gPower": row[2]} for row in rows]
            status = 200

        else:
            response = {"error": "Bad request. Bad route"}
            status = 400

        conn.close()
        self._set_headers(status)
        self.wfile.write(json.dumps(response).encode())


    def do_POST(self):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        content_length = int(self.headers["Content-Length"])
        post_data = json.loads(self.rfile.read(content_length))

        route_args = self.path.strip("/").split("/")
        response = {"error": "Internal server error"}
        status = 500

        if len(route_args) == 1 and route_args[0] == "bakugan":
            if "name" not in post_data or "attribute" not in post_data or "gPower" not in post_data:
                response = {"error": "Bad request. Bad content"}
                status = 400
            else:
                name, attribute, gPower = post_data["name"], post_data["attribute"], post_data["gPower"]
                cursor.execute(f"SELECT * FROM {TABLE_NAME} WHERE name = ?", (name,))
                row = cursor.fetchone()

                if row:
                    response = {"error": "Conflict"}
                    status = 409
                else:
                    cursor.execute(f"INSERT INTO {TABLE_NAME} (name, attribute, gPower) VALUES (?, ?, ?)", (name, attribute, gPower))
                    conn.commit()
                    response = {"message": f"Created new bakugan {name}"}
                    status = 201

        elif len(route_args) == 2 and route_args[0] == "bakugan" and route_args[1] == "rare":
            if "name" not in post_data:
                response = {"error": "Bad request. Bad content"}
                status = 400
            else:
                name = post_data["name"]
                attribute = "Diamond"
                gPower = 1000
                cursor.execute(f"SELECT * FROM {TABLE_NAME} WHERE name = ?", (name,))
                row = cursor.fetchone()

                if row:
                    response = {"error": "Conflict"}
                    status = 409
                else:
                    cursor.execute(f"INSERT INTO {TABLE_NAME} (name, attribute, gPower) VALUES (?, ?, ?)", (name, attribute, gPower))
                    conn.commit()
                    response = {"message": f"Created new rare bakugan {name}"}
                    status = 201

        else:
            response = {"error": "Bad request. Bad route"}
            status = 400

        conn.close()
        self._set_headers(status)
        self.wfile.write(json.dumps(response).encode())


    def do_PUT(self):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        content_length = int(self.headers["Content-Length"])
        put_data = json.loads(self.rfile.read(content_length))

        route_args = self.path.strip("/").split("/")
        response = {"error": "Internal server error"}
        status = 500

        if len(route_args) == 2 and route_args[0] == "bakugan" and route_args[1] == "attribute":
            if "name" not in put_data or "attribute" not in put_data:
                response = {"error": "Bad request. Bad content"}
                status = 400
            else:
                name, attribute = put_data["name"], put_data["attribute"]
                cursor.execute(f"SELECT * FROM {TABLE_NAME} WHERE name = ?", (name,))
                row = cursor.fetchone()

                if row:
                    cursor.execute(f"UPDATE {TABLE_NAME} SET attribute = ? WHERE name = ?", (attribute, name))
                    conn.commit()
                    response = {"message": f"Updated attribute for bakugan {name}"}
                    status = 200
                else:
                    response = {"error": "Item not found"}
                    status = 404

        elif len(route_args) == 2 and route_args[0] == "bakugan" and route_args[1] == "gPower":
            if "name" not in put_data or "gPower" not in put_data:
                response = {"error": "Bad request. Bad content"}
                status = 400
            else:
                name, gPower = put_data["name"], put_data["gPower"]
                cursor.execute(f"SELECT * FROM {TABLE_NAME} WHERE name = ?", (name,))
                row = cursor.fetchone()

                if row:
                    cursor.execute(f"UPDATE {TABLE_NAME} SET gPower = ? WHERE name = ?", (gPower, name))
                    conn.commit()
                    response = {"message": f"Updated gPower for bakugan {name}"}
                    status = 200
                else:
                    response = {"error": "Item not found"}
                    status = 404

        else:
            response = {"error": "Bad request. Bad route"}
            status = 400

        conn.close()
        self._set_headers(status)
        self.wfile.write(json.dumps(response).encode())

    
    def do_DELETE(self):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        route_args = self.path.strip("/").split("/")
        response = {"error": "Internal server error"}
        status = 500
        
        if len(route_args) == 2 and route_args[0] == "bakugan":
            name = str(route_args[1])
            cursor.execute(f"SELECT * FROM {TABLE_NAME} WHERE name = ?", (name,))
            row = cursor.fetchone()

            if row:
                cursor.execute(f"DELETE FROM {TABLE_NAME} WHERE name = ?", (name,))
                conn.commit()
                response = {"message": f"Deleted bakugan {name}"}
                status = 200
            else:
                response = {"error": "Item not found"}
                status = 404

        elif len(route_args) == 1 and route_args[0] == "bakugan":
            response = {"error": "Method not allowed"}
            status = 405

        else:
            response = {"error": "Bad request. Bad route"}
            status = 400

        conn.close()
        self._set_headers(status)
        self.wfile.write(json.dumps(response).encode())


if __name__ == "__main__":
    init_db()
    server_address = ("", 8000)
    httpd = HTTPServer(server_address, RequestHandler)
    print("Starting server on port 8000...")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        httpd.server_close()