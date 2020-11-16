"""A single common terminal for all websockets.
"""
import tornado.web
# This demo requires tornado_xstatic and XStatic-term.js
import tornado_xstatic

from terminado import TermSocket, SingleTermManager

import os.path
import webbrowser
import tornado.ioloop
import terminado

STATIC_DIR = os.path.join(os.path.dirname(terminado.__file__), "_static")
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")

def run_and_show_browser(url, term_manager):
    loop = tornado.ioloop.IOLoop.instance()
    loop.add_callback(webbrowser.open, url)
    try:
        loop.start()
    except KeyboardInterrupt:
        print(" Shutting down on SIGINT")
    finally:
        term_manager.shutdown()
        loop.close()

class TerminalPageHandler(tornado.web.RequestHandler):
    def get(self):
        return self.render("xterm.html", static=self.static_url,
                           xstatic=self.application.settings['xstatic_url'],
                           ws_url_path="/websocket")

def main(cmd):
    term_manager = SingleTermManager(shell_command=cmd)
    handlers = [
                (r"/websocket", TermSocket,
                     {'term_manager': term_manager}),
                (r"/", TerminalPageHandler),
                (r"/xstatic/(.*)", tornado_xstatic.XStaticFileHandler,
                     {'allowed_modules': ['termjs']})
               ]
    app = tornado.web.Application(handlers, static_path=STATIC_DIR,
                      template_path=TEMPLATE_DIR,
                      xstatic_url = tornado_xstatic.url_maker('/xstatic/'))
    app.listen(8765, 'localhost')
    run_and_show_browser("http://localhost:8765/", term_manager)


if __name__ == '__main__':

    import sys
    cmd = sys.argv[1:]
    print(f"Running terminado server, with command {cmd}")

    main(cmd)
