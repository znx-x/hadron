# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties
# of merchantability, fitness for a particular purpose and
# noninfringement. In no event shall the authors or copyright
# holders be liable for any claim, damages, or other liability,
# whether in an action of contract, tort or otherwise, arising
# from, out of or in connection with the software or the use or
# other dealings in the software.

from flask import Flask
from api import create_app
from parameters import parameters

app = create_app()

if __name__ == "__main__":
    host = parameters.get("host", "0.0.0.0")
    port = parameters.get("port", 5000)
    app.run(host=host, port=port)
