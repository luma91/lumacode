import logging
import os

import config
import graph_server
from flask import Flask

log_path = os.path.join(config.base_path, config.log_directory)
logging.basicConfig(filename=log_path,
                    filemode='a',
                    format='%(asctime)s - %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO)


def web_server():

    app = Flask(__name__)
    app.register_blueprint(graph_server.anime_tracker)

    @app.route('/', methods=['GET'])
    def index():
        return 'nothing to see here yet...'

    # For Testing
    if config.local:
        app.run(host='0.0.0.0', port=8080)

    # For AWS
    else:
        app.run(host='0.0.0.0', port=80)


if __name__ == "__main__":
    web_server()
