#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Finanzas - Software de Gestión Financiera
Desarrollado con Python y PyQt5
"""

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from src.controllers.main_controller import MainController
from src.views.main_window import MainWindow
from src.models.database_manager import DatabaseManager


def main():
    # Enable High DPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # Create application
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Initialize database
    db_manager = DatabaseManager()
    db_manager.setup_database()
    
    # Create main window
    main_window = MainWindow()
    
    # Create controller
    controller = MainController(main_window, db_manager)
    
    # Show main window
    main_window.show()
    
    # Execute application
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()