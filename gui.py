# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties
# of merchantability, fitness for a particular purpose and
# noninfringement. In no event shall the authors or copyright
# holders be liable for any claim, damages, or other liability,
# whether in an action of contract, tort or otherwise, arising
# from, out of or in connection with the software or the use or
# other dealings in the software.

# Graphical User Interface (GUI) for the blockchain network.

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QVBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMenuBar, QMenu
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

class WalletUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Blockchain Wallet")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon('wallet_icon.png'))

        self.init_ui()

    def init_ui(self):
        self.create_menu_bar()
        self.create_wallet_overview()
        self.create_transactions_table()
        self.create_network_status()

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.wallet_overview)
        main_layout.addWidget(self.transactions_table)
        main_layout.addWidget(self.network_status)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def create_menu_bar(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("&File")
        exit_action = QAction(QIcon('exit.png'), 'Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        wallet_menu = menu_bar.addMenu("&Wallet")
        new_wallet_action = QAction("New Wallet", self)
        load_wallet_action = QAction("Load Wallet", self)
        wallet_menu.addAction(new_wallet_action)
        wallet_menu.addAction(load_wallet_action)

        view_menu = menu_bar.addMenu("&View")
        overview_action = QAction("Overview", self)
        transactions_action = QAction("Transactions", self)
        view_menu.addAction(overview_action)
        view_menu.addAction(transactions_action)

        help_menu = menu_bar.addMenu("&Help")
        about_action = QAction("About", self)
        help_menu.addAction(about_action)

    def create_wallet_overview(self):
        self.wallet_overview = QWidget()
        layout = QVBoxLayout()

        balance_label = QLabel("Balance:")
        self.balance_amount = QLabel("0.00")

        layout.addWidget(balance_label)
        layout.addWidget(self.balance_amount)

        self.wallet_overview.setLayout(layout)

    def create_transactions_table(self):
        self.transactions_table = QTableWidget()
        self.transactions_table.setColumnCount(4)
        self.transactions_table.setHorizontalHeaderLabels(["Date", "Type", "Amount", "Status"])
        self.transactions_table.horizontalHeader().setStretchLastSection(True)

        # Example data
        example_data = [
            {"date": "2024-08-21", "type": "Sent", "amount": "-10.00", "status": "Confirmed"},
            {"date": "2024-08-20", "type": "Received", "amount": "25.00", "status": "Pending"},
        ]
        self.transactions_table.setRowCount(len(example_data))

        for i, data in enumerate(example_data):
            self.transactions_table.setItem(i, 0, QTableWidgetItem(data["date"]))
            self.transactions_table.setItem(i, 1, QTableWidgetItem(data["type"]))
            self.transactions_table.setItem(i, 2, QTableWidgetItem(data["amount"]))
            self.transactions_table.setItem(i, 3, QTableWidgetItem(data["status"]))

    def create_network_status(self):
        self.network_status = QWidget()
        layout = QVBoxLayout()

        status_label = QLabel("Network Status:")
        self.status_info = QLabel("Connected to 5 peers")

        layout.addWidget(status_label)
        layout.addWidget(self.status_info)

        self.network_status.setLayout(layout)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    wallet_ui = WalletUI()
    wallet_ui.show()
    sys.exit(app.exec_())
