from onvif import ONVIFCamera
import threading
import logging

logging.basicConfig(level=logging.INFO)

class PTZController:
    def __init__(self, ip, port, username, password, preset_map):
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password
        self.preset_map = preset_map

        self.camera = ONVIFCamera(ip, port, username, password)
        self.media = self.camera.create_media_service()
        self.ptz = self.camera.create_ptz_service()
        self.profile = self.media.GetProfiles()[0]

    def goto_preset(self, preset_id):
        if preset_id not in self.preset_map:
            raise ValueError(f"Preset {preset_id} not defined")

        preset_token = self.preset_map[preset_id]

        logging.info(
            f"Camera {self.ip}: GotoPreset {preset_id} (token {preset_token})"
        )

        self.ptz.GotoPreset({
            "ProfileToken": self.profile.token,
            "PresetToken": preset_token
        })


def goto_preset_async(controller, preset_id):
    """Run PTZ move in a background thread so Flask never blocks"""
    thread = threading.Thread(
        target=controller.goto_preset,
        args=(preset_id,),
        daemon=True
    )
    thread.start()

def create_controller_from_config(config):
    return PTZController(
        ip=config["ip"],
        port=config.get("port", 80),
        username=config["username"],
        password=config["password"],
        preset_map={int(k): v for k, v in config["presets"].items()}
    )
