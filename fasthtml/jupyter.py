# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/api/06_jupyter.ipynb.

# %% auto 0
__all__ = ['cors_allow', 'nb_serve', 'nb_serve_async', 'is_port_free', 'wait_port_free', 'JupyUvi', 'FastJupy', 'HTMX',
           'jupy_app']

# %% ../nbs/api/06_jupyter.ipynb
import asyncio, socket, time, uvicorn
from threading import Thread
from fastcore.utils import *
from .common import *
from IPython.display import HTML,Markdown,IFrame
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware import Middleware
from fastcore.parallel import startthread

# %% ../nbs/api/06_jupyter.ipynb
def nb_serve(app, log_level="error", port=8000, **kwargs):
    "Start a Jupyter compatible uvicorn server with ASGI `app` on `port` with `log_level`"
    server = uvicorn.Server(uvicorn.Config(app, log_level=log_level, port=port, **kwargs))
    async def async_run_server(server): await server.serve()
    @startthread
    def run_server(): asyncio.run(async_run_server(server))
    while not server.started: time.sleep(0.01)
    return server

# %% ../nbs/api/06_jupyter.ipynb
async def nb_serve_async(app, log_level="error", port=8000, **kwargs):
    "Async version of `nb_serve`"
    server = uvicorn.Server(uvicorn.Config(app, log_level=log_level, port=port, **kwargs))
    asyncio.get_running_loop().create_task(server.serve())
    while not server.started: await asyncio.sleep(0.01)
    return server

# %% ../nbs/api/06_jupyter.ipynb
def is_port_free(port, host='localhost'):
    "Check if `port` is free on `host`"
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        return True
    except OSError: return False
    finally: sock.close()

# %% ../nbs/api/06_jupyter.ipynb
def wait_port_free(port, host='localhost', max_wait=3):
    "Wait for `port` to be free on `host`"
    start_time = time.time()
    while not is_port_free(port):
        if time.time() - start_time>max_wait: return print(f"Timeout")
        time.sleep(0.1)

# %% ../nbs/api/06_jupyter.ipynb
cors_allow = Middleware(CORSMiddleware, allow_credentials=True,
                        allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# %% ../nbs/api/06_jupyter.ipynb
class JupyUvi:
    "Start and stop a Jupyter compatible uvicorn server with ASGI `app` on `port` with `log_level`"
    def __init__(self, app, log_level="error", port=8000, start=True, **kwargs):
        self.kwargs = kwargs
        store_attr(but='start')
        self.server = None
        if start: self.start()

    def start(self):
        self.server = nb_serve(self.app, log_level=self.log_level, port=self.port, **self.kwargs)

    def stop(self):
        self.server.should_exit = True
        wait_port_free(self.port)

# %% ../nbs/api/06_jupyter.ipynb
# The script lets an iframe parent know of changes so that it can resize automatically.  
_iframe_scr = Script("""
    function sendmsg() {window.parent.postMessage({height: document.documentElement.offsetHeight}, '*')}
    window.onload = function() {
        sendmsg();
        document.body.addEventListener('htmx:afterSettle', sendmsg);
    };""")

# %% ../nbs/api/06_jupyter.ipynb
def FastJupy(hdrs=None, middleware=None, **kwargs):
    "Same as FastHTML, but with Jupyter compatible middleware and headers added"
    hdrs = listify(hdrs)+[_iframe_scr]
    middleware = listify(middleware)+[cors_allow]
    return FastHTML(hdrs=hdrs, middleware=middleware, **kwargs)

# %% ../nbs/api/06_jupyter.ipynb
def HTMX(host='localhost', path="/", port=8000, iframe_height="auto"):
    "An iframe which displays the HTMX application in a notebook."
    return HTML(f'<iframe src="http://{host}:{port}{path}" style="width: 100%; height: {iframe_height}; border: none;" ' + """onload="{
        let frame = this;
        window.addEventListener('message', function(e) {
            if (e.data.height) frame.style.height = (e.data.height+1) + 'px';
        }, false);
    }" allow="accelerometer; autoplay; camera; clipboard-read; clipboard-write; display-capture; encrypted-media; fullscreen; gamepad; geolocation; gyroscope; hid; identity-credentials-get; idle-detection; magnetometer; microphone; midi; payment; picture-in-picture; publickey-credentials-get; screen-wake-lock; serial; usb; web-share; xr-spatial-tracking"></iframe> """)

# %% ../nbs/api/06_jupyter.ipynb
def jupy_app(pico=False, hdrs=None, middleware=None, **kwargs):
    "Same as `fast_app` but for Jupyter notebooks"
    hdrs = listify(hdrs)+[_iframe_scr]
    middleware = listify(middleware)+[cors_allow]
    return fast_app(pico=pico, hdrs=hdrs, middleware=middleware, **kwargs)
