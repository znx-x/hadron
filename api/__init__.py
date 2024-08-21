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
from .blockchain import create_blockchain_blueprint
from .contracts import create_contracts_blueprint
from .fts import create_fts_blueprint
from .nfts import create_nfts_blueprint
from .transactions import create_transactions_blueprint
import logging

def create_app(blockchain):
    app = Flask(__name__)

    # Basic logging setup
    logging.basicConfig(level=logging.INFO)

    # Registering the Blueprints with the blockchain instance
    app.register_blueprint(accounts_bp, url_prefix='/accounts')
    app.register_blueprint(create_blockchain_blueprint(blockchain), url_prefix='/blockchain')
    app.register_blueprint(create_contracts_blueprint(blockchain), url_prefix='/contracts')
    app.register_blueprint(create_fts_blueprint(blockchain), url_prefix='/fts')
    app.register_blueprint(create_nfts_blueprint(blockchain), url_prefix='/nfts')
    app.register_blueprint(create_transactions_blueprint(blockchain), url_prefix='/transactions')

    # Global error handlers (Optional)
    @app.errorhandler(404)
    def not_found_error(error):
        return {"error": "Not found"}, 404

    @app.errorhandler(500)
    def internal_error(error):
        return {"error": "Internal server error"}, 500

    return app
