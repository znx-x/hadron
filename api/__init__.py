# api/__init__.py

# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties
# of merchantability, fitness for a particular purpose and
# noninfringement. In no event shall the authors or copyright
# holders be liable for any claim, damages, or other liability,
# whether in an action of contract, tort or otherwise, arising
# from, out of or in connection with the software or the use or
# other dealings in the software.

# api/__init__.py

from flask import Flask
import logging

# Existing imports for your other blueprints:
from .accounts import accounts_bp
from .blockchain import create_blockchain_blueprint
from .contracts import create_contracts_blueprint
from .fts import create_fts_blueprint
from .nfts import create_nfts_blueprint
from .transactions import create_transactions_blueprint

# Import your new admin blueprint factory
from .admin import create_admin_blueprint

def create_app(blockchain, miner):
    app = Flask(__name__)
    logging.basicConfig(level=logging.INFO)

    # Store references in app config so the admin blueprint can access them
    app.config['blockchain'] = blockchain
    app.config['miner'] = miner
    # If you have a separate network object, you can do:
    # app.config['network'] = blockchain.p2p_network  # or however you store it

    # Register your existing blueprints
    app.register_blueprint(accounts_bp, url_prefix='/accounts')
    app.register_blueprint(create_blockchain_blueprint(blockchain, miner), url_prefix='/blockchain')
    app.register_blueprint(create_contracts_blueprint(blockchain), url_prefix='/contracts')
    app.register_blueprint(create_fts_blueprint(blockchain), url_prefix='/fts')
    app.register_blueprint(create_nfts_blueprint(blockchain), url_prefix='/nfts')
    app.register_blueprint(create_transactions_blueprint(blockchain), url_prefix='/transactions')

    # Register the admin blueprint at /admin
    admin_bp = create_admin_blueprint()
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # Global error handlers (Optional)
    @app.errorhandler(404)
    def not_found_error(error):
        return {"error": "Not found"}, 404

    @app.errorhandler(500)
    def internal_error(error):
        return {"error": "Internal server error"}, 500

    return app

