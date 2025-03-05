#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QFrame, QDialog, QFormLayout,
                             QLineEdit, QComboBox, QDoubleSpinBox, QTextEdit,
                             QDialogButtonBox, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QFont, QColor
import os

class AccountsView(QWidget):
    """Accounts view showing all financial accounts and their details."""
    
    # Signal emitted when user requests to add a new account
    add_account_requested = pyqtSignal(dict)
    
    # Signal emitted when user requests to edit an account
    edit_account_requested = pyqtSignal(int, dict)
    
    # Signal emitted when user requests to delete an account
    delete_account_requested = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header section
        header_layout = QHBoxLayout()
        
        # Title
        title_label = QLabel("Cuentas Financieras")
        title_font = QFont("Segoe UI", 16, QFont.Bold)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        
        # Spacer
        header_layout.addStretch()
        
        # Add account button
        self.add_account_btn = QPushButton("Nueva Cuenta")
        self.add_account_btn.clicked.connect(self.show_add_account_dialog)
        header_layout.addWidget(self.add_account_btn)
        
        main_layout.addLayout(header_layout)
        
        # Accounts table
        self.accounts_table = QTableWidget()
        self.accounts_table.setColumnCount(5)
        self.accounts_table.setHorizontalHeaderLabels(["Nombre", "Tipo", "Moneda", "Saldo Actual", "Acciones"])
        self.accounts_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.accounts_table.setAlternatingRowColors(True)
        self.accounts_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.accounts_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.accounts_table.setSelectionMode(QTableWidget.SingleSelection)
        
        main_layout.addWidget(self.accounts_table)
    
    def load_accounts(self, accounts):
        """Load accounts data into the table.
        
        Args:
            accounts (list): List of account dictionaries
        """
        self.accounts_table.setRowCount(0)  # Clear existing rows
        
        if not accounts:
            return
        
        for row, account in enumerate(accounts):
            self.accounts_table.insertRow(row)
            
            # Name
            name_item = QTableWidgetItem(account['name'])
            self.accounts_table.setItem(row, 0, name_item)
            
            # Type
            type_item = QTableWidgetItem(self.get_account_type_display(account['type']))
            self.accounts_table.setItem(row, 1, type_item)
            
            # Currency
            currency_item = QTableWidgetItem(account['currency'])
            self.accounts_table.setItem(row, 2, currency_item)
            
            # Balance
            balance_item = QTableWidgetItem(f"{account['current_balance']:.2f}")
            balance_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.accounts_table.setItem(row, 3, balance_item)
            
            # Actions
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(4, 4, 4, 4)
            actions_layout.setSpacing(4)
            
            edit_btn = QPushButton("Editar")
            edit_btn.setProperty("account_id", account['id'])
            edit_btn.clicked.connect(lambda checked, aid=account['id']: self.edit_account(aid))
            actions_layout.addWidget(edit_btn)
            
            delete_btn = QPushButton("Eliminar")
            delete_btn.setProperty("account_id", account['id'])
            delete_btn.clicked.connect(lambda checked, aid=account['id']: self.delete_account(aid))
            actions_layout.addWidget(delete_btn)
            
            actions_widget = QWidget()
            actions_widget.setLayout(actions_layout)
            self.accounts_table.setCellWidget(row, 4, actions_widget)
    
    def get_account_type_display(self, account_type):
        """Convert account type code to display name.
        
        Args:
            account_type (str): Account type code
            
        Returns:
            str: Display name for the account type
        """
        account_types = {
            'checking': 'Cuenta Corriente',
            'savings': 'Cuenta de Ahorros',
            'credit': 'Tarjeta de Crédito',
            'investment': 'Inversión',
            'cash': 'Efectivo',
            'other': 'Otro'
        }
        return account_types.get(account_type, account_type)
    
    def show_add_account_dialog(self):
        """Show dialog to add a new account."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Nueva Cuenta")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # Name field
        name_edit = QLineEdit()
        form_layout.addRow("Nombre:", name_edit)
        
        # Type field
        type_combo = QComboBox()
        type_combo.addItem("Cuenta Corriente", "checking")
        type_combo.addItem("Cuenta de Ahorros", "savings")
        type_combo.addItem("Tarjeta de Crédito", "credit")
        type_combo.addItem("Inversión", "investment")
        type_combo.addItem("Efectivo", "cash")
        type_combo.addItem("Otro", "other")
        form_layout.addRow("Tipo:", type_combo)
        
        # Currency field
        currency_combo = QComboBox()
        currency_combo.addItem("MXN - Peso Mexicano", "MXN")
        currency_combo.addItem("USD - Dólar Estadounidense", "USD")
        currency_combo.addItem("EUR - Euro", "EUR")
        form_layout.addRow("Moneda:", currency_combo)
        
        # Initial balance field
        balance_spin = QDoubleSpinBox()
        balance_spin.setRange(0, 1000000000)
        balance_spin.setDecimals(2)
        balance_spin.setSingleStep(100)
        form_layout.addRow("Saldo Inicial:", balance_spin)
        
        # Description field
        description_edit = QTextEdit()
        description_edit.setMaximumHeight(100)
        form_layout.addRow("Descripción:", description_edit)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        if dialog.exec_() == QDialog.Accepted:
            # Create account data dictionary
            account_data = {
                'name': name_edit.text(),
                'type': type_combo.currentData(),
                'currency': currency_combo.currentData(),
                'initial_balance': balance_spin.value(),
                'description': description_edit.toPlainText() if description_edit.toPlainText() else None
            }
            
            # Emit signal with account data
            self.add_account_requested.emit(account_data)
    
    def edit_account(self, account_id):
        """Edit an existing account.
        
        Args:
            account_id (int): ID of the account to edit
        """
        # Find the account data in the table
        for row in range(self.accounts_table.rowCount()):
            for col in range(self.accounts_table.columnCount()):
                cell_widget = self.accounts_table.cellWidget(row, 4)
                if cell_widget:
                    actions_layout = cell_widget.layout()
                    for i in range(actions_layout.count()):
                        button = actions_layout.itemAt(i).widget()
                        if button and button.property("account_id") == account_id and button.text() == "Editar":
                            # Found the account, get its data
                            name = self.accounts_table.item(row, 0).text()
                            account_type_display = self.accounts_table.item(row, 1).text()
                            currency = self.accounts_table.item(row, 2).text()
                            balance = self.accounts_table.item(row, 3).text()
                            
                            # Show edit dialog
                            self.show_edit_account_dialog(account_id, name, account_type_display, currency, balance)
                            return
    
    def show_edit_account_dialog(self, account_id, name, account_type_display, currency, balance):
        """Show dialog to edit an existing account.
        
        Args:
            account_id (int): ID of the account to edit
            name (str): Current name of the account
            account_type_display (str): Current account type display name
            currency (str): Current currency
            balance (str): Current balance as string
        """
        dialog = QDialog(self)
        dialog.setWindowTitle("Editar Cuenta")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # Name field
        name_edit = QLineEdit(name)
        form_layout.addRow("Nombre:", name_edit)
        
        # Type field
        type_combo = QComboBox()
        type_combo.addItem("Cuenta Corriente", "checking")
        type_combo.addItem("Cuenta de Ahorros", "savings")
        type_combo.addItem("Tarjeta de Crédito", "credit")
        type_combo.addItem("Inversión", "investment")
        type_combo.addItem("Efectivo", "cash")
        type_combo.addItem("Otro", "other")
        # Set current account type
        for i in range(type_combo.count()):
            if type_combo.itemText(i) == account_type_display:
                type_combo.setCurrentIndex(i)
                break
        form_layout.addRow("Tipo:", type_combo)
        
        # Currency field
        currency_combo = QComboBox()
        currency_combo.addItem("MXN - Peso Mexicano", "MXN")
        currency_combo.addItem("USD - Dólar Estadounidense", "USD")
        currency_combo.addItem("EUR - Euro", "EUR")
        # Set current currency
        for i in range(currency_combo.count()):
            if currency_combo.itemData(i) == currency:
                currency_combo.setCurrentIndex(i)
                break
        form_layout.addRow("Moneda:", currency_combo)
        
        # Current balance field
        balance_spin = QDoubleSpinBox()
        balance_spin.setRange(-1000000000, 1000000000)
        balance_spin.setDecimals(2)
        balance_spin.setSingleStep(100)
        # Set current balance
        try:
            balance_value = float(balance)
            balance_spin.setValue(balance_value)
        except ValueError:
            balance_spin.setValue(0)
        form_layout.addRow("Saldo Actual:", balance_spin)
        
        # Description field
        description_edit = QTextEdit()
        description_edit.setMaximumHeight(100)
        form_layout.addRow("Descripción:", description_edit)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        if dialog.exec_() == QDialog.Accepted:
            # Create account data dictionary
            account_data = {
                'id': account_id,
                'name': name_edit.text(),
                'type': type_combo.currentData(),
                'currency': currency_combo.currentData(),
                'current_balance': balance_spin.value(),
                'description': description_edit.toPlainText() if description_edit.toPlainText() else None
            }
            
            # Emit signal with account data
            self.edit_account_requested.emit(account_id, account_data)
    
    def delete_account(self, account_id):
        """Delete an account.
        
        Args:
            account_id (int): ID of the account to delete
        """
        # Show confirmation dialog
        confirm = QMessageBox.question(
            self,
            "Confirmar eliminación",
            "¿Está seguro de que desea eliminar esta cuenta? Esta acción no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            # Emit signal to delete the account
            self.delete_account_requested.emit(account_id)