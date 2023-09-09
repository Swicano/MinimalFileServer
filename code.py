# Write your code here :-)
# SPDX-FileCopyrightText: 2022 Dan Halbert for Adafruit Industries
#
# SPDX-License-Identifier: Unlicense
import socketpool
import wifi
import os

from adafruit_httpserver import (
    Server,
    REQUEST_HANDLED_RESPONSE_SENT,
    Request,
    FileResponse, ChunkedResponse,
    MIMETypes
)


import microsd
import minfileserv as mf

MIMETypes.configure(
    default_to="text/plain",
    # Unregistering unnecessary MIME types can save memory
    keep_for=[".html", ".css", ".js", ".png", ".jpg", ".jpeg", ".gif", ".ico"],
    # If you need to, you can add additional MIME types
    register={".foo": "text/foo", ".bar": "text/bar"},
)

sd_root = microsd.create()

ssid = os.getenv("WIFI_SSID")
password = os.getenv("WIFI_PASSWORD")


print("Connecting to", ssid)
wifi.radio.connect(ssid, password)
print("Connected to", ssid)

pool = socketpool.SocketPool(wifi.radio)
server = Server(pool, "/static", debug=True)


@server.route("/")
def base(request: Request):
    """
    Serve the default index.html file.
    """
    return FileResponse(request, "index.html")

@server.route("/sd")
def usd_root(request: Request):
    """
    serve the microsd directory
    """
    fIOres = mf.list_directory(sd_root)

    def bob():
        for gg in fIOres:
            yield gg.decode('utf-8')

    return ChunkedResponse(request, bob, content_type=".html")

# Start the server.
server.start(str(wifi.radio.ipv4_address))

while True:
    try:
        # Do something useful in this section,
        # for example read a sensor and capture an average,
        # or a running total of the last 10 samples

        # Process any waiting requests
        pool_result = server.poll()

        if pool_result == REQUEST_HANDLED_RESPONSE_SENT:
            # Do something only after handling a request
            pass

        # You can stop the server by calling server.stop() anywhere in your code
    except OSError as error:
        print(error)
        continue
