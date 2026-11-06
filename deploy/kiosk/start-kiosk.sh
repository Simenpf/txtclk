
#!/bin/bash
set -e

URL="http://127.0.0.1:8000/display"

# Wait for FastAPI
until curl -fsS "$URL" >/dev/null; do
    sleep 2
done

sleep 5

exec chromium \
    --ozone-platform=wayland \
    --password-store=basic \
    --user-data-dir=/home/sflotake/.config/txtclk-chromium \
    --kiosk \
    --noerrdialogs \
    --disable-infobars \
    --no-first-run \
    --disable-session-crashed-bubble \
    "$URL"
