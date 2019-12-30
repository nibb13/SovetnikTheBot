#!/bin/sh

BOT_TOKEN="<YOUR BOT TOKEN HERE>"
HOOK_URL="https://yourdomain.com/sovetnik.cgi?token=$BOT_TOKEN"

curl "https://api.telegram.org/bot$BOT_TOKEN/setWebhook?url=$HOOK_URL"
