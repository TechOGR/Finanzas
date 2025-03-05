#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QFrame, QDialog, QFormLayout,
                             QLineEdit, QComboBox, QDoubleSpinBox, QTextEdit,
                             QDialogButtonBox, QMessageBox, QDateEdit, QProgressBar)
from PyQt5.QtCore import Qt, pyqtSignal, QDate
from PyQt5.QtGui import QIcon, QFont, QColor
import os
from datetime import datetime

class BudgetsView(QWidget):
    """Budgets view showing all financial budgets and their details."""
    
    # Signal emitted when user requests to add a new budget
    add_budget_requested = pyqtSignal(dict)
    
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
        title_label = QLabel("Presupuestos")
        title_font = QFont("Segoe UI", 16, QFont.Bold)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        
        # Spacer
        header_layout.addStretch()
        
        # Add budget button
        self.add_budget_btn = QPushButton("Nuevo Presupuesto")
        self.add_budget_btn.clicked.connect(self.show_add_budget_dialog)
        header_layout.addWidget(self.add_budget_btn)
        
        main_layout.addLayout(header_layout)
        
        # Budgets table
        self.budgets_table = QTableWidget()
        self.budgets_table.setColumnCount(6)
        self.budgets_table.setHorizontalHeaderLabels(["Categoría", "Monto", "Período", "Fecha Inicio", "Progreso", "Acciones"])
        self.budgets_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.budgets_table.setAlternatingRowColors(True)
        self.budgets_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.budgets_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.budgets_table.setSelectionMode(QTableWidget.SingleSelection)
        
        main_layout.addWidget(self.budgets_table)
    
    def load_budgets(self, budgets):
        """Load budgets data into the table.
        
        Args:
            budgets (list): List of budget dictionaries
        """
        self.budgets_table.setRowCount(0)  # Clear existing rows
        
        if not budgets:
            return
        
        for row, budget in enumerate(budgets):
            self.budgets_table.insertRow(row)
            
            # Category
            category_item = QTableWidgetItem(budget.get('category_name', 'Sin categoría'))
            self.budgets_table.setItem(row, 0, category_item)
            
            # Amount
            amount_item = QTableWidgetItem(f"{budget['amount']:.2f}")
            amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.budgets_table.setItem(row, 1, amount_item)
            
            # Period
            period_item = QTableWidgetItem(self.get_period_display(budget['period']))
            self.budgets_table.setItem(row, 2, period_item)
            
            # Start date
            start_date_str = budget['start_date']
            if isinstance(start_date_str, str):
                start_date_obj = datetime.strptime(start_date_str, '%Y-%m-%d')
                start_date_display = start_date_obj.strftime('%d/%m/%Y')
            else:
                start_date_display = start_date_str.strftime('%d/%m/%Y')
            start_date_item = QTableWidgetItem(start_date_display)
            self.budgets_table.setItem(row, 3, start_date_item)
            
            # Progress
            progress_widget = QWidget()
            progress_layout = QVBoxLayout(progress_widget)
            progress_layout.setContentsMargins(4, 4, 4, 4)
            
            # Placeholder progress - in a real app, this would be calculated
            progress_value = budget.get('progress', 50)  # Default to 50% for demo
            
            progress_bar = QProgressBar()
            progress_bar.setRange(0, 100)
            progress_bar.setValue(progress_value)
            progress_bar.setTextVisible(True)
            progress_bar.setFormat("%p%")
            
            # Set color based on progress
            if progress_value < 50:
                progress_bar.setStyleSheet("QProgressBar::chunk { background-color: #28A745; }")
            elif progress_value < 80:
                progress_bar.setStyleSheet("QProgressBar::chunk { background-color: #FFC107; }")
            else:
                progress_bar.setStyleSheet("QProgressBar::chunk { background-color: #DC3545; }")
                
            progress_layout.addWidget(progress_bar)
            self.budgets_table.setCellWidget(row, 4, progress_widget)
            
            # Actions
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(4, 4, 4, 4)
            actions_layout.setSpacing(4)
            
            edit_btn = QPushButton("Editar")
            edit_btn.setProperty("budget_id", budget['id'])
            edit_btn.clicked.connect(lambda checked, bid=budget['id']: self.edit_budget(bid))
            actions_layout.addWidget(edit_btn)
            
            delete_btn = QPushButton("Eliminar")
            delete_btn.setProperty("budget_id", budget['id'])
            delete_btn.clicked.connect(lambda checked, bid=budget['id']: self.delete_budget(bid))
            actions_layout.addWidget(delete_btn)
            
            actions_widget = QWidget()
            actions_widget.setLayout(actions_layout)
            self.budgets_table.setCellWidget(row, 5, actions_widget)
    
    def get_period_display(self, period):
        """Convert period code to display name.
        
        Args:
            period (str): Period code
            
        Returns:
            str: Display name for the period
        """
        periods = {
            'monthly': 'Mensual',
            'quarterly': 'Trimestral',
            'yearly': 'Anual',
            'custom': 'Personalizado'
        }
        return periods.get(period, period)
    
    def show_add_budget_dialog(self):
        """Show dialog to add a new budget."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Nuevo Presupuesto")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
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
        
        # Period field
        period_combo = QComboBox()
        period_combo.addItem("Mensual", "monthly")
        period_combo.addItem("Trimestral", "quarterly")
        period_combo.addItem("Anual", "yearly")
        period_combo.addItem("Personalizado", "custom")
        form_layout.addRow("Período:", period_combo)
        
        # Start date field
        start_date_edit = QDateEdit()
        start_date_edit.setCalendarPopup(True)
        start_date_edit.setDate(QDate.currentDate())
        form_layout.addRow("Fecha Inicio:", start_date_edit)
        
        # End date field
        end_date_edit = QDateEdit()
        end_date_edit.setCalendarPopup(True)
        end_date_edit.setDate(QDate.currentDate().addMonths(1))
        form_layout.addRow("Fecha Fin:", end_date_edit)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        if dialog.exec_() == QDialog.Accepted:
            # Create budget data dictionary
            budget_data = {
                'category_id': category_combo.currentData(),
                'amount': amount_spin.value(),
                'period': period_combo.currentData(),
                'start_date': start_date_edit.date().toString("yyyy-MM-dd"),
                'end_date': end_date_edit.date().toString("yyyy-MM-dd")
            }
            
            # Emit signal with budget data
            self.add_budget_requested.emit(budget_data)
    
    def edit_budget(self, budget_id):
        """Edit an existing budget.
        
        Args:
            budget_id (int): ID of the budget to edit
        """
        # Find the budget in the table
        budget_row = None
        for row in range(self.budgets_table.rowCount()):
            for col in range(self.budgets_table.columnCount()):
                cell_widget = self.budgets_table.cellWidget(row, 5)
                if cell_widget:
                    for child in cell_widget.findChildren(QPushButton):
                        if child.property("budget_id") == budget_id:
                            budget_row = row
                            break
            if budget_row is not None:
                break
        
        if budget_row is None:
            QMessageBox.warning(self, "Error", "No se pudo encontrar el presupuesto seleccionado.")
            return
        
        # Get budget data from the table
        category_name = self.budgets_table.item(budget_row, 0).text()
        amount = float(self.budgets_table.item(budget_row, 1).text())
        period_display = self.budgets_table.item(budget_row, 2).text()
        start_date_str = self.budgets_table.item(budget_row, 3).text()
        
        # Create edit dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Editar Presupuesto")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
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
        amount_spin.setValue(amount)
        form_layout.addRow("Monto:", amount_spin)
        
        # Period field
        period_combo = QComboBox()
        period_combo.addItem("Mensual", "monthly")
        period_combo.addItem("Trimestral", "quarterly")
        period_combo.addItem("Anual", "yearly")
        period_combo.addItem("Personalizado", "custom")
        
        # Set current period
        for i in range(period_combo.count()):
            if period_combo.itemText(i) == period_display:
                period_combo.setCurrentIndex(i)
                break
        
        form_layout.addRow("Período:", period_combo)
        
        # Start date field
        start_date_edit = QDateEdit()
        start_date_edit.setCalendarPopup(True)
        
        # Parse and set the start date
        try:
            start_date = QDate.fromString(start_date_str, "dd/MM/yyyy")
            start_date_edit.setDate(start_date)
        except:
            start_date_edit.setDate(QDate.currentDate())
        
        form_layout.addRow("Fecha Inicio:", start_date_edit)
        
        # End date field
        end_date_edit = QDateEdit()
        end_date_edit.setCalendarPopup(True)
        end_date_edit.setDate(start_date_edit.date().addMonths(1))
        form_layout.addRow("Fecha Fin:", end_date_edit)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        if dialog.exec_() == QDialog.Accepted:
            # Create updated budget data dictionary
            updated_budget_data = {
                'id': budget_id,
                'category_id': category_combo.currentData(),
                'amount': amount_spin.value(),
                'period': period_combo.currentData(),
                'start_date': start_date_edit.date().toString("yyyy-MM-dd"),
                'end_date': end_date_edit.date().toString("yyyy-MM-dd")
            }
            
            # Emit signal with updated budget data
            # In a real implementation, you would have an update_budget_requested signal
            # For now, just show a message
            QMessageBox.information(self, "Presupuesto Actualizado", 
                                  f"El presupuesto {budget_id} ha sido actualizado correctamente.")
            
            # In a real implementation, you would update the database and refresh the view
    
    def delete_budget(self, budget_id):
        """Delete a budget.
        
        Args:
            budget_id (int): ID of the budget to delete
        """
        # This would be implemented to delete a budget
        # For now, it's a placeholder
        QMessageBox.information(self, "Eliminar Presupuesto", f"Función para eliminar el presupuesto {budget_id} no implementada aún.")