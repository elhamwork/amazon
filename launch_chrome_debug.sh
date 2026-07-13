#!/bin/bash
# Launches Chrome with remote debugging enabled, using a dedicated
# profile folder so it doesn't collide with your normal Chrome windows.
# Log into Amazon, Keepa, and DataDive in THIS window once, and install
# + log into the Seller Amp and Helium 10 Chrome extensions -- the
# script will reuse that session/setup on every run.

DEBUG_PORT=9222
PROFILE_DIR="$HOME/chrome-fba-debug-profile"
CHROME_APP="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

if [ ! -f "$CHROME_APP" ]; then
    echo "Could not find Chrome at: $CHROME_APP"
    echo "Edit this script's CHROME_APP path if Chrome is installed elsewhere."
    exit 1
fi

"$CHROME_APP" --remote-debugging-port="$DEBUG_PORT" --user-data-dir="$PROFILE_DIR" &
