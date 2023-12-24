# Write your code here :-)
# SPDX-FileCopyrightText: 2022 Dan Halbert for Adafruit Industries
#
# SPDX-License-Identifier: Unlicense
import socketpool
import wifi
import os
import time
import asyncio as aio


import adafruit_httpserver as ahs


import microsd
import minfileserv as mf

def connect_build_srv():
    ahs.MIMETypes.configure(
        default_to="text/plain",
        # Unregistering unnecessary MIME types can save memory
        keep_for=[".html", ".css", ".js", ".png", ".jpg", ".jpeg", ".gif", ".ico"],
        # If you need to, you can add additional MIME types
        register={".foo": "text/foo", ".bar": "text/bar"},
    )

    sd_root = microsd.create()
    display_root = "/sdd"

    ssid = os.getenv("WIFI_SSID")
    password = os.getenv("WIFI_PASSWORD")


    print("Connecting to", ssid)
    wifi.radio.connect(ssid, password)
    print("Connected to", ssid)

    pool = socketpool.SocketPool(wifi.radio)
    server = ahs.Server(pool, "/static", debug=True)


    @server.route("/")
    def base(request: ahs.Request):
        """
        Serve the default index.html file.
        """
        return ahs.FileResponse(request, "index.html")

    @server.route(f"{display_root}....",[ahs.GET],append_slash=False)
    @server.route(f"{display_root}",[ahs.GET],append_slash=False)
    def usd_root(request: ahs.Request):
        """
        serve the microsd directory
        """

        #fIOres = mf.list_directory(sd_root)
        print(request)
        print(f"headers: {request.headers}")
        print(f"httpvers: {request.http_version}")
        print(f"json: {request.json()}")
        print(f"method: {request.method}")
        print(f"path: {request.path}")
        print(f"queryParam: {request.query_params}")
        #print(f"raw: {request.raw_request}")


        #def bob():
        #    for gg in fIOres:
        #        yield gg.decode('utf-8')

        #return ahs.ChunkedResponse(request, bob, content_type=".html")
        return mf.fileServer(sd_root, display_root, request)


    return server

async def run_polling(server, poll_time):
    # Start the server.
    server.start(str(wifi.radio.ipv4_address))

    while True:
        try:
            # Do something useful in this section,
            # for example read a sensor and capture an average,
            # or a running total of the last 10 samples

            await aio.sleep(poll_time)
            # Process any waiting requests
            pool_result = server.poll()

            if pool_result == ahs.REQUEST_HANDLED_RESPONSE_SENT:
                # Do something only after handling a request
                pass

            # You can stop the server by calling server.stop() anywhere in your code
        except OSError as error:
            print(error)
            continue


def run_blocking(server):
    # Start the server.
    server.start(str(wifi.radio.ipv4_address))

    while True:
        try:
            # Do something useful in this section,
            # for example read a sensor and capture an average,
            # or a running total of the last 10 samples

            time.sleep(0.01)
            # Process any waiting requests
            pool_result = server.poll()

            if pool_result == ahs.REQUEST_HANDLED_RESPONSE_SENT:
                # Do something only after handling a request
                pass

            # You can stop the server by calling server.stop() anywhere in your code
        except OSError as error:
            print(error)
            continue
