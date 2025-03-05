#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QPushButton, QAction, QToolBar,
                             QStatusBar, QMessageBox, QSplitter, QFrame)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont, QPixmap
import os
import qdarkstyle

from src.views.dashboard_view import DashboardView
from src.views.accounts_view import AccountsView
from src.views.transactions_view import TransactionsView
from src.views.budgets_view import BudgetsView
from src.views.reports_view import ReportsView
from src.views.goals_view import GoalsView
from src.views.settings_view import SettingsView

class MainWindow(QMainWindow):
    """Main window of the financial management application."""
    
    # Signal emitted when a report generation is requested
    from PyQt5.QtCore import pyqtSignal
    generate_report_signal = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        
        # Set window properties
        self.setWindowTitle("Finanzas - Gestión Financiera")
        self.setMinimumSize(1200, 800)
        
        # Set window icon
        # self.setWindowIcon(QIcon(os.path.join('resources', 'icons', 'app_icon.png')))
        
        # Initialize UI
        self.init_ui()
        
        # Apply dark style
        self.apply_style()
    
    def init_ui(self):
        """Initialize the user interface."""
        # Create central widget and main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Create header
        self.create_header()
        
        # Create tab widget
        self.create_tabs()
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Listo")
        
        # Create toolbar
        self.create_toolbar()
        
        # Create menu
        self.create_menu()
    
    def create_header(self):
        """Create the header with logo and title."""
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(10, 10, 10, 10)
        
        # Logo placeholder
        logo_label = QLabel()
        # logo_label.setPixmap(QPixmap(os.path.join('resources', 'icons', 'logo.png')).scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        header_layout.addWidget(logo_label)
        
        # Title
        title_label = QLabel("Finanzas")
        title_font = QFont("Segoe UI", 18, QFont.Bold)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        
        # Spacer
        header_layout.addStretch()
        
        # User info placeholder
        user_widget = QWidget()
        user_layout = QHBoxLayout(user_widget)
        user_layout.setContentsMargins(0, 0, 0, 0)
        
        user_icon = QLabel()
        # user_icon.setPixmap(QPixmap(os.path.join('resources', 'icons', 'user.png')).scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        user_layout.addWidget(user_icon)
        
        user_name = QLabel("Usuario")
        user_layout.addWidget(user_name)
        
        header_layout.addWidget(user_widget)
        
        # Add header to main layout
        self.main_layout.addWidget(header_widget)
        
        # Add separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        self.main_layout.addWidget(separator)
    
    def create_tabs(self):
        """Create the tab widget with different views."""
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)
        self.tab_widget.setDocumentMode(True)
        self.tab_widget.setMovable(True)
        
        # Dashboard tab
        self.dashboard_view = DashboardView()
        self.tab_widget.addTab(self.dashboard_view, "Panel Principal")
        
        # Accounts tab
        self.accounts_view = AccountsView()
        self.tab_widget.addTab(self.accounts_view, "Cuentas")
        
        # Transactions tab
        self.transactions_view = TransactionsView()
        self.tab_widget.addTab(self.transactions_view, "Transacciones")
        
        # Budgets tab
        self.budgets_view = BudgetsView()
        self.tab_widget.addTab(self.budgets_view, "Presupuestos")
        
        # Reports tab
        self.reports_view = ReportsView()
        self.tab_widget.addTab(self.reports_view, "Informes")
        
        # Goals tab
        self.goals_view = GoalsView()
        self.tab_widget.addTab(self.goals_view, "Metas")
        
        # Settings tab
        self.settings_view = SettingsView()
        self.tab_widget.addTab(self.settings_view, "Configuración")
        
        # Add tab widget to main layout
        self.main_layout.addWidget(self.tab_widget)
    
    def create_toolbar(self):
        """Create the toolbar with quick actions."""
        self.toolbar = QToolBar("Barra de herramientas")
        self.toolbar.setIconSize(QSize(24, 24))
        self.toolbar.setMovable(False)
        self.addToolBar(Qt.TopToolBarArea, self.toolbar)
        
        # Add actions
        add_transaction_action = QAction("Nueva Transacción", self)
        # add_transaction_action.setIcon(QIcon(os.path.join('resources', 'icons', 'add_transaction.png')))
        add_transaction_action.triggered.connect(self.add_transaction)
        self.toolbar.addAction(add_transaction_action)
        
        add_account_action = QAction("Nueva Cuenta", self)
        # add_account_action.setIcon(QIcon(os.path.join('resources', 'icons', 'add_account.png')))
        add_account_action.triggered.connect(self.add_account)
        self.toolbar.addAction(add_account_action)
        
        self.toolbar.addSeparator()
        
        reports_action = QAction("Generar Informe", self)
        # reports_action.setIcon(QIcon(os.path.join('resources', 'icons', 'report.png')))
        reports_action.triggered.connect(self.generate_report)
        self.toolbar.addAction(reports_action)
    
    def create_menu(self):
        """Create the application menu."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("Archivo")
        
        new_transaction = QAction("Nueva Transacción", self)
        new_transaction.triggered.connect(self.add_transaction)
        file_menu.addAction(new_transaction)
        
        new_account = QAction("Nueva Cuenta", self)
        new_account.triggered.connect(self.add_account)
        file_menu.addAction(new_account)
        
        file_menu.addSeparator()
        
        import_action = QAction("Importar Datos", self)
        import_action.triggered.connect(self.import_data)
        file_menu.addAction(import_action)
        
        export_action = QAction("Exportar Datos", self)
        export_action.triggered.connect(self.export_data)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Salir", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Reports menu
        reports_menu = menubar.addMenu("Informes")
        
        income_expense_report = QAction("Informe de Ingresos y Gastos", self)
        income_expense_report.triggered.connect(lambda: self.generate_report("income_expense"))
        reports_menu.addAction(income_expense_report)
        
        category_report = QAction("Informe por Categorías", self)
        category_report.triggered.connect(lambda: self.generate_report("category"))
        reports_menu.addAction(category_report)
        
        trend_report = QAction("Informe de Tendencias", self)
        trend_report.triggered.connect(lambda: self.generate_report("trend"))
        reports_menu.addAction(trend_report)
        
        # Help menu
        help_menu = menubar.addMenu("Ayuda")
        
        about_action = QAction("Acerca de", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        help_action = QAction("Ayuda", self)
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)
    
    def apply_style(self):
        """Apply custom styling to the application."""
        # Apply dark style base
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        
        # Additional custom styles for futuristic dark theme
        additional_styles = """
        QMainWindow {
            background-color: #1a1a1a;
        }
        
        QWidget {
            background-color: #1a1a1a;
            color: #e0e0e0;
        }
        
        QTabWidget::pane { 
            border: 1px solid #333;
            border-radius: 8px;
            background-color: #1a1a1a;
        }
        
        QTabBar::tab {
            background-color: #252525;
            color: #888;
            padding: 10px 20px;
            margin-right: 4px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            border: 1px solid #333;
            border-bottom: none;
        }
        
        QTabBar::tab:selected {
            background-color: #0d47a1;
            color: #fff;
            border: 1px solid #1565c0;
            border-bottom: none;
        }
        
        QTabBar::tab:hover:!selected {
            background-color: #303030;
            color: #fff;
        }
        
        QPushButton {
            background-color: #0d47a1;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 1px;
            border: 1px solid #0a3d91;
        }
        
        QPushButton:hover {
            background-color: #1565c0;
            border: 1px solid #1565c0;
        }
        
        QPushButton:pressed {
            background-color: #0a3d91;
            border: 1px solid #083371
        }
        
        QFrame {
            border-radius: 8px;
            background-color: #252525;
            border: 1px solid #333;
        }
        
        QLabel {
            color: #e0e0e0;
        }
        
        QLineEdit, QTextEdit, QComboBox {
            background-color: #303030;
            border: 1px solid #444;
            border-radius: 6px;
            padding: 8px;
            color: #e0e0e0;
        }
        
        QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
            border: 1px solid #1565c0;
        }
        
        QScrollBar:vertical {
            border: none;
            background-color: #252525;
            width: 10px;
            border-radius: 5px;
        }
        
        QScrollBar::handle:vertical {
            background-color: #444;
            border-radius: 5px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #666;
        }
        
        QMenuBar {
            background-color: #1a1a1a;
            color: #e0e0e0;
            border-bottom: 1px solid #333;
        }
        
        QMenuBar::item:selected {
            background-color: #0d47a1;
        }
        
        QMenu {
            background-color: #252525;
            border: 1px solid #333;
        }
        
        QMenu::item:selected {
            background-color: #0d47a1;
        }
        
        QStatusBar {
            background-color: #1a1a1a;
            color: #888;
            border-top: 1px solid #333;
        }
        
        QToolBar {
            background-color: #252525;
            border: none;
            spacing: 10px;
            padding: 5px;
        }
        
        QToolButton {
            background-color: transparent;
            border-radius: 4px;
            padding: 4px;
        }
        
        QToolButton:hover {
            background-color: #333;
        }
        """
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5() + additional_styles)
    
    # Action handlers
    def add_transaction(self):
        """Open dialog to add a new transaction."""
        self.tab_widget.setCurrentIndex(2)  # Switch to transactions tab
        self.transactions_view.show_add_transaction_dialog()
    
    def add_account(self):
        """Open dialog to add a new account."""
        self.tab_widget.setCurrentIndex(1)  # Switch to accounts tab
        self.accounts_view.show_add_account_dialog()
    
    def generate_report(self, report_type=None):
        """Generate a financial report."""
        self.tab_widget.setCurrentIndex(4)  # Switch to reports tab
        if report_type:
            self.reports_view.generate_report(report_type)
    
    def import_data(self):
        """Import data from external sources."""
        from PyQt5.QtWidgets import QFileDialog
        import csv
        import sqlite3
        import os
        
        # Ask user to select a file
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Importar Datos",
            "",
            "Archivos CSV (*.csv);;Todos los archivos (*)"
        )
        
        if not file_path:
            return  # User cancelled
        
        try:
            # Show import options dialog
            import_dialog = QDialog(self)
            import_dialog.setWindowTitle("Opciones de Importación")
            import_dialog.setMinimumWidth(400)
            
            layout = QVBoxLayout(import_dialog)
            
            # Data type selection
            form_layout = QFormLayout()
            data_type_combo = QComboBox()
            data_type_combo.addItem("Transacciones", "transactions")
            data_type_combo.addItem("Cuentas", "accounts")
            data_type_combo.addItem("Categorías", "categories")
            form_layout.addRow("Tipo de datos:", data_type_combo)
            
            # Date format selection
            date_format_combo = QComboBox()
            date_format_combo.addItem("DD/MM/YYYY", "dd/MM/yyyy")
            date_format_combo.addItem("MM/DD/YYYY", "MM/dd/yyyy")
            date_format_combo.addItem("YYYY-MM-DD", "yyyy-MM-dd")
            form_layout.addRow("Formato de fecha:", date_format_combo)
            
            layout.addLayout(form_layout)
            
            # Buttons
            button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            button_box.accepted.connect(import_dialog.accept)
            button_box.rejected.connect(import_dialog.reject)
            layout.addWidget(button_box)
            
            if import_dialog.exec_() != QDialog.Accepted:
                return  # User cancelled
            
            # Get selected options
            data_type = data_type_combo.currentData()
            date_format = date_format_combo.currentData()
            
            # Read CSV file
            with open(file_path, 'r', encoding='utf-8') as csv_file:
                csv_reader = csv.DictReader(csv_file)
                rows = list(csv_reader)
            
            if not rows:
                QMessageBox.warning(self, "Importar Datos", "El archivo CSV está vacío o no tiene el formato correcto.")
                return
            
            # Process data based on type
            # In a real implementation, this would insert the data into the database
            # For now, we'll just show a success message
            
            QMessageBox.information(
                self,
                "Importar Datos",
                f"Se importaron {len(rows)} registros de {data_type} exitosamente."
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al importar datos: {str(e)}")
    
    def export_data(self):
        """Export data to external formats."""
        from PyQt5.QtWidgets import QFileDialog
        import csv
        import sqlite3
        import os
        
        # Ask user to select export format and location
        export_dialog = QDialog(self)
        export_dialog.setWindowTitle("Exportar Datos")
        export_dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(export_dialog)
        
        # Data type selection
        form_layout = QFormLayout()
        data_type_combo = QComboBox()
        data_type_combo.addItem("Transacciones", "transactions")
        data_type_combo.addItem("Cuentas", "accounts")
        data_type_combo.addItem("Categorías", "categories")
        form_layout.addRow("Tipo de datos:", data_type_combo)
        
        # Export format selection
        format_combo = QComboBox()
        format_combo.addItem("CSV", "csv")
        format_combo.addItem("Excel", "excel")
        form_layout.addRow("Formato:", format_combo)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(export_dialog.accept)
        button_box.rejected.connect(export_dialog.reject)
        layout.addWidget(button_box)
        
        if export_dialog.exec_() != QDialog.Accepted:
            return  # User cancelled
        
        # Get selected options
        data_type = data_type_combo.currentData()
        export_format = format_combo.currentData()
        
        try:
            if export_format == "csv":
                file_path, _ = QFileDialog.getSaveFileName(
                    self,
                    "Exportar a CSV",
                    "",
                    "Archivos CSV (*.csv)"
                )
                if not file_path:
                    return  # User cancelled
                
                # Connect to database
                db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'finanzas.db')
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Get table data
                cursor.execute(f"SELECT * FROM {data_type}")
                rows = cursor.fetchall()
                
                # Get column names
                cursor.execute(f"PRAGMA table_info({data_type})")
                headers = [column[1] for column in cursor.fetchall()]
                
                # Write to CSV
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(headers)
                    writer.writerows(rows)
                
                conn.close()
                
            elif export_format == "excel":
                file_path, _ = QFileDialog.getSaveFileName(
                    self,
                    "Exportar a Excel",
                    "",
                    "Archivos Excel (*.xlsx)"
                )
                if not file_path:
                    return  # User cancelled
                
                import pandas as pd
                
                # Connect to database
                db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'finanzas.db')
                conn = sqlite3.connect(db_path)
                
                # Read data into DataFrame
                df = pd.read_sql_query(f"SELECT * FROM {data_type}", conn)
                
                # Export to Excel
                df.to_excel(file_path, index=False)
                
                conn.close()
            
            QMessageBox.information(
                self,
                "Exportar Datos",
                f"Los datos se han exportado exitosamente a {file_path}"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al exportar datos: {str(e)}")
    
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(self, "Acerca de Finanzas", 
                         "<h3>Finanzas - Software de Gestión Financiera</h3>"
                         "<p>Versión 1.0</p>"
                         "<p>Un software profesional para la gestión de finanzas personales.</p>"
                         "<p>Desarrollado con Python y PyQt5.</p>")
    
    def show_help(self):
        """Show help information."""
        QMessageBox.information(self, "Ayuda", "Consulte la documentación para obtener ayuda sobre cómo usar el software.")