import subprocess
import shlex
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)
SOUNDNESS_CLI_PATH = "/root/.soundness/bin/soundness-cli"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate-key', methods=['POST'])
def generate_key():
    name = request.form.get('name')
    password = request.form.get('password')
    if not name or not password:
        return jsonify({"error": "Name and password required"}), 400

    cmd = f"""expect -c '
spawn {SOUNDNESS_CLI_PATH} generate-key --name {shlex.quote(name)}
expect "Enter password"
send "{password}\\r"
expect "Confirm password"
send "{password}\\r"
expect eof
'"""
    output = subprocess.getoutput(cmd)
    return jsonify({"output": output})

@app.route('/import-key', methods=['POST'])
def import_key():
    name = request.form.get('name')
    mnemonic = request.form.get('mnemonic')
    password = request.form.get('password')
    if not name or not mnemonic or not password:
        return jsonify({"error": "Name, mnemonic and password required"}), 400

    cmd = f"""expect -c '
spawn {SOUNDNESS_CLI_PATH} import-key --name {shlex.quote(name)} --mnemonic {shlex.quote(mnemonic)}
expect "Enter password"
send "{password}\\r"
expect "Confirm password"
send "{password}\\r"
expect eof
'"""
    output = subprocess.getoutput(cmd)
    return jsonify({"output": output})

@app.route('/list-keys', methods=['GET'])
def list_keys():
    output = subprocess.getoutput(f"{SOUNDNESS_CLI_PATH} list-keys")
    return jsonify({"output": output})

@app.route('/send-proof', methods=['POST'])
def send_proof():
    password = request.form.get('password')
    raw_command = request.form.get('command')

    if not password or not raw_command:
        return jsonify({"error": "Password and command required"}), 400

    # Hilangkan prefix 'soundness-cli' atau 'soundness-cli ' jika ada
    if raw_command.strip().startswith("soundness-cli"):
        raw_command = raw_command.strip().replace("soundness-cli", "", 1).strip()

    # Split dan quote ulang agar payload JSON tetap aman
    try:
        safe_command_parts = shlex.split(raw_command)
        quoted_command = " ".join(shlex.quote(arg) for arg in safe_command_parts)
    except Exception as e:
        return jsonify({"error": f"Failed to parse command: {str(e)}"}), 400

    # Buat dan jalankan expect script
    expect_script = f"""expect -c '
spawn {SOUNDNESS_CLI_PATH} {quoted_command}
expect "Enter password"
send "{password}\\r"
expect eof
'"""

    output = subprocess.getoutput(expect_script)
    return jsonify({"output": output})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
