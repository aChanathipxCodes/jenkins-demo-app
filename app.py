# WARNING: Intentionally vulnerable for CI demo only.

from flask import Flask, request, jsonify
import subprocess      # INSECURE (Bandit B602/B607)
import hashlib         # INSECURE md5 (B303)
import pickle          # INSECURE (B301)
import base64
import yaml            # INSECURE yaml.load (B506)

app = Flask(__name__)

@app.route("/")
def index():
    return "Hello PSU Students from Jenkins! (demo: intentionally vulnerable)"

# ---- HIGH: eval on user input (B307) ----
@app.route("/eval")
def eval_expr():
    expr = request.args.get("expr", "1+1")
    result = eval(expr)  # nosec - keep for demo
    return jsonify({"expr": expr, "result": result})

# ---- HIGH: shell=True (B602/B607) ----
@app.route("/ping")
def ping():
    host = request.args.get("host", "127.0.0.1")
    cmd = f"ping -c 1 {host}"
    rc = subprocess.call(cmd, shell=True)  # nosec - keep for demo
    return jsonify({"cmd": cmd, "return_code": rc})

# ---- MEDIUM: weak hash (B303) ----
@app.route("/md5")
def weak_hash():
    text = request.args.get("text", "demo")
    digest = hashlib.md5(text.encode()).hexdigest()  # nosec - keep for demo
    return jsonify({"algo": "md5", "text": text, "digest": digest})

# ---- HIGH: unsafe pickle (B301) ----
@app.route("/unpickle", methods=["POST"])
def unpickle_data():
    b64 = request.get_data(as_text=True)
    data = pickle.loads(base64.b64decode(b64))  # nosec - keep for demo
    return jsonify({"status": "ok", "data": str(data)})

# ---- HIGH: yaml.load without SafeLoader (B506) ----
@app.route("/yaml", methods=["POST"])
def yaml_load():
    content = request.get_data(as_text=True)
    obj = yaml.load(content, Loader=yaml.Loader)  # nosec - keep for demo
    return jsonify({"loaded": obj})

# ---- LOW: hardcoded secret (B105) ----
HARDCODED_PASSWORD = "P@ssw0rd123"  # nosec - keep for demo

@app.route("/login", methods=["POST"])
def login():
    return jsonify({"ok": request.form.get("password") == HARDCODED_PASSWORD})

if __name__ == "__main__":
    # HIGH: debug=True (B201)
    app.run(host="0.0.0.0", port=5000, debug=True)
