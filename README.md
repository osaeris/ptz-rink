# PTZ Hockey Rink Controller

A Raspberry Pi–hosted web application for controlling ONVIF PTZ camera presets
using a touch-friendly SVG hockey rink interface.


## Features
- SVG rink with faceoff-zone controls
- ONVIF PTZ preset triggering
- Dockerized (Python 3.11)
- Persistent camera configuration
- Settings UI
- Raspberry Pi friendly

## Requirements
- Raspberry Pi 4
- Docker
- ONVIF-compatible PTZ camera

## Quick Start

```bash
git clone https://github.com/osaeris/ptz-rink
cd ptz-rink
cp config/camera.example.json config/camera.json
docker build -t ptz-rink .
docker run -d \
  -p 5001:5001 \
  -v $(pwd)/config:/app/config \
  --restart unless-stopped \
  ptz-rink

Open:
http://<pi-ip>:5001
Notes

    The application will create `config/camera.json` automatically on first run.
    You dont need to make any changes to the file, just go to the settings cog to set
    up your camera. http://<pi-ip>:5001/settings
    A sample structure is provided in `config/camera.example.json` for reference.

    Camera presets must already exist on the camera

    This project is intended for LAN use

FUTURE DEVELOPMENTS

* Add more cameras
* Add neutral zone drop areas
