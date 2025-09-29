# WARNING: This file is intentionally vulnerable for CI demo purposes only.
# Do NOT use in production.

from flask import Flask, request, jsonify
import subprocess   # INSECURE demo (Bandit: B602/B607)
import hashlib      # INSECURE demo (Bandit: B303 for md5)
import pickle       # INSECURE demo (Bandit: B301)
import base64
import yaml         # INSECURE demo (Bandit: B506)

app = Flask(__name__)

@app.route("/")
def index():
    return "Hello PSU Students from Jenkins! (demo: intentionally vulnerable)"

# ---- HIGH: eval on user input (Bandit B307) ----
@app.route("/eval")
def eval_expr():
    expr = request.args.get("expr", "1+1")
    # INSECURE: arbitrary code execution
    result = eval(expr)  # nosec  B307 (keep for demo)
    return jsonify({"expr": expr, "result": result})

# ---- HIGH: shell=True in subprocess (Bandit B602/B607) ----
@app.route("/ping")
def ping():
    host = request.args.get("host", "127.0.0.1")
    cmd = f"ping -c 1 {host}"
    # INSECURE: command injection
    rc = subprocess.call(cmd, shell=True)  # nosec  B602,B607 (keep for demo)
    return jsonify({"cmd": cmd, "return_code": rc})

# ---- Medium/High: weak hash (Bandit B303) ----
@app.route("/md5")
def weak_hash():
    text = request.args.get("text", "demo")
    digest = hashlib.md5(text.encode()).hexdigest()  # nosec B303 (keep for demo)
    return jsonify({"algo": "md5", "text": text, "digest": digest})

# ---- HIGH: unsafe pickle (Bandit B301) ----
@app.route("/unpickle", methods=["POST"])
def unpickle_data():
    b64 = request.get_data(as_text=True)
    try:
        data = pickle.loads(base64.b64decode(b64))  # nosec B301 (keep for demo)
        return jsonify({"status": "ok", "data": str(data)})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

# ---- HIGH: yaml.load without SafeLoader (Bandit B506) ----
@app.route("/yaml", methods=["POST"])
def yaml_load():
    content = request.get_data(as_text=True)
    obj = yaml.load(content, Loader=yaml.Loader)  # nosec B506 (keep for demo)
    return jsonify({"loaded": obj})

# ---- Demo: hardcoded secret (Bandit B105) ----
HARDCODED_PASSWORD = "P@ssw0rd123"  # nosec B105 (keep for demo)

@app.route("/login", methods=["POST"])
def login():
    pw = request.form.get("password", "")
    ok = (pw == HARDCODED_PASSWORD)
    return jsonify({"ok": ok})

if __name__ == "__main__":
    # Flask debug True (Bandit B201) – deliberately enabled for demo
    app.run(host="0.0.0.0", port=5000, debug=True)
