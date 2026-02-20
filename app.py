from flask import Flask, render_template, jsonify, request, redirect, url_for
import json
import os
import traceback
from camera_control import create_controller_from_config, goto_preset_async


DEFAULT_CONFIG = {
    "ip": "192.168.1.231",
    "port": 80,
    "username": "admin",
    "password": "password",
    "presets": {
        "1": "1",
        "2": "2",
        "3": "3",
        "4": "4",
        "5": "5"
    }
}

CONFIG_PATH = "config/camera.json"
CAMERA_1 = None
CAMERA_STATUS = {
    "ok": False,
    "error": None
}

app = Flask(__name__)

def ensure_config_exists():
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)

    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)

def load_camera():
    global CAMERA_1, CAMERA_STATUS

    try:

        ensure_config_exists()

        with open(CONFIG_PATH) as f:
            config = json.load(f)

        CAMERA_1 = create_controller_from_config(config)

        CAMERA_STATUS["ok"] = True
        CAMERA_STATUS["error"] = None

        app.logger.info("Camera connected successfully")

    except Exception as e:
        CAMERA_1 = None
        CAMERA_STATUS["ok"] = False
        CAMERA_STATUS["error"] = str(e)

        app.logger.error("Camera connection failed")
        app.logger.error(traceback.format_exc())



# =========================
# ROUTES
# =========================

@app.route("/")
def index():
    return render_template("index.html")



@app.route("/camera/1/preset/<int:preset_id>", methods=["POST"])
def camera_1_preset(preset_id):
    if not CAMERA_1:
        return jsonify({
            "status": "error",
            "message": "Camera not connected"
        }), 503

    try:
        goto_preset_async(CAMERA_1, preset_id)
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500




@app.route("/settings", methods=["GET", "POST"])
def settings():
    ensure_config_exists()

    if request.method == "POST":
        new_config = {
            "ip": request.form["ip"],
            "port": int(request.form["port"]),
            "username": request.form["username"],
            "password": request.form["password"],
            "presets": {
                "1": "1",
                "2": "2",
                "3": "3",
                "4": "4",
                "5": "5"
            }
        }

        with open(CONFIG_PATH, "w") as f:
            json.dump(new_config, f, indent=2)

        # 🔑 Try to reload camera, but NEVER fail the request
        load_camera()

        return redirect(url_for("settings"))

    with open(CONFIG_PATH) as f:
        config = json.load(f)

    return render_template(
        "settings.html",
        config=config,
        camera_status=CAMERA_STATUS
    )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5001,
        debug=True
    )


