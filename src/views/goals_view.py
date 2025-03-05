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

class GoalsView(QWidget):
    """Goals view showing all financial goals and their details."""
    
    # Signal emitted when user requests to add a new goal
    add_goal_requested = pyqtSignal(dict)
    
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
        title_label = QLabel("Metas Financieras")
        title_font = QFont("Segoe UI", 16, QFont.Bold)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        
        # Spacer
        header_layout.addStretch()
        
        # Add goal button
        self.add_goal_btn = QPushButton("Nueva Meta")
        self.add_goal_btn.clicked.connect(self.show_add_goal_dialog)
        header_layout.addWidget(self.add_goal_btn)
        
        main_layout.addLayout(header_layout)
        
        # Goals table
        self.goals_table = QTableWidget()
        self.goals_table.setColumnCount(6)
        self.goals_table.setHorizontalHeaderLabels(["Nombre", "Objetivo", "Actual", "Fecha Límite", "Progreso", "Acciones"])
        self.goals_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.goals_table.setAlternatingRowColors(True)
        self.goals_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.goals_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.goals_table.setSelectionMode(QTableWidget.SingleSelection)
        
        main_layout.addWidget(self.goals_table)
    
    def load_goals(self, goals):
        """Load goals data into the table.
        
        Args:
            goals (list): List of goal dictionaries
        """
        self.goals_table.setRowCount(0)  # Clear existing rows
        
        if not goals:
            return
        
        for row, goal in enumerate(goals):
            self.goals_table.insertRow(row)
            
            # Name
            name_item = QTableWidgetItem(goal['name'])
            self.goals_table.setItem(row, 0, name_item)
            
            # Target amount
            target_item = QTableWidgetItem(f"{goal['target_amount']:.2f}")
            target_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.goals_table.setItem(row, 1, target_item)
            
            # Current amount
            current_item = QTableWidgetItem(f"{goal['current_amount']:.2f}")
            current_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.goals_table.setItem(row, 2, current_item)
            
            # Deadline
            deadline_str = goal.get('deadline', '')
            if deadline_str:
                if isinstance(deadline_str, str):
                    deadline_obj = datetime.strptime(deadline_str, '%Y-%m-%d')
                    deadline_display = deadline_obj.strftime('%d/%m/%Y')
                else:
                    deadline_display = deadline_str.strftime('%d/%m/%Y')
                deadline_item = QTableWidgetItem(deadline_display)
            else:
                deadline_item = QTableWidgetItem("Sin fecha límite")
            self.goals_table.setItem(row, 3, deadline_item)
            
            # Progress
            progress_widget = QWidget()
            progress_layout = QVBoxLayout(progress_widget)
            progress_layout.setContentsMargins(4, 4, 4, 4)
            
            # Calculate progress percentage
            if goal['target_amount'] > 0:
                progress_value = min(100, int((goal['current_amount'] / goal['target_amount']) * 100))
            else:
                progress_value = 0
            
            progress_bar = QProgressBar()
            progress_bar.setRange(0, 100)
            progress_bar.setValue(progress_value)
            progress_bar.setTextVisible(True)
            progress_bar.setFormat("%p%")
            
            # Set color based on progress
            if progress_value < 33:
                progress_bar.setStyleSheet("QProgressBar::chunk { background-color: #DC3545; }")
            elif progress_value < 66:
                progress_bar.setStyleSheet("QProgressBar::chunk { background-color: #FFC107; }")
            else:
                progress_bar.setStyleSheet("QProgressBar::chunk { background-color: #28A745; }")
                
            progress_layout.addWidget(progress_bar)
            self.goals_table.setCellWidget(row, 4, progress_widget)
            
            # Actions
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(4, 4, 4, 4)
            actions_layout.setSpacing(4)
            
            edit_btn = QPushButton("Editar")
            edit_btn.setProperty("goal_id", goal['id'])
            edit_btn.clicked.connect(lambda checked, gid=goal['id']: self.edit_goal(gid))
            actions_layout.addWidget(edit_btn)
            
            delete_btn = QPushButton("Eliminar")
            delete_btn.setProperty("goal_id", goal['id'])
            delete_btn.clicked.connect(lambda checked, gid=goal['id']: self.delete_goal(gid))
            actions_layout.addWidget(delete_btn)
            
            actions_widget = QWidget()
            actions_widget.setLayout(actions_layout)
            self.goals_table.setCellWidget(row, 5, actions_widget)
    
    def show_add_goal_dialog(self):
        """Show dialog to add a new goal."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Nueva Meta Financiera")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # Name field
        name_edit = QLineEdit()
        form_layout.addRow("Nombre:", name_edit)
        
        # Target amount field
        target_spin = QDoubleSpinBox()
        target_spin.setRange(0, 1000000000)
        target_spin.setDecimals(2)
        target_spin.setSingleStep(1000)
        form_layout.addRow("Monto Objetivo:", target_spin)
        
        # Current amount field
        current_spin = QDoubleSpinBox()
        current_spin.setRange(0, 1000000000)
        current_spin.setDecimals(2)
        current_spin.setSingleStep(100)
        form_layout.addRow("Monto Actual:", current_spin)
        
        # Deadline field
        deadline_edit = QDateEdit()
        deadline_edit.setCalendarPopup(True)
        deadline_edit.setDate(QDate.currentDate().addMonths(6))
        form_layout.addRow("Fecha Límite:", deadline_edit)
        
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
            # Create goal data dictionary
            goal_data = {
                'name': name_edit.text(),
                'target_amount': target_spin.value(),
                'current_amount': current_spin.value(),
                'deadline': deadline_edit.date().toString("yyyy-MM-dd"),
                'description': description_edit.toPlainText() if description_edit.toPlainText() else None
            }
            
            # Emit signal with goal data
            self.add_goal_requested.emit(goal_data)
    
    # Signal emitted when user requests to edit a goal
    edit_goal_requested = pyqtSignal(int, dict)
    
    # Signal emitted when user requests to delete a goal
    delete_goal_requested = pyqtSignal(int)
    
    def edit_goal(self, goal_id):
        """Edit an existing goal.
        
        Args:
            goal_id (int): ID of the goal to edit
        """
        # Find the goal data in the table
        for row in range(self.goals_table.rowCount()):
            for col in range(self.goals_table.columnCount()):
                cell_widget = self.goals_table.cellWidget(row, 5)
                if cell_widget:
                    actions_layout = cell_widget.layout()
                    for i in range(actions_layout.count()):
                        button = actions_layout.itemAt(i).widget()
                        if button and button.property("goal_id") == goal_id and button.text() == "Editar":
                            # Found the goal, get its data
                            name = self.goals_table.item(row, 0).text()
                            target_amount = float(self.goals_table.item(row, 1).text())
                            current_amount = float(self.goals_table.item(row, 2).text())
                            deadline_text = self.goals_table.item(row, 3).text()
                            
                            # Show edit dialog
                            self.show_edit_goal_dialog(goal_id, name, target_amount, current_amount, deadline_text)
                            return
    
    def show_edit_goal_dialog(self, goal_id, name, target_amount, current_amount, deadline_text):
        """Show dialog to edit an existing goal.
        
        Args:
            goal_id (int): ID of the goal to edit
            name (str): Current name of the goal
            target_amount (float): Current target amount
            current_amount (float): Current saved amount
            deadline_text (str): Current deadline text
        """
        dialog = QDialog(self)
        dialog.setWindowTitle("Editar Meta Financiera")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # Name field
        name_edit = QLineEdit(name)
        form_layout.addRow("Nombre:", name_edit)
        
        # Target amount field
        target_spin = QDoubleSpinBox()
        target_spin.setRange(0, 1000000000)
        target_spin.setDecimals(2)
        target_spin.setSingleStep(1000)
        target_spin.setValue(target_amount)
        form_layout.addRow("Monto Objetivo:", target_spin)
        
        # Current amount field
        current_spin = QDoubleSpinBox()
        current_spin.setRange(0, 1000000000)
        current_spin.setDecimals(2)
        current_spin.setSingleStep(100)
        current_spin.setValue(current_amount)
        form_layout.addRow("Monto Actual:", current_spin)
        
        # Deadline field
        deadline_edit = QDateEdit()
        deadline_edit.setCalendarPopup(True)
        
        # Parse deadline text
        if deadline_text != "Sin fecha límite":
            try:
                deadline_date = QDate.fromString(deadline_text, "dd/MM/yyyy")
                deadline_edit.setDate(deadline_date)
            except:
                deadline_edit.setDate(QDate.currentDate().addMonths(6))
        else:
            deadline_edit.setDate(QDate.currentDate().addMonths(6))
            
        form_layout.addRow("Fecha Límite:", deadline_edit)
        
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
            # Create goal data dictionary
            goal_data = {
                'name': name_edit.text(),
                'target_amount': target_spin.value(),
                'current_amount': current_spin.value(),
                'deadline': deadline_edit.date().toString("yyyy-MM-dd"),
                'description': description_edit.toPlainText() if description_edit.toPlainText() else None
            }
            
            # Emit signal with goal data
            self.edit_goal_requested.emit(goal_id, goal_data)
    
    def delete_goal(self, goal_id):
        """Delete a goal.
        
        Args:
            goal_id (int): ID of the goal to delete
        """
        # Show confirmation dialog
        confirm = QMessageBox.question(
            self,
            "Confirmar eliminación",
            "¿Está seguro de que desea eliminar esta meta financiera? Esta acción no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            # Emit signal to delete the goal
            self.delete_goal_requested.emit(goal_id)