import os.path
from pprint import pprint
import tornado.web
import tornado.ioloop
# This demo requires tornado_xstatic and XStatic-term.js
import tornado_xstatic

import terminado
import re

STATIC_DIR = os.path.join(os.path.dirname(terminado.__file__), "_static")
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")

class TerminalPageHandler(tornado.web.RequestHandler):
    def get(self):
        return self.render("sockterm.html", static=self.static_url,
                           xstatic=self.application.settings['xstatic_url'],
                           ws_url_path="/websocket")



class PlainTermSocket(terminado.TermSocket):
    """Plaintext version of terminado textsocket""" 

    def on_pty_read(self, text):
        # remove unsupported OCR command (will fix later)
        text = re.sub("\x1b]\d;.*((\x1b\\\\)|(\x07))", "", text)
        # temporary workaround for issue #2
        text = re.sub("\x1b\[0(\d+)", "\x1b[\\1", text)
        self.write_message(text)

    def send_json_message(self, msg):
        pass

    def on_message(self, message):
        self.terminal.ptyproc.write(message)


if __name__ == '__main__':
    import sys
    cmd = sys.argv[1:]
    print(f"Running terminado server, with command {cmd}")

    term_manager = terminado.SingleTermManager(shell_command=[cmd])
    handlers = [
                (r"/websocket", PlainTermSocket,
                     {'term_manager': term_manager}),
                (r"/", TerminalPageHandler)
               ]
    app = tornado.web.Application(handlers, static_path=STATIC_DIR,

                                  template_path=TEMPLATE_DIR,
                      xstatic_url = tornado_xstatic.url_maker('/xstatic/'))
    # Serve at http://localhost:8000/ N.B. Leaving out 'localhost' here will
    # work, but it will listen on the public network interface as well.
    # Given what terminado does, that would be rather a security hole.
    app.listen(8000, 'localhost')
    try:
        tornado.ioloop.IOLoop.instance().start()
    finally:
        term_manager.shutdown()
