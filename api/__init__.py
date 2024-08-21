# api/__init__.py

# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties
# of merchantability, fitness for a particular purpose and
# noninfringement. In no event shall the authors or copyright
# holders be liable for any claim, damages, or other liability,
# whether in an action of contract, tort or otherwise, arising
# from, out of or in connection with the software or the use or
# other dealings in the software.

from flask import Flask
from .accounts import accounts_bp
from .blockchain import blockchain_bp
from .contracts import contracts_bp
from .fts import fts_bp
from .nfts import nfts_bp
from .transactions import transactions_bp
import logging

def create_app():
    app = Flask(__name__)

    # Basic logging setup
    logging.basicConfig(level=logging.INFO)

    # Registering the Blueprints
    app.register_blueprint(accounts_bp, url_prefix='/accounts')
    app.register_blueprint(blockchain_bp, url_prefix='/blockchain')
    app.register_blueprint(contracts_bp, url_prefix='/contracts')
    app.register_blueprint(fts_bp, url_prefix='/fts')
    app.register_blueprint(nfts_bp, url_prefix='/nfts')
    app.register_blueprint(transactions_bp, url_prefix='/transactions')

    # Global error handlers (Optional)
    @app.errorhandler(404)
    def not_found_error(error):
        return {"error": "Not found"}, 404

    @app.errorhandler(500)
    def internal_error(error):
        return {"error": "Internal server error"}, 500

    return app
