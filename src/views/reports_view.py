#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QComboBox, QFrame, QDateEdit,
                             QFormLayout, QTabWidget, QMessageBox)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
import pyqtgraph as pg
import os
from datetime import datetime, timedelta

class ReportsView(QWidget):
    """Reports view showing financial reports and analytics."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.load_accounts()

    def load_accounts(self):
        """Load accounts into the account filter combo box."""
        self.account_combo.clear()
        self.account_combo.addItem("Todas las Cuentas", None)
        
        # Get accounts from database
        from src.models.database_manager import DatabaseManager
        db_manager = DatabaseManager()
        accounts = db_manager.get_accounts()
        
        for account in accounts:
            self.account_combo.addItem(account['name'], account['id'])
    
    def init_ui(self):
        """Initialize the user interface."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header section
        header_layout = QHBoxLayout()
        
        # Title
        title_label = QLabel("Informes Financieros")
        title_font = QFont("Segoe UI", 16, QFont.Bold)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        
        # Spacer
        header_layout.addStretch()
        
        # Generate report button
        self.generate_btn = QPushButton("Generar Informe")
        self.generate_btn.clicked.connect(self.generate_report)
        header_layout.addWidget(self.generate_btn)
        
        main_layout.addLayout(header_layout)
        
        # Report filters section
        filters_frame = QFrame()
        filters_frame.setObjectName("filtersFrame")
        filters_frame.setStyleSheet("""
            #filtersFrame {
                background-color: #2D2D30;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        
        filters_layout = QFormLayout(filters_frame)
        filters_layout.setContentsMargins(20, 20, 20, 20)
        filters_layout.setSpacing(15)
        
        # Report type filter
        self.report_type_combo = QComboBox()
        self.report_type_combo.addItem("Ingresos y Gastos", "income_expense")
        self.report_type_combo.addItem("Gastos por Categoría", "category")
        self.report_type_combo.addItem("Tendencias", "trend")
        self.report_type_combo.addItem("Presupuestos", "budget")
        filters_layout.addRow("Tipo de Informe:", self.report_type_combo)
        
        # Date range filter
        date_range_layout = QHBoxLayout()
        
        # Start date
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(QDate.currentDate().addMonths(-1))
        date_range_layout.addWidget(QLabel("Desde:"))
        date_range_layout.addWidget(self.start_date_edit)
        
        # End date
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDate(QDate.currentDate())
        date_range_layout.addWidget(QLabel("Hasta:"))
        date_range_layout.addWidget(self.end_date_edit)
        
        filters_layout.addRow("Período:", date_range_layout)
        
        # Account filter
        self.account_combo = QComboBox()
        self.account_combo.addItem("Todas las Cuentas", None)
        # This would be populated with actual accounts from the database
        filters_layout.addRow("Cuenta:", self.account_combo)
        
        main_layout.addWidget(filters_frame)
        
        # Reports tab widget
        self.reports_tabs = QTabWidget()
        self.reports_tabs.setTabPosition(QTabWidget.North)
        self.reports_tabs.setDocumentMode(True)
        
        # Income vs Expenses tab
        self.income_expense_tab = QWidget()
        self.reports_tabs.addTab(self.income_expense_tab, "Ingresos vs Gastos")
        
        # Categories tab
        self.categories_tab = QWidget()
        self.reports_tabs.addTab(self.categories_tab, "Categorías")
        
        # Trends tab
        self.trends_tab = QWidget()
        self.reports_tabs.addTab(self.trends_tab, "Tendencias")
        
        # Budgets tab
        self.budgets_tab = QWidget()
        self.reports_tabs.addTab(self.budgets_tab, "Presupuestos")
        
        main_layout.addWidget(self.reports_tabs)
    
    def generate_report(self, report_type=None):
        """Generate a financial report.
        
        Args:
            report_type (str, optional): Type of report to generate. Defaults to None.
        """
        if report_type is None:
            report_type = self.report_type_combo.currentData()
        else:
            # Set the combo box to the specified report type
            for i in range(self.report_type_combo.count()):
                if self.report_type_combo.itemData(i) == report_type:
                    self.report_type_combo.setCurrentIndex(i)
                    break
        
        # Get date range
        start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
        end_date = self.end_date_edit.date().toString("yyyy-MM-dd")
        
        # Get account filter
        account_id = self.account_combo.currentData()
        
        # Show appropriate tab based on report type
        if report_type == "income_expense":
            self.reports_tabs.setCurrentIndex(0)
            self.generate_income_expense_report(start_date, end_date, account_id)
        elif report_type == "category":
            self.reports_tabs.setCurrentIndex(1)
            self.generate_category_report(start_date, end_date, account_id)
        elif report_type == "trend":
            self.reports_tabs.setCurrentIndex(2)
            self.generate_trend_report(start_date, end_date, account_id)
        elif report_type == "budget":
            self.reports_tabs.setCurrentIndex(3)
            self.generate_budget_report(start_date, end_date, account_id)
    
    def generate_income_expense_report(self, start_date, end_date, account_id=None):
        """Generate income vs expenses report.
        
        Args:
            start_date (str): Start date in format 'yyyy-MM-dd'
            end_date (str): End date in format 'yyyy-MM-dd'
            account_id (int, optional): Account ID to filter by. Defaults to None.
        """
        # Clear previous content
        if self.income_expense_tab.layout():
            # Clear previous layout
            while self.income_expense_tab.layout().count():
                item = self.income_expense_tab.layout().takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
            # Remove the layout
            QWidget().setLayout(self.income_expense_tab.layout())
        
        # Create new layout
        layout = QVBoxLayout(self.income_expense_tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Add report header
        header_label = QLabel(f"Informe de Ingresos y Gastos: {start_date} a {end_date}")
        header_font = QFont("Segoe UI", 14, QFont.Bold)
        header_label.setFont(header_font)
        layout.addWidget(header_label)
        
        # Add account filter info if applicable
        if account_id:
            # Get account name from database
            from src.models.database_manager import DatabaseManager
            db_manager = DatabaseManager()
            account = db_manager.get_account(account_id)
            account_name = account['name'] if account else str(account_id)
            account_label = QLabel(f"Cuenta: {account_name}")
            account_label.setStyleSheet("color: #888;")
            layout.addWidget(account_label)
        
        # Create chart frame
        chart_frame = QFrame()
        chart_frame.setObjectName("chartFrame")
        chart_frame.setStyleSheet("""
            #chartFrame {
                background-color: #252529;
                border-radius: 8px;
                border: 1px solid #333;
            }
        """)
        chart_layout = QVBoxLayout(chart_frame)
        
        # Get real data from database
        from src.models.database_manager import DatabaseManager
        from datetime import datetime, timedelta
        import calendar
        
        db_manager = DatabaseManager()
        
        # Parse start and end dates
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
        
        # Calculate months between start and end date
        months_data = {}
        current_date = start_date_obj
        
        while current_date <= end_date_obj:
            month_name = current_date.strftime('%b')
            first_day = datetime(current_date.year, current_date.month, 1)
            last_day = datetime(current_date.year, current_date.month, 
                               calendar.monthrange(current_date.year, current_date.month)[1])
            
            # Get transactions for this month
            month_transactions = db_manager.get_transactions(
                account_id=account_id,
                start_date=first_day.strftime('%Y-%m-%d'),
                end_date=last_day.strftime('%Y-%m-%d')
            )
            
            # Calculate income and expenses
            month_income = sum(t['amount'] for t in month_transactions if t['type'] == 'income')
            month_expenses = sum(t['amount'] for t in month_transactions if t['type'] == 'expense')
            
            months_data[month_name] = {
                'income': month_income,
                'expenses': month_expenses
            }
            
            # Move to next month
            if current_date.month == 12:
                current_date = datetime(current_date.year + 1, 1, 1)
            else:
                current_date = datetime(current_date.year, current_date.month + 1, 1)
        
        # Prepare data for chart
        months = list(months_data.keys())
        income = [months_data[month]['income'] for month in months]
        expenses = [months_data[month]['expenses'] for month in months]
        
        # Create bar chart
        pg.setConfigOption('background', '#252529')
        pg.setConfigOption('foreground', '#DDDDDD')
        
        budget_widget = pg.PlotWidget()
        budget_widget.setMinimumHeight(300)
        budget_widget.setTitle("Rendimiento del Presupuesto por Categoría")
        budget_widget.showGrid(y=True, alpha=0.3)
        
        # Set up x-axis
        x_axis = budget_widget.getAxis('bottom')
        x_axis.setTicks([[(i, cat) for i, cat in enumerate(categories)]])
        
        # Create bar graph items
        bar_width = 0.35
        budget_bars = pg.BarGraphItem(x=[i-bar_width/2 for i in range(len(categories))], height=budgeted, width=bar_width, brush='#007BFF')
        actual_bars = pg.BarGraphItem(x=[i+bar_width/2 for i in range(len(categories))], height=actual, width=bar_width, brush='#FFC107')
        
        # Add items to the plot
        budget_widget.addItem(budget_bars)
        budget_widget.addItem(actual_bars)
        
        # Add legend
        legend = pg.LegendItem((100, 60), offset=(70, 20))
        legend.setParentItem(budget_widget.graphicsItem())
        legend.addItem(pg.BarGraphItem(x=[0], height=[1], width=bar_width, brush='#007BFF'), 'Presupuestado')
        legend.addItem(pg.BarGraphItem(x=[0], height=[1], width=bar_width, brush='#FFC107'), 'Real')
        
        budget_layout.addWidget(budget_widget)
        layout.addWidget(budget_frame)
        
        # Create budget summary table
        summary_frame = QFrame()
        summary_frame.setObjectName("budgetSummaryFrame")
        summary_frame.setStyleSheet("""
            #budgetSummaryFrame {
                background-color: #252529;
                border-radius: 8px;
                border: 1px solid #333;
            }
        """)
        summary_layout = QVBoxLayout(summary_frame)
        
        # Create a table for budget breakdown
        from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
        
        budget_table = QTableWidget()
        budget_table.setColumnCount(4)
        budget_table.setHorizontalHeaderLabels(["Categoría", "Presupuestado", "Real", "Diferencia"])
        budget_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        budget_table.setAlternatingRowColors(True)
        budget_table.setStyleSheet("""
            QTableWidget {
                background-color: #1E1E1E;
                border: none;
                border-radius: 6px;
                gridline-color: #333333;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #333333;
            }
            QHeaderView::section {
                background-color: #1E1E1E;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
            QTableWidget::item:selected {
                background-color: #0d47a1;
            }
        """)
        
        # Populate table with data
        budget_table.setRowCount(len(categories))
        for row, (category, budget, act) in enumerate(zip(categories, budgeted, actual)):
            # Category name
            category_item = QTableWidgetItem(category)
            budget_table.setItem(row, 0, category_item)
            
            # Budgeted amount
            budget_item = QTableWidgetItem(f"${budget:,.2f}")
            budget_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            budget_table.setItem(row, 1, budget_item)
            
            # Actual amount
            actual_item = QTableWidgetItem(f"${act:,.2f}")
            actual_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            budget_table.setItem(row, 2, actual_item)
            
            # Difference
            diff = budget - act
            diff_item = QTableWidgetItem(f"${diff:,.2f}")
            diff_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            # Color code the difference
            if diff < 0:
                diff_item.setForeground(QColor("#DC3545"))  # Red for over budget
            else:
                diff_item.setForeground(QColor("#28A745"))  # Green for under budget
                
            budget_table.setItem(row, 3, diff_item)
        
        summary_layout.addWidget(budget_table)
        layout.addWidget(summary_frame)
        
        # Add overall summary section
        overall_frame = QFrame()
        overall_frame.setObjectName("overallFrame")
        overall_frame.setStyleSheet("""
            #overallFrame {
                background-color: #252529;
                border-radius: 8px;
                border: 1px solid #333;
            }
        """)
        overall_layout = QHBoxLayout(overall_frame)
        
        # Total budgeted
        total_budget = sum(budgeted)
        budget_widget = QWidget()
        budget_layout = QVBoxLayout(budget_widget)
        budget_title = QLabel("Total Presupuestado")
        budget_title.setStyleSheet("color: #888;")
        budget_value = QLabel(f"${total_budget:,.2f}")
        budget_value.setFont(QFont("Segoe UI", 18, QFont.Bold))
        budget_value.setStyleSheet("color: #007BFF;")
        budget_layout.addWidget(budget_title)
        budget_layout.addWidget(budget_value)
        overall_layout.addWidget(budget_widget)
        
        # Total actual
        total_actual = sum(actual)
        actual_widget = QWidget()
        actual_layout = QVBoxLayout(actual_widget)
        actual_title = QLabel("Total Gastado")
        actual_title.setStyleSheet("color: #888;")
        actual_value = QLabel(f"${total_actual:,.2f}")
        actual_value.setFont(QFont("Segoe UI", 18, QFont.Bold))
        actual_value.setStyleSheet("color: #FFC107;")
        actual_layout.addWidget(actual_title)
        actual_layout.addWidget(actual_value)
        overall_layout.addWidget(actual_widget)
        
        # Total difference
        total_diff = total_budget - total_actual
        diff_widget = QWidget()
        diff_layout = QVBoxLayout(diff_widget)
        diff_title = QLabel("Diferencia Total")
        diff_title.setStyleSheet("color: #888;")
        diff_value = QLabel(f"${total_diff:,.2f}")
        diff_value.setFont(QFont("Segoe UI", 18, QFont.Bold))
        
        if total_diff < 0:
            diff_value.setStyleSheet("color: #DC3545;")  # Red for over budget
        else:
            diff_value.setStyleSheet("color: #28A745;")  # Green for under budget
            
        diff_layout.addWidget(diff_title)
        diff_layout.addWidget(diff_value)
        overall_layout.addWidget(diff_widget)
        
        layout.addWidget(overall_frame)
        
        # Set chart configuration
        pg.setConfigOption('background', '#252529')
        pg.setConfigOption('foreground', '#DDDDDD')
        
        plot_widget = pg.PlotWidget()
        plot_widget.setMinimumHeight(300)
        plot_widget.showGrid(x=True, y=True, alpha=0.3)
        
        # Set up x-axis
        x_axis = plot_widget.getAxis('bottom')
        x_axis.setTicks([[(i, month) for i, month in enumerate(months)]])
        
        # Create bar graph items
        bar_width = 0.35
        income_bars = pg.BarGraphItem(x=[i-bar_width/2 for i in range(len(months))], height=income, width=bar_width, brush='#28A745')
        expense_bars = pg.BarGraphItem(x=[i+bar_width/2 for i in range(len(months))], height=expenses, width=bar_width, brush='#DC3545')
        
        # Add items to the plot
        plot_widget.addItem(income_bars)
        plot_widget.addItem(expense_bars)
        
        # Add legend
        legend = pg.LegendItem((80, 60), offset=(70, 20))
        legend.setParentItem(plot_widget.graphicsItem())
        legend.addItem(pg.BarGraphItem(x=[0], height=[1], width=bar_width, brush='#28A745'), 'Ingresos')
        legend.addItem(pg.BarGraphItem(x=[0], height=[1], width=bar_width, brush='#DC3545'), 'Gastos')
        
        chart_layout.addWidget(plot_widget)
        layout.addWidget(chart_frame)
        
        # Add summary section
        summary_frame = QFrame()
        summary_frame.setObjectName("summaryFrame")
        summary_frame.setStyleSheet("""
            #summaryFrame {
                background-color: #252529;
                border-radius: 8px;
                border: 1px solid #333;
            }
        """)
        summary_layout = QHBoxLayout(summary_frame)
        
        # Total income
        total_income = sum(income)
        income_widget = QWidget()
        income_layout = QVBoxLayout(income_widget)
        income_title = QLabel("Total de Ingresos")
        income_title.setStyleSheet("color: #888;")
        income_value = QLabel(f"${total_income:,.2f}")
        income_value.setFont(QFont("Segoe UI", 18, QFont.Bold))
        income_value.setStyleSheet("color: #28A745;")
        income_layout.addWidget(income_title)
        income_layout.addWidget(income_value)
        summary_layout.addWidget(income_widget)
        
        # Total expenses
        total_expenses = sum(expenses)
        expenses_widget = QWidget()
        expenses_layout = QVBoxLayout(expenses_widget)
        expenses_title = QLabel("Total de Gastos")
        expenses_title.setStyleSheet("color: #888;")
        expenses_value = QLabel(f"${total_expenses:,.2f}")
        expenses_value.setFont(QFont("Segoe UI", 18, QFont.Bold))
        expenses_value.setStyleSheet("color: #DC3545;")
        expenses_layout.addWidget(expenses_title)
        expenses_layout.addWidget(expenses_value)
        summary_layout.addWidget(expenses_widget)
        
        # Net income
        net_income = total_income - total_expenses
        net_widget = QWidget()
        net_layout = QVBoxLayout(net_widget)
        net_title = QLabel("Ingreso Neto")
        net_title.setStyleSheet("color: #888;")
        net_value = QLabel(f"${net_income:,.2f}")
        net_value.setFont(QFont("Segoe UI", 18, QFont.Bold))
        net_value.setStyleSheet("color: #007BFF;")
        net_layout.addWidget(net_title)
        net_layout.addWidget(net_value)
        summary_layout.addWidget(net_widget)
        
        layout.addWidget(summary_frame)
    
    def generate_category_report(self, start_date, end_date, account_id=None):
        """Generate expenses by category report.
        
        Args:
            start_date (str): Start date in format 'yyyy-MM-dd'
            end_date (str): End date in format 'yyyy-MM-dd'
            account_id (int, optional): Account ID to filter by. Defaults to None.
        """
        # Clear previous content
        if self.categories_tab.layout():
            # Clear previous layout
            while self.categories_tab.layout().count():
                item = self.categories_tab.layout().takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
            # Remove the layout
            QWidget().setLayout(self.categories_tab.layout())
        
        # Create new layout
        layout = QVBoxLayout(self.categories_tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Add report header
        header_label = QLabel(f"Informe de Gastos por Categoría: {start_date} a {end_date}")
        header_font = QFont("Segoe UI", 14, QFont.Bold)
        header_label.setFont(header_font)
        layout.addWidget(header_label)
        
        # Add account filter info if applicable
        if account_id:
            account_label = QLabel(f"Cuenta: {account_id}")
            account_label.setStyleSheet("color: #888;")
            layout.addWidget(account_label)
        
        # Create charts layout
        charts_layout = QHBoxLayout()
        
        # Create pie chart frame
        pie_frame = QFrame()
        pie_frame.setObjectName("pieFrame")
        pie_frame.setStyleSheet("""
            #pieFrame {
                background-color: #252529;
                border-radius: 8px;
                border: 1px solid #333;
            }
        """)
        pie_layout = QVBoxLayout(pie_frame)
        
        # Sample data - in a real app, this would come from the database
        categories = ['Alimentación', 'Vivienda', 'Transporte', 'Entretenimiento', 'Servicios', 'Otros']
        values = [650, 800, 250, 180, 220, 80]
        colors = ['#FF5733', '#33FF57', '#33A8FF', '#A833FF', '#FF33A8', '#FFFF33']
        
        # Create pie chart
        pg.setConfigOption('background', '#252529')
        pg.setConfigOption('foreground', '#DDDDDD')
        
        pie_widget = pg.PlotWidget()
        pie_widget.setMinimumHeight(300)
        pie_widget.setTitle("Distribución de Gastos por Categoría")
        
        # Create a custom view box that will contain our pie chart
        view_box = pg.ViewBox()
        pie_widget.setCentralItem(view_box)
        
        # Create a custom pie chart item
        from src.views.dashboard_view import PieChartItem
        pie = PieChartItem(values, colors, categories)
        view_box.addItem(pie)
        
        pie_layout.addWidget(pie_widget)
        charts_layout.addWidget(pie_frame, 1)
        
        # Create bar chart frame
        bar_frame = QFrame()
        bar_frame.setObjectName("barFrame")
        bar_frame.setStyleSheet("""
            #barFrame {
                background-color: #252529;
                border-radius: 8px;
                border: 1px solid #333;
            }
        """)
        bar_layout = QVBoxLayout(bar_frame)
        
        # Create bar chart
        bar_widget = pg.PlotWidget()
        bar_widget.setMinimumHeight(300)
        bar_widget.setTitle("Gastos por Categoría")
        bar_widget.showGrid(y=True, alpha=0.3)
        
        # Set up x-axis
        x_axis = bar_widget.getAxis('bottom')
        x_axis.setTicks([[(i, cat) for i, cat in enumerate(categories)]])
        
        # Create bar graph item
        bars = pg.BarGraphItem(x=range(len(categories)), height=values, width=0.6, brush='#33A8FF')
        bar_widget.addItem(bars)
        
        bar_layout.addWidget(bar_widget)
        charts_layout.addWidget(bar_frame, 1)
        
        layout.addLayout(charts_layout)
        
        # Add summary section
        summary_frame = QFrame()
        summary_frame.setObjectName("categorySummaryFrame")
        summary_frame.setStyleSheet("""
            #categorySummaryFrame {
                background-color: #252529;
                border-radius: 8px;
                border: 1px solid #333;
            }
        """)
        summary_layout = QVBoxLayout(summary_frame)
        
        # Create a table for category breakdown
        from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
        
        category_table = QTableWidget()
        category_table.setColumnCount(3)
        category_table.setHorizontalHeaderLabels(["Categoría", "Monto", "Porcentaje"])
        category_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        category_table.setAlternatingRowColors(True)
        category_table.setStyleSheet("""
            QTableWidget {
                background-color: #1E1E1E;
                border: none;
                border-radius: 6px;
                gridline-color: #333333;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #333333;
            }
            QHeaderView::section {
                background-color: #1E1E1E;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
            QTableWidget::item:selected {
                background-color: #0d47a1;
            }
        """)
        
        # Calculate total
        total = sum(values)
        
        # Populate table with data
        category_table.setRowCount(len(categories))
        for row, (category, value, color) in enumerate(zip(categories, values, colors)):
            # Category name
            category_item = QTableWidgetItem(category)
            category_table.setItem(row, 0, category_item)
            
            # Amount
            amount_item = QTableWidgetItem(f"${value:,.2f}")
            amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            category_table.setItem(row, 1, amount_item)
            
            # Percentage
            percentage = (value / total) * 100 if total > 0 else 0
            percentage_item = QTableWidgetItem(f"{percentage:.1f}%")
            percentage_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            category_table.setItem(row, 2, percentage_item)
        
        summary_layout.addWidget(category_table)
        layout.addWidget(summary_frame)
    
    def generate_trend_report(self, start_date, end_date, account_id=None):
        """Generate financial trends report.
        
        Args:
            start_date (str): Start date in format 'yyyy-MM-dd'
            end_date (str): End date in format 'yyyy-MM-dd'
            account_id (int, optional): Account ID to filter by. Defaults to None.
        """
        # Clear previous content
        if self.trends_tab.layout():
            # Clear previous layout
            while self.trends_tab.layout().count():
                item = self.trends_tab.layout().takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
            # Remove the layout
            QWidget().setLayout(self.trends_tab.layout())
        
        # Create new layout
        layout = QVBoxLayout(self.trends_tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Add report header
        header_label = QLabel(f"Informe de Tendencias Financieras: {start_date} a {end_date}")
        header_font = QFont("Segoe UI", 14, QFont.Bold)
        header_label.setFont(header_font)
        layout.addWidget(header_label)
        
        # Add account filter info if applicable
        if account_id:
            account_label = QLabel(f"Cuenta: {account_id}")
            account_label.setStyleSheet("color: #888;")
            layout.addWidget(account_label)
        
        # Create line chart frame for net worth trend
        net_worth_frame = QFrame()
        net_worth_frame.setObjectName("netWorthFrame")
        net_worth_frame.setStyleSheet("""
            #netWorthFrame {
                background-color: #252529;
                border-radius: 8px;
                border: 1px solid #333;
            }
        """)
        net_worth_layout = QVBoxLayout(net_worth_frame)
        
        # Sample data - in a real app, this would come from the database
        months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
        net_worth = [8500, 8800, 9200, 9500, 9800, 10200, 10500, 10800, 11200, 11500, 11800, 12000]
        
        # Create line chart
        pg.setConfigOption('background', '#252529')
        pg.setConfigOption('foreground', '#DDDDDD')
        
        net_worth_widget = pg.PlotWidget()
        net_worth_widget.setMinimumHeight(250)
        net_worth_widget.setTitle("Tendencia de Patrimonio Neto")
        net_worth_widget.showGrid(x=True, y=True, alpha=0.3)
        
        # Set up x-axis
        x_axis = net_worth_widget.getAxis('bottom')
        x_axis.setTicks([[(i, month) for i, month in enumerate(months)]])
        
        # Create line plot
        pen = pg.mkPen(color='#1565c0', width=3)
        line = net_worth_widget.plot(range(len(months)), net_worth, pen=pen, symbol='o', symbolSize=8, symbolBrush='#1565c0')
        
        net_worth_layout.addWidget(net_worth_widget)
        layout.addWidget(net_worth_frame)
        
        # Create income/expense trend frame
        income_expense_frame = QFrame()
        income_expense_frame.setObjectName("incomeExpenseFrame")
        income_expense_frame.setStyleSheet("""
            #incomeExpenseFrame {
                background-color: #252529;
                border-radius: 8px;
                border: 1px solid #333;
            }
        """)
        income_expense_layout = QVBoxLayout(income_expense_frame)
        
        # Sample data - in a real app, this would come from the database
        income_trend = [3000, 3100, 3200, 3150, 3250, 3300, 3350, 3400, 3450, 3500, 3550, 3600]
        expense_trend = [2200, 2300, 2100, 2000, 2200, 2300, 2250, 2300, 2350, 2400, 2450, 2500]
        
        # Create line chart
        trend_widget = pg.PlotWidget()
        trend_widget.setMinimumHeight(250)
        trend_widget.setTitle("Tendencia de Ingresos y Gastos")
        trend_widget.showGrid(x=True, y=True, alpha=0.3)
        
        # Set up x-axis
        x_axis = trend_widget.getAxis('bottom')
        x_axis.setTicks([[(i, month) for i, month in enumerate(months)]])
        
        # Create line plots
        income_pen = pg.mkPen(color='#28A745', width=3)
        expense_pen = pg.mkPen(color='#DC3545', width=3)
        
        income_line = trend_widget.plot(range(len(months)), income_trend, pen=income_pen, symbol='o', symbolSize=6, symbolBrush='#28A745', name='Ingresos')
        expense_line = trend_widget.plot(range(len(months)), expense_trend, pen=expense_pen, symbol='o', symbolSize=6, symbolBrush='#DC3545', name='Gastos')
        
        # Add legend
        legend = pg.LegendItem((100, 60), offset=(70, 20))
        legend.setParentItem(trend_widget.graphicsItem())
        legend.addItem(income_line, 'Ingresos')
        legend.addItem(expense_line, 'Gastos')
        
        income_expense_layout.addWidget(trend_widget)
        layout.addWidget(income_expense_frame)
        
        # Add summary section
        summary_frame = QFrame()
        summary_frame.setObjectName("trendSummaryFrame")
        summary_frame.setStyleSheet("""
            #trendSummaryFrame {
                background-color: #252529;
                border-radius: 8px;
                border: 1px solid #333;
            }
        """)
        summary_layout = QHBoxLayout(summary_frame)
        
        # Average monthly income
        avg_income = sum(income_trend) / len(income_trend)
        income_widget = QWidget()
        income_layout = QVBoxLayout(income_widget)
        income_title = QLabel("Ingreso Mensual Promedio")
        income_title.setStyleSheet("color: #888;")
        income_value = QLabel(f"${avg_income:,.2f}")
        income_value.setFont(QFont("Segoe UI", 18, QFont.Bold))
        income_value.setStyleSheet("color: #28A745;")
        income_layout.addWidget(income_title)
        income_layout.addWidget(income_value)
        summary_layout.addWidget(income_widget)
        
        # Average monthly expenses
        avg_expense = sum(expense_trend) / len(expense_trend)
        expense_widget = QWidget()
        expense_layout = QVBoxLayout(expense_widget)
        expense_title = QLabel("Gasto Mensual Promedio")
        expense_title.setStyleSheet("color: #888;")
        expense_value = QLabel(f"${avg_expense:,.2f}")
        expense_value.setFont(QFont("Segoe UI", 18, QFont.Bold))
        expense_value.setStyleSheet("color: #DC3545;")
        expense_layout.addWidget(expense_title)
        expense_layout.addWidget(expense_value)
        summary_layout.addWidget(expense_widget)
        
        # Net worth growth
        growth = ((net_worth[-1] - net_worth[0]) / net_worth[0]) * 100 if net_worth[0] > 0 else 0
        growth_widget = QWidget()
        growth_layout = QVBoxLayout(growth_widget)
        growth_title = QLabel("Crecimiento Patrimonial")
        growth_title.setStyleSheet("color: #888;")
        growth_value = QLabel(f"{growth:.1f}%")
        growth_value.setFont(QFont("Segoe UI", 18, QFont.Bold))
        growth_value.setStyleSheet("color: #007BFF;")
        growth_layout.addWidget(growth_title)
        growth_layout.addWidget(growth_value)
        summary_layout.addWidget(growth_widget)
        
        layout.addWidget(summary_frame)
    
    def generate_budget_report(self, start_date, end_date, account_id=None):
        """Generate budget performance report.
        
        Args:
            start_date (str): Start date in format 'yyyy-MM-dd'
            end_date (str): End date in format 'yyyy-MM-dd'
            account_id (int, optional): Account ID to filter by. Defaults to None.
        """
        # Clear previous content
        if self.budgets_tab.layout():
            # Clear previous layout
            while self.budgets_tab.layout().count():
                item = self.budgets_tab.layout().takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
            # Remove the layout
            QWidget().setLayout(self.budgets_tab.layout())
        
        # Create new layout
        layout = QVBoxLayout(self.budgets_tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Add report header
        header_label = QLabel(f"Informe de Presupuestos: {start_date} a {end_date}")
        header_font = QFont("Segoe UI", 14, QFont.Bold)
        header_label.setFont(header_font)
        layout.addWidget(header_label)
        
        # Add account filter info if applicable
        if account_id:
            account_label = QLabel(f"Cuenta: {account_id}")
            account_label.setStyleSheet("color: #888;")
            layout.addWidget(account_label)
        
        # Create budget performance frame
        budget_frame = QFrame()
        budget_frame.setObjectName("budgetFrame")
        budget_frame.setStyleSheet("""
            #budgetFrame {
                background-color: #252529;
                border-radius: 8px;
                border: 1px solid #333;
            }
        """)
        budget_layout = QVBoxLayout(budget_frame)
        
        # Sample data - in a real app, this would come from the database
        categories = ['Alimentación', 'Vivienda', 'Transporte', 'Entretenimiento', 'Servicios', 'Otros']
        budgeted = [800, 1000, 300, 200, 250, 100]
        actual = [650, 800, 250, 180, 220, 80]
        
        # Create bar chart
        pg.setConfigOption('background', '#252529')
        pg.setConfigOption('foreground', '#DDDDDD')
        
        budget_widget = pg.PlotWidget()
        budget_widget.setMinimumHeight(300)
        budget_widget.setTitle("Rendimiento del Presupuesto por Categoría")
        budget_widget.showGrid(y=True, alpha=0.3)
        
        # Set up x-axis
        x_axis = budget_widget.getAxis('bottom')
        x_axis.setTicks([[(i, cat) for i, cat in enumerate(categories)]])
        
        # Create bar graph items
        bar_width = 0.35
        budget_bars = pg.BarGraphItem(x=[i-bar_width/2 for i in range(len(categories))], height=budgeted, width=bar_width, brush='#007BFF')
        actual_bars = pg.BarGraphItem(x=[i+bar_width/2 for i in range(len(categories))], height=actual, width=bar_width, brush='#FFC107')
        
        # Add items to the plot
        budget_widget.addItem(budget_bars)
        budget_widget.addItem(actual_bars)
        
        # Add legend
        legend = pg.LegendItem((100, 60), offset=(70, 20))
        legend.setParentItem(budget_widget.graphicsItem())
        legend.addItem(pg.BarGraphItem(x=[0], height=[1], width=bar_width, brush='#007BFF'), 'Presupuestado')
        legend.addItem(pg.BarGraphItem(x=[0], height=[1], width=bar_width, brush='#FFC107'), 'Real')
        
        budget_layout.addWidget(budget_widget)
        layout.addWidget(budget_frame)
        
        # Create budget summary table
        summary_frame = QFrame()
        summary_frame.setObjectName("budgetSummaryFrame")
        summary_frame.setStyleSheet("""
            #budgetSummaryFrame {
                background-color: #252529;
                border-radius: 8px;
                border: 1px solid #333;
            }
        """)
        summary_layout = QVBoxLayout(summary_frame)
        
        # Create a table for budget breakdown
        from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
        
        budget_table = QTableWidget()
        budget_table.setColumnCount(4)
        budget_table.setHorizontalHeaderLabels(["Categoría", "Presupuestado", "Real", "Diferencia"])
        budget_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        budget_table.setAlternatingRowColors(True)
        budget_table.setStyleSheet("""
            QTableWidget {
                background-color: #1E1E1E;
                border: none;
                border-radius: 6px;
                gridline-color: #333333;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #333333;
            }
            QHeaderView::section {
                background-color: #1E1E1E;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
            QTableWidget::item:selected {
                background-color: #0d47a1;
            }
        """)
        
        # Populate table with data
        budget_table.setRowCount(len(categories))
        for row, (category, budget, act) in enumerate(zip(categories, budgeted, actual)):
            # Category name
            category_item = QTableWidgetItem(category)
            budget_table.setItem(row, 0, category_item)
            
            # Budgeted amount
            budget_item = QTableWidgetItem(f"${budget:,.2f}")
            budget_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            budget_table.setItem(row, 1, budget_item)
            
            # Actual amount
            actual_item = QTableWidgetItem(f"${act:,.2f}")
            actual_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            budget_table.setItem(row, 2, actual_item)
            
            # Difference
            diff = budget - act
            diff_item = QTableWidgetItem(f"${diff:,.2f}")
            diff_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            # Color code the difference
            if diff < 0:
                diff_item.setForeground(QColor("#DC3545"))  # Red for over budget
            else:
                diff_item.setForeground(QColor("#28A745"))  # Green for under budget
                
            budget_table.setItem(row, 3, diff_item)
        
        summary_layout.addWidget(budget_table)
        layout.addWidget(summary_frame)
        
        # Add overall summary section
        overall_frame = QFrame()
        overall_frame.setObjectName("overallFrame")
        overall_frame.setStyleSheet("""
            #overallFrame {
                background-color: #252529;
                border-radius: 8px;
                border: 1px solid #333;
            }
        """)
        overall_layout = QHBoxLayout(overall_frame)
        
        # Total budgeted
        total_budget = sum(budgeted)
        budget_widget = QWidget()
        budget_layout = QVBoxLayout(budget_widget)
        budget_title = QLabel("Total Presupuestado")
        budget_title.setStyleSheet("color: #888;")
        budget_value = QLabel(f"${total_budget:,.2f}")
        budget_value.setFont(QFont("Segoe UI", 18, QFont.Bold))
        budget_value.setStyleSheet("color: #007BFF;")
        budget_layout.addWidget(budget_title)
        budget_layout.addWidget(budget_value)
        overall_layout.addWidget(budget_widget)
        
        # Total actual
        total_actual = sum(actual)
        actual_widget = QWidget()
        actual_layout = QVBoxLayout(actual_widget)
        actual_title = QLabel("Total Gastado")
        actual_title.setStyleSheet("color: #888;")
        actual_value = QLabel(f"${total_actual:,.2f}")
        actual_value.setFont(QFont("Segoe UI", 18, QFont.Bold))
        actual_value.setStyleSheet("color: #FFC107;")
        actual_layout.addWidget(actual_title)
        actual_layout.addWidget(actual_value)
        overall_layout.addWidget(actual_widget)
        
        # Total difference
        total_diff = total_budget - total_actual
        diff_widget = QWidget()
        diff_layout = QVBoxLayout(diff_widget)
        diff_title = QLabel("Diferencia Total")
        diff_title.setStyleSheet("color: #888;")
        diff_value = QLabel(f"${total_diff:,.2f}")
        diff_value.setFont(QFont("Segoe UI", 18, QFont.Bold))
        
        if total_diff < 0:
            diff_value.setStyleSheet("color: #DC3545;")  # Red for over budget
        else:
            diff_value.setStyleSheet("color: #28A745;")  # Green for under budget
            
        diff_layout.addWidget(diff_title)
        diff_layout.addWidget(diff_value)
        overall_layout.addWidget(diff_widget)
        
        layout.addWidget(overall_frame)
    
    def load_accounts(self):
        """Load accounts into the account filter combo box."""
        self.account_combo.clear()
        self.account_combo.addItem("Todas las Cuentas", None)
        
        # Get accounts from database
        from src.models.database_manager import DatabaseManager
        db_manager = DatabaseManager()
        accounts = db_manager.get_accounts()
        
        for account in accounts:
            self.account_combo.addItem(account['name'], account['id'])
    
    def generate_category_report(self, start_date, end_date, account_id=None):
        """Generate expenses by category report.
        
        Args:
            start_date (str): Start date in format 'yyyy-MM-dd'
            end_date (str): End date in format 'yyyy-MM-dd'
            account_id (int, optional): Account ID to filter by. Defaults to None.
        """
        # Clear previous content
        if self.categories_tab.layout():
            # Clear previous layout
            while self.categories_tab.layout().count():
                item = self.categories_tab.layout().takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
            # Remove the layout
            QWidget().setLayout(self.categories_tab.layout())
        
        # Create new layout
        layout = QVBoxLayout(self.categories_tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Add report header
        header_label = QLabel(f"Informe de Gastos por Categoría: {start_date} a {end_date}")
        header_font = QFont("Segoe UI", 14, QFont.Bold)
        header_label.setFont(header_font)
        layout.addWidget(header_label)
        
        # Add account filter info if applicable
        if account_id:
            account_label = QLabel(f"Cuenta: {account_id}")
            account_label.setStyleSheet("color: #888;")
            layout.addWidget(account_label)
        
        # Create charts layout
        charts_layout = QHBoxLayout()
        
        # Create pie chart frame
        pie_frame = QFrame()
        pie_frame.setObjectName("pieFrame")
        pie_frame.setStyleSheet("""
            #pieFrame {
                background-color: #252529;
                border-radius: 8px;
                border: 1px solid #333;
            }
        """)
        pie_layout = QVBoxLayout(pie_frame)
        
        # Sample data - in a real app, this would come from the database
        categories = ['Alimentación', 'Vivienda', 'Transporte', 'Entretenimiento', 'Servicios', 'Otros']
        values = [650, 800, 250, 180, 220, 80]
        colors = ['#FF5733', '#33FF57', '#33A8FF', '#A833FF', '#FF33A8', '#FFFF33']
        
        # Create pie chart
        pg.setConfigOption('background', '#252529')
        pg.setConfigOption('foreground', '#DDDDDD')
        
        pie_widget = pg.PlotWidget()
        pie_widget.setMinimumHeight(300)
        pie_widget.setTitle("Distribución de Gastos por Categoría")
        
        # Create a custom view box that will contain our pie chart
        view_box = pg.ViewBox()
        pie_widget.setCentralItem(view_box)
        
        # Create a custom pie chart item
        from src.views.dashboard_view import PieChartItem
        pie = PieChartItem(values, colors, categories)
        view_box.addItem(pie)
        
        pie_layout.addWidget(pie_widget)
        charts_layout.addWidget(pie_frame, 1)
        
        # Create bar chart frame
        bar_frame = QFrame()
        bar_frame.setObjectName("barFrame")
        bar_frame.setStyleSheet("""
            #barFrame {
                background-color: #252529;
                border-radius: 8px;
                border: 1px solid #333;
            }
        """)
        bar_layout = QVBoxLayout(bar_frame)
        
        # Create bar chart
        bar_widget = pg.PlotWidget()
        bar_widget.setMinimumHeight(300)
        bar_widget.setTitle("Gastos por Categoría")
        bar_widget.showGrid(y=True, alpha=0.3)
        
        # Set up x-axis
        x_axis = bar_widget.getAxis('bottom')
        x_axis.setTicks([[(i, cat) for i, cat in enumerate(categories)]])
        
        # Create bar graph item
        bars = pg.BarGraphItem(x=range(len(categories)), height=values, width=0.6, brush='#33A8FF')
        bar_widget.addItem(bars)
        
        bar_layout.addWidget(bar_widget)
        charts_layout.addWidget(bar_frame, 1)
        
        layout.addLayout(charts_layout)
        
        # Add summary section
        summary_frame = QFrame()
        summary_frame.setObjectName("categorySummaryFrame")
        summary_frame.setStyleSheet("""
            #categorySummaryFrame {
                background-color: #252529;
                border-radius: 8px;
                border: 1px solid #333;
            }
        """)
        summary_layout = QVBoxLayout(summary_frame)
        
        # Create a table for category breakdown
        from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
        
        category_table = QTableWidget()
        category_table.setColumnCount(3)
        category_table.setHorizontalHeaderLabels(["Categoría", "Monto", "Porcentaje"])
        category_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        category_table.setAlternatingRowColors(True)
        category_table.setStyleSheet("""
            QTableWidget {
                background-color: #1E1E1E;
                border: none;
                border-radius: 6px;
                gridline-color: #333333;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #333333;
            }
            QHeaderView::section {
                background-color: #1E1E1E;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
            QTableWidget::item:selected {
                background-color: #0d47a1;
            }
        """)
        
        # Calculate total
        total = sum(values)
        
        # Populate table with data
        category_table.setRowCount(len(categories))
        for row, (category, value, color) in enumerate(zip(categories, values, colors)):
            # Category name
            category_item = QTableWidgetItem(category)
            category_table.setItem(row, 0, category_item)
            
            # Amount
            amount_item = QTableWidgetItem(f"${value:,.2f}")
            amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            category_table.setItem(row, 1, amount_item)
            
            # Percentage
            percentage = (value / total) * 100 if total > 0 else 0
            percentage_item = QTableWidgetItem(f"{percentage:.1f}%")
            percentage_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            category_table.setItem(row, 2, percentage_item)
        
        summary_layout.addWidget(category_table)
        layout.addWidget(summary_frame)
    
    def generate_trend_report(self, start_date, end_date, account_id=None):
        """Generate financial trends report.
        
        Args:
            start_date (str): Start date in format 'yyyy-MM-dd'
            end_date (str): End date in format 'yyyy-MM-dd'
            account_id (int, optional): Account ID to filter by. Defaults to None.
        """
        # Clear previous content
        if self.trends_tab.layout():
            # Clear previous layout
            while self.trends_tab.layout().count():
                item = self.trends_tab.layout().takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
            # Remove the layout
            QWidget().setLayout(self.trends_tab.layout())
        
        # Create new layout
        layout = QVBoxLayout(self.trends_tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Add report header
        header_label = QLabel(f"Informe de Tendencias Financieras: {start_date} a {end_date}")
        header_font = QFont("Segoe UI", 14, QFont.Bold)
        header_label.setFont(header_font)
        layout.addWidget(header_label)
        
        # Add account filter info if applicable
        if account_id:
            account_label = QLabel(f"Cuenta: {account_id}")
            account_label.setStyleSheet("color: #888;")
            layout.addWidget(account_label)
        
        # Create line chart frame for net worth trend
        net_worth_frame = QFrame()
        net_worth_frame.setObjectName("netWorthFrame")
        net_worth_frame.setStyleSheet("""
            #netWorthFrame {
                background-color: #252529;
                border-radius: 8px;
                border: 1px solid #333;
            }
        """)
        net_worth_layout = QVBoxLayout(net_worth_frame)
        
        # Sample data - in a real app, this would come from the database
        months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
        net_worth = [8500, 8800, 9200, 9500, 9800, 10200, 10500, 10800, 11200, 11500, 11800, 12000]
        
        # Create line chart
        pg.setConfigOption('background', '#252529')
        pg.setConfigOption('foreground', '#DDDDDD')
        
        net_worth_widget = pg.PlotWidget()
        net_worth_widget.setMinimumHeight(250)
        net_worth_widget.setTitle("Tendencia de Patrimonio Neto")
        net_worth_widget.showGrid(x=True, y=True, alpha=0.3)
        
        # Set up x-axis
        x_axis = net_worth_widget.getAxis('bottom')
        x_axis.setTicks([[(i, month) for i, month in enumerate(months)]])
        
        # Create line plot
        pen = pg.mkPen(color='#1565c0', width=3)
        line = net_worth_widget.plot(range(len(months)), net_worth, pen=pen, symbol='o', symbolSize=8, symbolBrush='#1565c0')
        
        net_worth_layout.addWidget(net_worth_widget)
        layout.addWidget(net_worth_frame)
        
        # Create income/expense trend frame
        income_expense_frame = QFrame()
        income_expense_frame.setObjectName("incomeExpenseFrame")
        income_expense_frame.setStyleSheet("""
            #incomeExpenseFrame {
                background-color: #252529;
                border-radius: 8px;
                border: 1px solid #333;
            }
        """)
        income_expense_layout = QVBoxLayout(income_expense_frame)
        
        # Sample data - in a real app, this would come from the database
        income_trend = [3000, 3100, 3200, 3150, 3250, 3300, 3350, 3400, 3450, 3500, 3550, 3600]
        expense_trend = [2200, 2300, 2100, 2000, 2200, 2300, 2250, 2300, 2350, 2400, 2450, 2500]
        
        # Create line chart
        trend_widget = pg.PlotWidget()
        trend_widget.setMinimumHeight(250)
        trend_widget.setTitle("Tendencia de Ingresos y Gastos")
        trend_widget.showGrid(x=True, y=True, alpha=0.3)
        
        # Set up x-axis
        x_axis = trend_widget.getAxis('bottom')
        x_axis.setTicks([[(i, month) for i, month in enumerate(months)]])
        
        # Create line plots
        income_pen = pg.mkPen(color='#28A745', width=3)
        expense_pen = pg.mkPen(color='#DC3545', width=3)
        
        income_line = trend_widget.plot(range(len(months)), income_trend, pen=income_pen, symbol='o', symbolSize=6, symbolBrush='#28A745', name='Ingresos')
        expense_line = trend_widget.plot(range(len(months)), expense_trend, pen=expense_pen, symbol='o', symbolSize=6, symbolBrush='#DC3545', name='Gastos')
        
        # Add legend
        legend = pg.LegendItem((100, 60), offset=(70, 20))
        legend.setParentItem(trend_widget.graphicsItem())
        legend.addItem(income_line, 'Ingresos')
        legend.addItem(expense_line, 'Gastos')
        
        income_expense_layout.addWidget(trend_widget)
        layout.addWidget(income_expense_frame)
        
        # Add summary section
        summary_frame = QFrame()
        summary_frame.setObjectName("trendSummaryFrame")
        summary_frame.setStyleSheet("""
            #trendSummaryFrame {
                background-color: #252529;
                border-radius: 8px;
                border: 1px solid #333;
            }
        """)
        summary_layout = QHBoxLayout(summary_frame)
        
        # Average monthly income
        avg_income = sum(income_trend) / len(income_trend)
        income_widget = QWidget()
        income_layout = QVBoxLayout(income_widget)
        income_title = QLabel("Ingreso Mensual Promedio")
        income_title.setStyleSheet("color: #888;")
        income_value = QLabel(f"${avg_income:,.2f}")
        income_value.setFont(QFont("Segoe UI", 18, QFont.Bold))
        income_value.setStyleSheet("color: #28A745;")
        income_layout.addWidget(income_title)
        income_layout.addWidget(income_value)
        summary_layout.addWidget(income_widget)
        
        # Average monthly expenses
        avg_expense = sum(expense_trend) / len(expense_trend)
        expense_widget = QWidget()
        expense_layout = QVBoxLayout(expense_widget)
        expense_title = QLabel("Gasto Mensual Promedio")
        expense_title.setStyleSheet("color: #888;")
        expense_value = QLabel(f"${avg_expense:,.2f}")
        expense_value.setFont(QFont("Segoe UI", 18, QFont.Bold))
        expense_value.setStyleSheet("color: #DC3545;")
        expense_layout.addWidget(expense_title)
        expense_layout.addWidget(expense_value)
        summary_layout.addWidget(expense_widget)
        
        # Net worth growth
        growth = ((net_worth[-1] - net_worth[0]) / net_worth[0]) * 100 if net_worth[0] > 0 else 0
        growth_widget = QWidget()
        growth_layout = QVBoxLayout(growth_widget)
        growth_title = QLabel("Crecimiento Patrimonial")
        growth_title.setStyleSheet("color: #888;")
        growth_value = QLabel(f"{growth:.1f}%")
        growth_value.setFont(QFont("Segoe UI", 18, QFont.Bold))
        growth_value.setStyleSheet("color: #007BFF;")
        growth_layout.addWidget(growth_title)
        growth_layout.addWidget(growth_value)
        summary_layout.addWidget(growth_widget)
        
        layout.addWidget(summary_frame)
    
    def generate_budget_report(self, start_date, end_date, account_id=None):
        """Generate budget performance report.
        
        Args:
            start_date (str): Start date in format 'yyyy-MM-dd'
            end_date (str): End date in format 'yyyy-MM-dd'
            account_id (int, optional): Account ID to filter by. Defaults to None.
        """
        # Clear previous content
        if self.budgets_tab.layout():
            # Clear previous layout
            while self.budgets_tab.layout().count():
                item = self.budgets_tab.layout().takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
            # Remove the layout
            QWidget().setLayout(self.budgets_tab.layout())
        
        # Create new layout
        layout = QVBoxLayout(self.budgets_tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Add report header
        header_label = QLabel(f"Informe de Presupuestos: {start_date} a {end_date}")
        header_font = QFont("Segoe UI", 14, QFont.Bold)
        header_label.setFont(header_font)
        layout.addWidget(header_label)
        
        # Add account filter info if applicable
        if account_id:
            account_label = QLabel(f"Cuenta: {account_id}")
            account_label.setStyleSheet("color: #888;")
            layout.addWidget(account_label)
        
        # Create budget performance frame
        budget_frame = QFrame()
        budget_frame.setObjectName("budgetFrame")
        budget_frame.setStyleSheet("""
            #budgetFrame {
                background-color: #252529;
                border-radius: 8px;
                border: 1px solid #333;
            }
        """)
        budget_layout = QVBoxLayout(budget_frame)
        
        # Sample data - in a real app, this would come from the database
        categories = ['Alimentación', 'Vivienda', 'Transporte', 'Entretenimiento', 'Servicios', 'Otros']
        budgeted = [800, 1000, 300, 200, 250, 100]
        actual = [650, 800, 250, 180, 220, 80]
        
        # Create bar chart
        pg.setConfigOption('background', '#252529')
        pg.setConfigOption('foreground', '#DDDDDD')
        
        budget_widget = pg.PlotWidget()
        budget_widget.setMinimumHeight(300)
        budget_widget.setTitle("Rendimiento del Presupuesto por Categoría")
        budget_widget.showGrid(y=True, alpha=0.3)
        
        # Set up x-axis
        x_axis = budget_widget.getAxis('bottom')
        x_axis.setTicks([[(i, cat) for i, cat in enumerate(categories)]])
        
        # Create bar graph items
        bar_width = 0.35
        budget_bars = pg.BarGraphItem(x=[i-bar_width/2 for i in range(len(categories))], height=budgeted, width=bar_width, brush='#007BFF')
        actual_bars = pg.BarGraphItem(x=[i+bar_width/2 for i in range(len(categories))], height=actual, width=bar_width, brush='#FFC107')
        
        # Add items to the plot
        budget_widget.addItem(budget_bars)
        budget_widget.addItem(actual_bars)
        
        # Add legend
        legend = pg.LegendItem((100, 60), offset=(70, 20))
        legend.setParentItem(budget_widget.graphicsItem())
        legend.addItem(pg.BarGraphItem(x=[0], height=[1], width=bar_width, brush='#007BFF'), 'Presupuestado')
        legend.addItem(pg.BarGraphItem(x=[0], height=[1], width=bar_width, brush='#FFC107'), 'Real')
        
        budget_layout.addWidget(budget_widget)
        layout.addWidget(budget_frame)
        
        # Create budget summary table
        summary_frame = QFrame()
        summary_frame.setObjectName("budgetSummaryFrame")
        summary_frame.setStyleSheet("""
            #budgetSummaryFrame {
                background-color: #252529;
                border-radius: 8px;
                border: 1px solid #333;
            }
        """)
        summary_layout = QVBoxLayout(summary_frame)
        
        # Create a table for budget breakdown
        from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
        
        budget_table = QTableWidget()
        budget_table.setColumnCount(4)
        budget_table.setHorizontalHeaderLabels(["Categoría", "Presupuestado", "Real", "Diferencia"])
        budget_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        budget_table.setAlternatingRowColors(True)
        budget_table.setStyleSheet("""
            QTableWidget {
                background-color: #1E1E1E;
                border: none;
                border-radius: 6px;
                gridline-color: #333333;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #333333;
            }
            QHeaderView::section {
                background-color: #1E1E1E;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
            QTableWidget::item:selected {
                background-color: #0d47a1;
            }
        """)
        
        # Populate table with data
        budget_table.setRowCount(len(categories))
        for row, (category, budget, act) in enumerate(zip(categories, budgeted, actual)):
            # Category name
            category_item = QTableWidgetItem(category)
            budget_table.setItem(row, 0, category_item)
            
            # Budgeted amount
            budget_item = QTableWidgetItem(f"${budget:,.2f}")
            budget_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            budget_table.setItem(row, 1, budget_item)