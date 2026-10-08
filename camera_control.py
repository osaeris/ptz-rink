from onvif import ONVIFCamera
import threading
import logging

logging.basicConfig(level=logging.INFO)


class PTZController:
    def __init__(self, name, ip, port, username, password, preset_map):
        self.name = name
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password
        self.preset_map = preset_map

        self.camera = ONVIFCamera(ip, port, username, password)
        self.media = self.camera.create_media_service()
        self.ptz = self.camera.create_ptz_service()
        self.profile = self.media.GetProfiles()[0]

    def goto_preset(self, preset_name):

        if preset_name not in self.preset_map:
            raise ValueError(
                f"Preset '{preset_name}' not defined for camera '{self.name}'"
            )

        preset_token = self.preset_map[preset_name]

        if not preset_token:
            raise ValueError(
                f"No preset token configured for '{preset_name}' on '{self.name}'"
            )

        logging.info(
            f"{self.name} ({self.ip}) -> "
            f"{preset_name} (token {preset_token})"
        )

        self.ptz.GotoPreset({
            "ProfileToken": self.profile.token,
            "PresetToken": preset_token
        })


def goto_preset_async(controller, preset_name):
    """Run PTZ move in a background thread so Flask never blocks."""

    thread = threading.Thread(
        target=controller.goto_preset,
        args=(preset_name,),
        daemon=True
    )

    thread.start()


def create_controller_from_config(config):
    return PTZController(
        name=config["name"],
        ip=config["ip"],
        port=config.get("port", 80),
        username=config["username"],
        password=config["password"],
        preset_map=config["presets"]
    )