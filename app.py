from flask import Flask, render_template, jsonify, request, redirect, url_for
import json
import os
import traceback
import time
from camera_control import create_controller_from_config, goto_preset_async

DEFAULT_CONFIG = {
  "version": 2,
  "trigger_delay_ms": 200,
  "preset_order": [
    "startup",
    "left_top",
    "left_bottom",
    "centre",
    "right_top",
    "right_bottom",
    "dead_zone_left",
    "dead_zone_right",
    "sinbin",
    "home_bench",
    "away_bench",
    "goal_left",
    "goal_right",
    "mom"
  ],
  "cameras": [
    {
      "enabled": False,
      "name": "Zone L",
      "ip": "192.168.0.111",
      "port": 80,
      "username": "admin",
      "password": "admin",
      "presets": {
        "startup": "0",
        "left_top": "1",
        "left_bottom": "2",
        "centre": "3",
        "right_top": "4",
        "right_bottom": "5",
        "dead_zone_left": "6",
        "dead_zone_right": "6",
        "sinbin": "7",
        "home_bench": "8",
        "away_bench": "9",
        "goal_left": "",
        "goal_right": "",
        "mom": ""
      }
    },
    {
      "enabled": False,
      "name": "Zone R",
      "ip": "192.168.0.112",
      "port": 80,
      "username": "admin",
      "password": "admin",
      "presets": {
        "startup": "0",
        "left_top": "1",
        "left_bottom": "2",
        "centre": "3",
        "right_top": "4",
        "right_bottom": "5",
        "dead_zone_left": "6",
        "dead_zone_right": "6",
        "sinbin": "7",
        "home_bench": "8",
        "away_bench": "9",
        "goal_left": "",
        "goal_right": "",
        "mom": ""
      }
    },
    {
      "enabled": False,
      "name": "Center",
      "ip": "192.168.0.113",
      "port": 80,
      "username": "admin",
      "password": "admin",
      "presets": {
        "startup": "0",
        "left_top": "1",
        "left_bottom": "2",
        "centre": "3",
        "right_top": "4",
        "right_bottom": "5",
        "dead_zone_left": "6",
        "dead_zone_right": "6",
        "sinbin": "7",
        "home_bench": "8",
        "away_bench": "9",
        "goal_left": "",
        "goal_right": "",
        "mom": ""
      }
    },
    {
      "enabled": False,
      "name": "Wide",
      "ip": "192.168.0.115",
      "port": 80,
      "username": "admin",
      "password": "admin",
      "presets": {
        "startup": "0",
        "left_top": "1",
        "left_bottom": "2",
        "centre": "3",
        "right_top": "4",
        "right_bottom": "5",
        "dead_zone_left": "6",
        "dead_zone_right": "6",
        "sinbin": "7",
        "home_bench": "8",
        "away_bench": "9",
        "goal_left": "",
        "goal_right": "",
        "mom": ""
      }
    }
  ]
}

DEVELOPMENT_MODE = False

CONFIG_PATH = "config/camera.json"

CAMERAS = []
CAMERA_STATUS = []

with open(CONFIG_PATH) as f:
    config = json.load(f)
    delay = config.get("trigger_delay_ms",100)/1000  

app = Flask(__name__)

def ensure_config_exists():
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)

    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)

def load_cameras():
    global CAMERAS, CAMERA_STATUS

    CAMERAS = []
    CAMERA_STATUS = []

    ensure_config_exists()

    with open(CONFIG_PATH) as f:
        config = json.load(f)

    for camera_cfg in config["cameras"]:

        status = {
            "name": camera_cfg["name"] or "Unnamed Camera",
            "enabled": camera_cfg["enabled"],
            "online": False,
            "error": None
        }

        if not camera_cfg["enabled"]:
            CAMERA_STATUS.append(status)
            continue

        try:
            controller = create_controller_from_config(camera_cfg)

            CAMERAS.append(controller)

            status["online"] = True

        except Exception as e:
            status["error"] = str(e)

        CAMERA_STATUS.append(status)

    app.logger.info(f"Loaded {len(CAMERAS)} camera(s)")


# =========================
# ROUTES
# =========================

@app.route("/")
def index():
    return render_template(
        "index.html",
        camera_status=CAMERA_STATUS
    )



@app.route("/preset/<preset_name>", methods=["POST"])
def trigger_preset(preset_name):

    if not CAMERAS:
        return jsonify({
            "status": "error",
            "message": "No cameras are configured or connected."
        }), 503

    triggered = []
    skipped = []

    for camera in CAMERAS:
        try:
            goto_preset_async(camera, preset_name)
            triggered.append(camera.name)
            # Wait 100 ms before triggering the next camera
            time.sleep(delay)

        except Exception as e:
            skipped.append({
                "camera": camera.name,
                "error": str(e)
            })

    return jsonify({
        "status": "ok",
        "preset": preset_name,
        "triggered": triggered,
        "skipped": skipped
    })



@app.route("/settings", methods=["GET", "POST"])
def settings():

    ensure_config_exists()

    if request.method == "POST":

        # Read the existing config so we preserve version/preset_order
        with open(CONFIG_PATH) as f:
            current = json.load(f)

        new_config = {
            "version": current.get("version", 2),
            "trigger_delay_ms": int(request.form.get("trigger_delay_ms") or 100),
            "preset_order": current["preset_order"],
            "cameras": []
        }

        for i in range(len(current["cameras"])):

            camera = {
                "enabled": f"camera_{i}_enabled" in request.form,
                "name": request.form.get(f"camera_{i}_name", ""),
                "ip": request.form.get(f"camera_{i}_ip", ""),
                "port": int(request.form.get(f"camera_{i}_port", 80)),
                "username": request.form.get(f"camera_{i}_username", ""),
                "password": request.form.get(f"camera_{i}_password", ""),
                "presets": {}
            }

            for preset in current["preset_order"]:
                camera["presets"][preset] = request.form.get(
                    f"camera_{i}_{preset}",
                    ""
                )

            new_config["cameras"].append(camera)

        with open(CONFIG_PATH, "w") as f:
            json.dump(new_config, f, indent=2)

        load_cameras()

        return redirect(url_for("settings"))

    # GET request
    with open(CONFIG_PATH) as f:
        config = json.load(f)

    return render_template(
        "settings.html",
        config=config,
        camera_status=CAMERA_STATUS
    )

@app.route("/test-camera/<int:index>", methods=["POST"])
def test_camera(index):

    ensure_config_exists()

    with open(CONFIG_PATH) as f:
        config = json.load(f)

    try:

        create_controller_from_config(
            config["cameras"][index]
        )

        return jsonify({
            "status": "ok"
        })

    except Exception as e:

        message = str(e)

        if "401" in message:
            message = "Authentication failed"

        elif "Connection refused" in message:
            message = "Camera not reachable"

        elif "timed out" in message:
            message = "Connection timed out"

        elif "Failed to establish a new connection" in message:
            message = "Camera not reachable"

        return jsonify({
            "status":"error",
            "message":message
        })

if not DEVELOPMENT_MODE:
    try:
        load_cameras()
    except Exception as e:
        app.logger.error(f"Failed to load cameras: {e}")

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5001,
        debug=True
    )


