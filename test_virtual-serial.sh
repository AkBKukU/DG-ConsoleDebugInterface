#!/bin/bash

# You will need `sudo usermod -a -G tty $USER`


function demo
{
        konsole -e "minicom -D /tmp/ttyS10" &
        konsole -e "minicom -D /tmp/ttyS11" &
}

echo "Setting up linked virtual serial ports:"
echo "    /tmp/ttyS10"
echo "    /tmp/ttyS11"

socat PTY,link=/tmp/ttyS10 PTY,link=/tmp/ttyS11



