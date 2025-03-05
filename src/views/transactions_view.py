#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QFrame, QDialog, QFormLayout,
                             QLineEdit, QComboBox, QDoubleSpinBox, QTextEdit,
                             QDialogButtonBox, QMessageBox, QDateEdit)
from PyQt5.QtCore import Qt, pyqtSignal, QDate
from PyQt5.QtGui import QIcon, QFont, QColor
import os
from datetime import datetime

class TransactionsView(QWidget):
    """Transactions view showing all financial transactions and their details."""
    
    # Signal emitted when user requests to add a new transaction
    add_transaction_requested = pyqtSignal(dict)
    
    # Signal emitted when user requests to edit a transaction
    edit_transaction_requested = pyqtSignal(int, dict)
    
    # Signal emitted when user requests to delete a transaction
    delete_transaction_requested = pyqtSignal(int)
    
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
        title_label = QLabel("Transacciones")
        title_font = QFont("Segoe UI", 16, QFont.Bold)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        
        # Spacer
        header_layout.addStretch()
        
        # Add transaction button
        self.add_transaction_btn = QPushButton("Nueva Transacción")
        self.add_transaction_btn.clicked.connect(self.show_add_transaction_dialog)
        header_layout.addWidget(self.add_transaction_btn)
        
        main_layout.addLayout(header_layout)
        
        # Transactions table
        self.transactions_table = QTableWidget()
        self.transactions_table.setColumnCount(6)
        self.transactions_table.setHorizontalHeaderLabels(["Fecha", "Cuenta", "Categoría", "Descripción", "Monto", "Acciones"])
        self.transactions_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.transactions_table.setAlternatingRowColors(True)
        self.transactions_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.transactions_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.transactions_table.setSelectionMode(QTableWidget.SingleSelection)
        
        main_layout.addWidget(self.transactions_table)
    
    def load_transactions(self, transactions):
        """Load transactions data into the table.
        
        Args:
            transactions (list): List of transaction dictionaries
        """
        self.transactions_table.setRowCount(0)  # Clear existing rows
        
        if not transactions:
            return
        
        for row, transaction in enumerate(transactions):
            self.transactions_table.insertRow(row)
            
            # Date
            date_str = transaction['date']
            if isinstance(date_str, str):
                # Handle date strings that might include time information
                if ' ' in date_str:  # Check if there's a space indicating time portion
                    date_obj = datetime.strptime(date_str.split(' ')[0], '%Y-%m-%d')  # Extract just the date part
                else:
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                date_display = date_obj.strftime('%d/%m/%Y')
            else:
                date_display = date_str.strftime('%d/%m/%Y')
            date_item = QTableWidgetItem(date_display)
            self.transactions_table.setItem(row, 0, date_item)
            
            # Account
            account_item = QTableWidgetItem(transaction.get('account_name', 'Unknown'))
            self.transactions_table.setItem(row, 1, account_item)
            
            # Category
            category_item = QTableWidgetItem(transaction.get('category_name', 'Sin categoría'))
            self.transactions_table.setItem(row, 2, category_item)
            
            # Description
            description_item = QTableWidgetItem(transaction.get('description', ''))
            self.transactions_table.setItem(row, 3, description_item)
            
            # Amount
            amount = transaction['amount']
            if transaction['type'] == 'expense':
                amount_str = f"-{amount:.2f}"
                amount_color = QColor("#DC3545")  # Red for expenses
            elif transaction['type'] == 'income':
                amount_str = f"+{amount:.2f}"
                amount_color = QColor("#28A745")  # Green for income
            else:
                amount_str = f"{amount:.2f}"
                amount_color = QColor("#6C757D")  # Gray for transfers
                
            amount_item = QTableWidgetItem(amount_str)
            amount_item.setForeground(amount_color)
            amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.transactions_table.setItem(row, 4, amount_item)
            
            # Actions
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(4, 4, 4, 4)
            actions_layout.setSpacing(4)
            
            edit_btn = QPushButton("Editar")
            edit_btn.setProperty("transaction_id", transaction['id'])
            edit_btn.clicked.connect(lambda checked, tid=transaction['id']: self.edit_transaction(tid))
            actions_layout.addWidget(edit_btn)
            
            delete_btn = QPushButton("Eliminar")
            delete_btn.setProperty("transaction_id", transaction['id'])
            delete_btn.clicked.connect(lambda checked, tid=transaction['id']: self.delete_transaction(tid))
            actions_layout.addWidget(delete_btn)
            
            actions_widget = QWidget()
            actions_widget.setLayout(actions_layout)
            self.transactions_table.setCellWidget(row, 5, actions_widget)
    
    def show_add_transaction_dialog(self):
        """Show dialog to add a new transaction."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Nueva Transacción")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # Account field
        account_combo = QComboBox()
        # This would be populated with actual accounts from the database
        account_combo.addItem("Cuenta Principal", 1)
        account_combo.addItem("Tarjeta de Crédito", 2)
        account_combo.addItem("Ahorros", 3)
        form_layout.addRow("Cuenta:", account_combo)
        
        # Type field
        type_combo = QComboBox()
        type_combo.addItem("Gasto", "expense")
        type_combo.addItem("Ingreso", "income")
        type_combo.addItem("Transferencia", "transfer")
        form_layout.addRow("Tipo:", type_combo)
        
        # Category field
        category_combo = QComboBox()
        # This would be populated with actual categories from the database
        category_combo.addItem("Alimentación", 1)
        category_combo.addItem("Transporte", 2)
        category_combo.addItem("Vivienda", 3)
        category_combo.addItem("Entretenimiento", 4)
        form_layout.addRow("Categoría:", category_combo)
        
        # Amount field
        amount_spin = QDoubleSpinBox()
        amount_spin.setRange(0, 1000000000)
        amount_spin.setDecimals(2)
        amount_spin.setSingleStep(100)
        form_layout.addRow("Monto:", amount_spin)
        
        # Date field
        date_edit = QDateEdit()
        date_edit.setCalendarPopup(True)
        date_edit.setDate(QDate.currentDate())
        form_layout.addRow("Fecha:", date_edit)
        
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
            # Create transaction data dictionary
            transaction_data = {
                'account_id': account_combo.currentData(),
                'type': type_combo.currentData(),
                'category_id': category_combo.currentData(),
                'amount': amount_spin.value(),
                'date': date_edit.date().toString("yyyy-MM-dd"),
                'description': description_edit.toPlainText() if description_edit.toPlainText() else None
            }
            
            # Emit signal with transaction data
            self.add_transaction_requested.emit(transaction_data)
    
    def edit_transaction(self, transaction_id):
        """Edit an existing transaction.
        
        Args:
            transaction_id (int): ID of the transaction to edit
        """
        # Find the transaction data in the table
        for row in range(self.transactions_table.rowCount()):
            for col in range(self.transactions_table.columnCount()):
                cell_widget = self.transactions_table.cellWidget(row, 5)
                if cell_widget:
                    actions_layout = cell_widget.layout()
                    for i in range(actions_layout.count()):
                        button = actions_layout.itemAt(i).widget()
                        if button and button.property("transaction_id") == transaction_id and button.text() == "Editar":
                            # Found the transaction, get its data
                            date_text = self.transactions_table.item(row, 0).text()
                            account_name = self.transactions_table.item(row, 1).text()
                            category_name = self.transactions_table.item(row, 2).text()
                            description = self.transactions_table.item(row, 3).text()
                            amount_text = self.transactions_table.item(row, 4).text()
                            
                            # Show edit dialog
                            self.show_edit_transaction_dialog(transaction_id, date_text, account_name, category_name, description, amount_text)
                            return
    
    def show_edit_transaction_dialog(self, transaction_id, date_text, account_name, category_name, description, amount_text):
        """Show dialog to edit an existing transaction.
        
        Args:
            transaction_id (int): ID of the transaction to edit
            date_text (str): Current date of the transaction
            account_name (str): Current account name
            category_name (str): Current category name
            description (str): Current description
            amount_text (str): Current amount text
        """
        dialog = QDialog(self)
        dialog.setWindowTitle("Editar Transacción")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # Account field
        account_combo = QComboBox()
        # This would be populated with actual accounts from the database
        account_combo.addItem("Cuenta Principal", 1)
        account_combo.addItem("Tarjeta de Crédito", 2)
        account_combo.addItem("Ahorros", 3)
        # Set current account
        for i in range(account_combo.count()):
            if account_combo.itemText(i) == account_name:
                account_combo.setCurrentIndex(i)
                break
        form_layout.addRow("Cuenta:", account_combo)
        
        # Type field
        type_combo = QComboBox()
        type_combo.addItem("Gasto", "expense")
        type_combo.addItem("Ingreso", "income")
        type_combo.addItem("Transferencia", "transfer")
        # Set current type based on amount prefix
        if amount_text.startswith("+"):
            type_combo.setCurrentIndex(1)  # Income
        elif amount_text.startswith("-"):
            type_combo.setCurrentIndex(0)  # Expense
        else:
            type_combo.setCurrentIndex(2)  # Transfer
        form_layout.addRow("Tipo:", type_combo)
        
        # Category field
        category_combo = QComboBox()
        # This would be populated with actual categories from the database
        category_combo.addItem("Alimentación", 1)
        category_combo.addItem("Transporte", 2)
        category_combo.addItem("Vivienda", 3)
        category_combo.addItem("Entretenimiento", 4)
        # Set current category
        for i in range(category_combo.count()):
            if category_combo.itemText(i) == category_name:
                category_combo.setCurrentIndex(i)
                break
        form_layout.addRow("Categoría:", category_combo)
        
        # Amount field
        amount_spin = QDoubleSpinBox()
        amount_spin.setRange(0, 1000000000)
        amount_spin.setDecimals(2)
        amount_spin.setSingleStep(100)
        # Set current amount (remove prefix and convert to float)
        amount_value = float(amount_text.replace("+", "").replace("-", ""))
        amount_spin.setValue(amount_value)
        form_layout.addRow("Monto:", amount_spin)
        
        # Date field
        date_edit = QDateEdit()
        date_edit.setCalendarPopup(True)
        # Parse date text
        try:
            date = QDate.fromString(date_text, "dd/MM/yyyy")
            date_edit.setDate(date)
        except:
            date_edit.setDate(QDate.currentDate())
        form_layout.addRow("Fecha:", date_edit)
        
        # Description field
        description_edit = QTextEdit()
        description_edit.setMaximumHeight(100)
        description_edit.setText(description)
        form_layout.addRow("Descripción:", description_edit)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        if dialog.exec_() == QDialog.Accepted:
            # Create transaction data dictionary
            transaction_data = {
                'id': transaction_id,
                'account_id': account_combo.currentData(),
                'type': type_combo.currentData(),
                'category_id': category_combo.currentData(),
                'amount': amount_spin.value(),
                'date': date_edit.date().toString("yyyy-MM-dd"),
                'description': description_edit.toPlainText() if description_edit.toPlainText() else None
            }
            
            # Emit signal with transaction data
            self.edit_transaction_requested.emit(transaction_id, transaction_data)
    
    def delete_transaction(self, transaction_id):
        """Delete a transaction.
        
        Args:
            transaction_id (int): ID of the transaction to delete
        """
        # Show confirmation dialog
        confirm = QMessageBox.question(
            self,
            "Confirmar eliminación",
            "¿Está seguro de que desea eliminar esta transacción? Esta acción no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            # Emit signal to delete the transaction
            self.delete_transaction_requested.emit(transaction_id)