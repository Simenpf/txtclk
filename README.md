# txtclk
A clock displaying time with text.


## First time setup on a pi`
### Install uv and sync
```
curl -LsSf https://astral.sh/uv/install.sh | sh`
cd /opt/txtclk
uv sync
```
### Install service running webserver and logic
```
deploy/install.sh
deploy/install-kiosk.sh
```
Then run `sudo raspi-config` and select desktop autologin in boot options, then reboot
