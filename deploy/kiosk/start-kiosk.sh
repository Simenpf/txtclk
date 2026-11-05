
#!/bin/bash
set -e

URL="http://127.0.0.1:8000/display"

# Wait for FastAPI to become available
until curl -fsS "$URL" >/dev/null; do
    sleep 2
done

exec chromium \
    --ozone-platform=wayland \
    --password-store=basic \
    --kiosk \
    --noerrdialogs \
    --disable-infobars \
    --no-first-run \
    --disable-session-crashed-bubble \
    "$URL"
