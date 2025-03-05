#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFormLayout, QComboBox, QCheckBox,
                             QFrame, QTabWidget, QLineEdit, QMessageBox,
                             QDialogButtonBox, QFileDialog, QGroupBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
import os

class SettingsView(QWidget):
    """Settings view for application configuration."""
    
    # Signal emitted when settings are saved
    settings_saved = pyqtSignal(dict)
    
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
        title_label = QLabel("Configuración")
        title_font = QFont("Segoe UI", 16, QFont.Bold)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        
        # Spacer
        header_layout.addStretch()
        
        # Save settings button
        self.save_btn = QPushButton("Guardar Cambios")
        self.save_btn.clicked.connect(self.save_settings)
        header_layout.addWidget(self.save_btn)
        
        main_layout.addLayout(header_layout)
        
        # Settings tabs
        self.settings_tabs = QTabWidget()
        
        # General settings tab
        self.general_tab = self.create_general_tab()
        self.settings_tabs.addTab(self.general_tab, "General")
        
        # Appearance tab
        self.appearance_tab = self.create_appearance_tab()
        self.settings_tabs.addTab(self.appearance_tab, "Apariencia")
        
        # Data tab
        self.data_tab = self.create_data_tab()
        self.settings_tabs.addTab(self.data_tab, "Datos")
        
        # Currency tab
        self.currency_tab = self.create_currency_tab()
        self.settings_tabs.addTab(self.currency_tab, "Monedas")
        
        main_layout.addWidget(self.settings_tabs)
    
    def create_general_tab(self):
        """Create general settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Language settings
        language_group = QGroupBox("Idioma")
        language_layout = QFormLayout(language_group)
        
        self.language_combo = QComboBox()
        self.language_combo.addItem("Español", "es")
        self.language_combo.addItem("English", "en")
        language_layout.addRow("Idioma de la aplicación:", self.language_combo)
        
        layout.addWidget(language_group)
        
        # Startup settings
        startup_group = QGroupBox("Inicio")
        startup_layout = QVBoxLayout(startup_group)
        
        self.start_with_system = QCheckBox("Iniciar con el sistema")
        startup_layout.addWidget(self.start_with_system)
        
        self.show_dashboard_startup = QCheckBox("Mostrar panel principal al iniciar")
        self.show_dashboard_startup.setChecked(True)
        startup_layout.addWidget(self.show_dashboard_startup)
        
        layout.addWidget(startup_group)
        
        # Notifications settings
        notifications_group = QGroupBox("Notificaciones")
        notifications_layout = QVBoxLayout(notifications_group)
        
        self.enable_notifications = QCheckBox("Habilitar notificaciones")
        self.enable_notifications.setChecked(True)
        notifications_layout.addWidget(self.enable_notifications)
        
        self.budget_alerts = QCheckBox("Alertas de presupuesto")
        self.budget_alerts.setChecked(True)
        notifications_layout.addWidget(self.budget_alerts)
        
        self.goal_alerts = QCheckBox("Alertas de metas financieras")
        self.goal_alerts.setChecked(True)
        notifications_layout.addWidget(self.goal_alerts)
        
        layout.addWidget(notifications_group)
        
        # Add spacer
        layout.addStretch()
        
        return tab
    
    def create_appearance_tab(self):
        """Create appearance settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Theme settings
        theme_group = QGroupBox("Tema")
        theme_layout = QFormLayout(theme_group)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItem("Oscuro", "dark")
        self.theme_combo.addItem("Claro", "light")
        self.theme_combo.addItem("Sistema", "system")
        theme_layout.addRow("Tema de la aplicación:", self.theme_combo)
        
        layout.addWidget(theme_group)
        
        # Font settings
        font_group = QGroupBox("Fuente")
        font_layout = QFormLayout(font_group)
        
        self.font_combo = QComboBox()
        self.font_combo.addItem("Segoe UI", "Segoe UI")
        self.font_combo.addItem("Arial", "Arial")
        self.font_combo.addItem("Roboto", "Roboto")
        font_layout.addRow("Fuente:", self.font_combo)
        
        self.font_size_combo = QComboBox()
        self.font_size_combo.addItem("Pequeño", "small")
        self.font_size_combo.addItem("Mediano", "medium")
        self.font_size_combo.addItem("Grande", "large")
        font_layout.addRow("Tamaño de fuente:", self.font_size_combo)
        
        layout.addWidget(font_group)
        
        # Add spacer
        layout.addStretch()
        
        return tab
    
    def create_data_tab(self):
        """Create data settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Backup settings
        backup_group = QGroupBox("Copia de seguridad")
        backup_layout = QVBoxLayout(backup_group)
        
        backup_btn_layout = QHBoxLayout()
        self.backup_btn = QPushButton("Crear copia de seguridad")
        self.backup_btn.clicked.connect(self.create_backup)
        backup_btn_layout.addWidget(self.backup_btn)
        
        self.restore_btn = QPushButton("Restaurar copia de seguridad")
        self.restore_btn.clicked.connect(self.restore_backup)
        backup_btn_layout.addWidget(self.restore_btn)
        
        backup_layout.addLayout(backup_btn_layout)
        
        self.auto_backup = QCheckBox("Crear copia de seguridad automática")
        backup_layout.addWidget(self.auto_backup)
        
        layout.addWidget(backup_group)
        
        # Data export settings
        export_group = QGroupBox("Exportación de datos")
        export_layout = QVBoxLayout(export_group)
        
        export_btn_layout = QHBoxLayout()
        self.export_csv_btn = QPushButton("Exportar a CSV")
        self.export_csv_btn.clicked.connect(self.export_to_csv)
        export_btn_layout.addWidget(self.export_csv_btn)
        
        self.export_excel_btn = QPushButton("Exportar a Excel")
        self.export_excel_btn.clicked.connect(self.export_to_excel)
        export_btn_layout.addWidget(self.export_excel_btn)
        
        export_layout.addLayout(export_btn_layout)
        
        layout.addWidget(export_group)
        
        # Data cleanup
        cleanup_group = QGroupBox("Limpieza de datos")
        cleanup_layout = QVBoxLayout(cleanup_group)
        
        self.clear_data_btn = QPushButton("Limpiar todos los datos")
        self.clear_data_btn.clicked.connect(self.clear_all_data)
        self.clear_data_btn.setStyleSheet("background-color: #DC3545; color: white;")
        cleanup_layout.addWidget(self.clear_data_btn)
        
        layout.addWidget(cleanup_group)
        
        # Add spacer
        layout.addStretch()
        
        return tab
    
    def create_currency_tab(self):
        """Create currency settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Default currency
        currency_group = QGroupBox("Moneda predeterminada")
        currency_layout = QFormLayout(currency_group)
        
        self.default_currency_combo = QComboBox()
        self.default_currency_combo.addItem("MXN - Peso Mexicano", "MXN")
        self.default_currency_combo.addItem("USD - Dólar Estadounidense", "USD")
        self.default_currency_combo.addItem("EUR - Euro", "EUR")
        currency_layout.addRow("Moneda predeterminada:", self.default_currency_combo)
        
        layout.addWidget(currency_group)
        
        # Exchange rates
        exchange_group = QGroupBox("Tasas de cambio")
        exchange_layout = QFormLayout(exchange_group)
        
        self.update_rates_btn = QPushButton("Actualizar tasas de cambio")
        self.update_rates_btn.clicked.connect(self.update_exchange_rates)
        exchange_layout.addRow("Actualizar:", self.update_rates_btn)
        
        self.usd_rate = QLineEdit("20.50")
        exchange_layout.addRow("USD a MXN:", self.usd_rate)
        
        self.eur_rate = QLineEdit("24.30")
        exchange_layout.addRow("EUR a MXN:", self.eur_rate)
        
        layout.addWidget(exchange_group)
        
        # Add spacer
        layout.addStretch()
        
        return tab
    
    def save_settings(self):
        """Save all settings."""
        # Collect all settings
        settings = {
            'language': self.language_combo.currentData(),
            'start_with_system': self.start_with_system.isChecked(),
            'show_dashboard_startup': self.show_dashboard_startup.isChecked(),
            'enable_notifications': self.enable_notifications.isChecked(),
            'budget_alerts': self.budget_alerts.isChecked(),
            'goal_alerts': self.goal_alerts.isChecked(),
            'theme': self.theme_combo.currentData(),
            'font': self.font_combo.currentData(),
            'font_size': self.font_size_combo.currentData(),
            'auto_backup': self.auto_backup.isChecked(),
            'default_currency': self.default_currency_combo.currentData(),
            'usd_rate': float(self.usd_rate.text()),
            'eur_rate': float(self.eur_rate.text())
        }
        
        # Emit signal with settings data
        self.settings_saved.emit(settings)
        
        QMessageBox.information(self, "Configuración", "La configuración ha sido guardada correctamente.")
    
    def create_backup(self):
        """Create a backup of the database."""
        file_path, _ = QFileDialog.getSaveFileName(self, "Guardar copia de seguridad", "", "Archivos de base de datos (*.db)")
        if file_path:
            try:
                import shutil
                import os
                
                # Get the path to the current database file
                current_db = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'finanzas.db')
                
                # Create backup by copying the database file
                shutil.copy2(current_db, file_path)
                
                QMessageBox.information(self, "Copia de seguridad", "Copia de seguridad creada exitosamente.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al crear la copia de seguridad: {str(e)}")
    
    def restore_backup(self):
        """Restore a backup of the database."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Restaurar copia de seguridad", "", "Archivos de base de datos (*.db)")
        if file_path:
            try:
                import shutil
                import os
                
                # Get the path to the current database file
                current_db = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'finanzas.db')
                
                # Create a temporary backup of the current database
                temp_backup = current_db + '.temp'
                shutil.copy2(current_db, temp_backup)
                
                try:
                    # Restore the backup file
                    shutil.copy2(file_path, current_db)
                    os.remove(temp_backup)
                    QMessageBox.information(self, "Restaurar copia de seguridad", "Copia de seguridad restaurada exitosamente.")
                except Exception as e:
                    # If restoration fails, restore the temporary backup
                    shutil.copy2(temp_backup, current_db)
                    os.remove(temp_backup)
                    raise e
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al restaurar la copia de seguridad: {str(e)}")
    
    def export_to_csv(self):
        """Export data to CSV format."""
        file_path, _ = QFileDialog.getSaveFileName(self, "Exportar a CSV", "", "Archivos CSV (*.csv)")
        if file_path:
            try:
                import sqlite3
                import csv
                import os
                
                # Connect to the database
                db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'finanzas.db')
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Get all tables
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                
                # Export each table to a separate CSV file
                base_name, ext = os.path.splitext(file_path)
                for table in tables:
                    table_name = table[0]
                    table_file = f"{base_name}_{table_name}{ext}"
                    
                    # Get table data
                    cursor.execute(f"SELECT * FROM {table_name}")
                    rows = cursor.fetchall()
                    
                    # Get column names
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    headers = [column[1] for column in cursor.fetchall()]
                    
                    # Write to CSV
                    with open(table_file, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow(headers)
                        writer.writerows(rows)
                
                conn.close()
                QMessageBox.information(self, "Exportar a CSV", "Datos exportados exitosamente a CSV.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al exportar a CSV: {str(e)}")
    
    def export_to_excel(self):
        """Export data to Excel format."""
        file_path, _ = QFileDialog.getSaveFileName(self, "Exportar a Excel", "", "Archivos Excel (*.xlsx)")
        if file_path:
            try:
                import sqlite3
                import pandas as pd
                import os
                
                # Connect to the database
                db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'finanzas.db')
                conn = sqlite3.connect(db_path)
                
                # Get all tables
                tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table';", conn)
                
                # Create Excel writer object
                with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                    # Export each table to a separate sheet
                    for table_name in tables['name']:
                        # Read table data
                        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
                        
                        # Write to Excel sheet
                        df.to_excel(writer, sheet_name=table_name, index=False)
                
                conn.close()
                QMessageBox.information(self, "Exportar a Excel", "Datos exportados exitosamente a Excel.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al exportar a Excel: {str(e)}")
    
    def clear_all_data(self):
        """Clear all data from the database."""
        # Show confirmation dialog
        confirm = QMessageBox.warning(
            self,
            "Confirmar eliminación",
            "¿Está seguro de que desea eliminar TODOS los datos? Esta acción no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            try:
                import sqlite3
                import os
                
                # Connect to the database
                db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'finanzas.db')
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Get all tables
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                
                # Delete data from each table
                for table in tables:
                    table_name = table[0]
                    cursor.execute(f"DELETE FROM {table_name};")
                
                conn.commit()
                conn.close()
                
                QMessageBox.information(self, "Limpiar datos", "Todos los datos han sido eliminados exitosamente.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al limpiar los datos: {str(e)}")
    
    def update_exchange_rates(self):
        """Update currency exchange rates using an external API."""
        try:
            import requests
            import json
            
            # Use the ExchangeRate-API (you would need to sign up for an API key)
            API_KEY = "YOUR_API_KEY"  # Replace with your actual API key
            base_currency = "MXN"
            
            # Make API request
            response = requests.get(f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/{base_currency}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Update exchange rate fields
                self.usd_rate.setText(str(round(1 / data['conversion_rates']['USD'], 2)))
                self.eur_rate.setText(str(round(1 / data['conversion_rates']['EUR'], 2)))
                
                QMessageBox.information(self, "Actualizar tasas", "Tasas de cambio actualizadas exitosamente.")
            else:
                raise Exception("Error en la respuesta de la API")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al actualizar las tasas de cambio: {str(e)}\n\nPor favor, verifique su conexión a internet y la configuración de la API.")