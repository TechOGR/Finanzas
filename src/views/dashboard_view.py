#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QGridLayout, QPushButton, QSizePolicy,
                             QScrollArea, QTableWidget, QTableWidgetItem, QHeaderView,
                             QDialog, QFormLayout, QLineEdit, QComboBox, QDoubleSpinBox, 
                             QTextEdit, QDialogButtonBox, QMessageBox, QDateEdit, QProgressBar)
from PyQt5.QtCore import Qt, QSize, QRect, QRectF
from PyQt5.QtGui import QFont, QIcon, QColor, QPainter, QPen
import pyqtgraph as pg
import os
import numpy as np
from math import pi

class PieChartItem(pg.GraphicsObject):
    """Custom pie chart item for pyqtgraph."""
    
    def __init__(self, values, colors, labels=None):
        pg.GraphicsObject.__init__(self)
        self.values = np.array(values)
        self.colors = colors
        self.labels = labels
        self.total = sum(values)
        self.startAngles = np.zeros(len(values))
        self.angles = 2 * pi * self.values / self.total
        
        # Calculate start angles
        for i in range(1, len(values)):
            self.startAngles[i] = self.startAngles[i-1] + self.angles[i-1]
    
    def paint(self, painter, option, widget):
        painter.setPen(QPen(Qt.black, 1))
        
        # Draw pie segments
        center = QSize(0, 0)
        radius = 100
        rect = QRect(center.width() - radius, center.height() - radius, 2 * radius, 2 * radius)
        
        for i in range(len(self.values)):
            startAngle = int(self.startAngles[i] * 180 / pi * 16)
            spanAngle = int(self.angles[i] * 180 / pi * 16)
            painter.setBrush(QColor(self.colors[i]))
            painter.drawPie(rect, startAngle, spanAngle)
    
    def boundingRect(self):
        return QRectF(-120, -120, 240, 240)

class DashboardView(QWidget):
    """Dashboard view showing financial overview and summaries."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Create scroll area for responsiveness
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        # Create scroll content widget
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(20)
        
        # Add welcome section
        scroll_layout.addWidget(self.create_welcome_section())
        
        # Add financial summary section
        scroll_layout.addWidget(self.create_financial_summary())
        
        # Add charts section
        scroll_layout.addWidget(self.create_charts_section())
        
        # Add quick actions section
        scroll_layout.addWidget(self.create_quick_actions())
        
        # Add recent transactions section
        scroll_layout.addWidget(self.create_recent_transactions())
        
        # Set scroll content and add to main layout
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
    
    def create_welcome_section(self):
        """Create welcome section with user greeting and date."""
        frame = QFrame()
        frame.setObjectName("welcomeFrame")
        frame.setStyleSheet("""
            #welcomeFrame {
                background-color: #2D2D30;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Welcome message
        welcome_label = QLabel("¡Bienvenido a Finanzas!")
        welcome_font = QFont("Segoe UI", 18, QFont.Bold)
        welcome_label.setFont(welcome_font)
        layout.addWidget(welcome_label)
        
        # Subtitle
        subtitle_label = QLabel("Tu asistente de gestión financiera personal")
        subtitle_font = QFont("Segoe UI", 12)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setStyleSheet("color: #AAAAAA;")
        layout.addWidget(subtitle_label)
        
        return frame
    
    def create_financial_summary(self):
        """Create financial summary section with account balances and totals."""
        frame = QFrame()
        frame.setObjectName("summaryFrame")
        frame.setStyleSheet("""
            #summaryFrame {
                background-color: #2D2D30;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Section title
        title_label = QLabel("Resumen Financiero")
        title_font = QFont("Segoe UI", 14, QFont.Bold)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Cards layout
        cards_layout = QGridLayout()
        cards_layout.setContentsMargins(0, 10, 0, 0)
        cards_layout.setSpacing(15)
        
        # Total balance card
        balance_card = self.create_summary_card(
            "Balance Total", 
            "$10,250.00", 
            "#007ACC", 
            "↑ 5.2% desde el mes pasado"
        )
        cards_layout.addWidget(balance_card, 0, 0)
        
        # Income card
        income_card = self.create_summary_card(
            "Ingresos (este mes)", 
            "$3,500.00", 
            "#28A745", 
            "↑ 2.1% desde el mes pasado"
        )
        cards_layout.addWidget(income_card, 0, 1)
        
        # Expenses card
        expenses_card = self.create_summary_card(
            "Gastos (este mes)", 
            "$2,180.00", 
            "#DC3545", 
            "↓ 3.5% desde el mes pasado"
        )
        cards_layout.addWidget(expenses_card, 0, 2)
        
        # Savings card
        savings_card = self.create_summary_card(
            "Ahorros", 
            "$1,320.00", 
            "#FFC107", 
            "37.7% de los ingresos"
        )
        cards_layout.addWidget(savings_card, 1, 0)
        
        # Budget card
        budget_card = self.create_summary_card(
            "Presupuesto Restante", 
            "$820.00", 
            "#17A2B8", 
            "27.3% disponible"
        )
        cards_layout.addWidget(budget_card, 1, 1)
        
        # Goals progress card
        goals_card = self.create_summary_card(
            "Progreso de Metas", 
            "45%", 
            "#6F42C1", 
            "2 metas activas"
        )
        cards_layout.addWidget(goals_card, 1, 2)
        
        layout.addLayout(cards_layout)
        
        return frame
    
    def create_summary_card(self, title, value, color, subtitle):
        """Create a summary card with title, value and subtitle."""
        card = QFrame()
        card.setObjectName("summaryCard")
        card.setStyleSheet(f"""
            #summaryCard {{
                background-color: #252529;
                border-radius: 8px;
                border-left: 4px solid {color};
            }}
        """)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        card.setMinimumHeight(100)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Title
        title_label = QLabel(title)
        title_font = QFont("Segoe UI", 10)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #AAAAAA;")
        layout.addWidget(title_label)
        
        # Value
        value_label = QLabel(value)
        value_font = QFont("Segoe UI", 16, QFont.Bold)
        value_label.setFont(value_font)
        layout.addWidget(value_label)
        
        # Subtitle
        subtitle_label = QLabel(subtitle)
        subtitle_font = QFont("Segoe UI", 9)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setStyleSheet(f"color: {color};")
        layout.addWidget(subtitle_label)
        
        return card
    
    def create_charts_section(self):
        """Create charts section with financial visualizations."""
        frame = QFrame()
        frame.setObjectName("chartsFrame")
        frame.setStyleSheet("""
            #chartsFrame {
                background-color: #2D2D30;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Section title
        title_label = QLabel("Gráficos Financieros")
        title_font = QFont("Segoe UI", 14, QFont.Bold)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Charts layout
        charts_layout = QHBoxLayout()
        charts_layout.setContentsMargins(0, 10, 0, 0)
        charts_layout.setSpacing(15)
        
        # Income vs Expenses chart
        income_expenses_chart = self.create_income_expenses_chart()
        charts_layout.addWidget(income_expenses_chart)
        
        # Expense categories chart
        categories_chart = self.create_expense_categories_chart()
        charts_layout.addWidget(categories_chart)
        
        layout.addLayout(charts_layout)
        
        return frame
    
    def create_income_expenses_chart(self):
        """Create income vs expenses bar chart."""
        # Set background color for the chart
        pg.setConfigOption('background', '#252529')
        pg.setConfigOption('foreground', '#DDDDDD')
        
        # Create the plot widget
        plot_widget = pg.PlotWidget()
        plot_widget.setMinimumHeight(250)
        plot_widget.setTitle("Ingresos vs Gastos (últimos 6 meses)")
        plot_widget.showGrid(x=True, y=True, alpha=0.3)
        
        # Sample data
        months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun']
        income = [3200, 3100, 3400, 3300, 3450, 3500]
        expenses = [2100, 2300, 2200, 2400, 2250, 2180]
        
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
        
        return plot_widget
    
    def create_expense_categories_chart(self):
        """Create expense categories pie chart."""
        # Set background color for the chart
        pg.setConfigOption('background', '#252529')
        pg.setConfigOption('foreground', '#DDDDDD')
        
        # Create the plot widget
        plot_widget = pg.PlotWidget()
        plot_widget.setMinimumHeight(250)
        plot_widget.setTitle("Gastos por Categoría (este mes)")
        
        # Sample data
        categories = ['Alimentación', 'Vivienda', 'Transporte', 'Entretenimiento', 'Servicios', 'Otros']
        values = [650, 800, 250, 180, 220, 80]
        colors = ['#FF5733', '#33FF57', '#33A8FF', '#A833FF', '#FF33A8', '#FFFF33']
        
        # Create a custom view box that will contain our pie chart
        view_box = pg.ViewBox()
        plot_widget.setCentralItem(view_box)
        
        # Create a custom pie chart item
        pie = PieChartItem(values, colors, categories)
        view_box.addItem(pie)
        
        return plot_widget
    
    def create_quick_actions(self):
        """Create quick actions section with buttons for common tasks."""
        frame = QFrame()
        frame.setObjectName("actionsFrame")
        frame.setStyleSheet("""
            #actionsFrame {
                background-color: #2D2D30;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Section title
        title_label = QLabel("Acciones Rápidas")
        title_font = QFont("Segoe UI", 14, QFont.Bold)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Buttons layout
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(0, 10, 0, 0)
        buttons_layout.setSpacing(15)
        
        # Add transaction button
        add_transaction_btn = self.create_action_button("Nueva Transacción", "#007ACC")
        buttons_layout.addWidget(add_transaction_btn)
        
        # Add account button
        add_account_btn = self.create_action_button("Nueva Cuenta", "#28A745")
        buttons_layout.addWidget(add_account_btn)
        
        # Add budget button
        add_budget_btn = self.create_action_button("Nuevo Presupuesto", "#FFC107")
        buttons_layout.addWidget(add_budget_btn)
        
        return frame
    
    def create_recent_transactions(self):
        """Create recent transactions section with transactions."""
        frame = QFrame()
        frame.setObjectName("transactionsFrame")
        frame.setStyleSheet("""
            #transactionsFrame {
                background-color: #2D2D30;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Section title
        title_label = QLabel("Transacciones Recientes")
        title_font = QFont("Segoe UI", 14, QFont.Bold)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Create table for transactions
        transactions_table = QTableWidget()
        transactions_table.setColumnCount(5)
        transactions_table.setHorizontalHeaderLabels(["Fecha", "Descripción", "Categoría", "Cuenta", "Monto"])
        transactions_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        transactions_table.setAlternatingRowColors(True)
        transactions_table.setStyleSheet("""
            QTableWidget {
                background-color: #252529;
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
        
        # Sample data - in a real app, this would come from the database
        sample_data = [
            ("2023-06-15", "Supermercado", "Alimentación", "Tarjeta Principal", "-$1,250.00"),
            ("2023-06-14", "Pago de Nómina", "Ingresos", "Cuenta Bancaria", "+$15,000.00"),
            ("2023-06-12", "Restaurante", "Alimentación", "Efectivo", "-$450.00"),
            ("2023-06-10", "Gasolina", "Transporte", "Tarjeta Principal", "-$800.00"),
            ("2023-06-08", "Netflix", "Entretenimiento", "Tarjeta Principal", "-$219.00")
        ]
        
        # Populate table with sample data
        transactions_table.setRowCount(len(sample_data))
        for row, (date, desc, category, account, amount) in enumerate(sample_data):
            transactions_table.setItem(row, 0, QTableWidgetItem(date))
            transactions_table.setItem(row, 1, QTableWidgetItem(desc))
            transactions_table.setItem(row, 2, QTableWidgetItem(category))
            transactions_table.setItem(row, 3, QTableWidgetItem(account))
            
            amount_item = QTableWidgetItem(amount)
            if amount.startswith("-"):
                amount_item.setForeground(QColor("#DC3545"))  # Red for expenses
            else:
                amount_item.setForeground(QColor("#28A745"))  # Green for income
            transactions_table.setItem(row, 4, amount_item)
        
        # Set fixed height for the table
        transactions_table.setMinimumHeight(200)
        transactions_table.setMaximumHeight(250)
        
        layout.addWidget(transactions_table)
        
        # View all transactions button
        view_all_btn = QPushButton("Ver Todas las Transacciones")
        view_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #252529;
                color: #DDDDDD;
                border: 1px solid #444;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #333333;
                border: 1px solid #555;
            }
        """)
        layout.addWidget(view_all_btn)
        
        return frame
        
    def create_action_button(self, text, color):
        """Create a styled action button."""
        button = QPushButton(text)
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {color}80;
            }}
        """)
        return button

    def update_summary_card(self, title, value, color, subtitle):
        """Update a summary card with new data."""
        # Find the card by title
        for card in self.findChildren(QFrame, "summaryCard"):
            title_label = card.findChild(QLabel)
            if title_label and title_label.text() == title:
                # Update value and subtitle
                value_label = card.findChildren(QLabel)[1]
                subtitle_label = card.findChildren(QLabel)[2]
                value_label.setText(value)
                subtitle_label.setText(subtitle)
                subtitle_label.setStyleSheet(f"color: {color};")
                break

    def update_income_expenses_chart(self, months, income, expenses):
        """Update income vs expenses chart with new data."""
        # Find the income vs expenses chart frame
        charts_frame = None
        for frame in self.findChildren(QFrame, "chartsFrame"):
            charts_frame = frame
            break
            
        if charts_frame:
            # Find the plot widget (first one in the charts section)
            plot_widgets = charts_frame.findChildren(pg.PlotWidget)
            if plot_widgets and len(plot_widgets) > 0:
                widget = plot_widgets[0]  # First plot widget is income vs expenses
                
                # Clear existing items
                widget.clear()
                
                # Set title
                widget.setTitle("Ingresos vs Gastos (últimos 6 meses)")

                # Set up x-axis
                x_axis = widget.getAxis('bottom')
                x_axis.setTicks([[(i, month) for i, month in enumerate(months)]])

                # Create bar graph items
                bar_width = 0.35
                income_bars = pg.BarGraphItem(x=[i-bar_width/2 for i in range(len(months))], height=income, width=bar_width, brush='#28A745')
                expense_bars = pg.BarGraphItem(x=[i+bar_width/2 for i in range(len(months))], height=expenses, width=bar_width, brush='#DC3545')

                # Add items to the plot
                widget.addItem(income_bars)
                widget.addItem(expense_bars)

                # Add legend
                legend = pg.LegendItem((80, 60), offset=(70, 20))
                legend.setParentItem(widget.graphicsItem())
                legend.addItem(pg.BarGraphItem(x=[0], height=[1], width=bar_width, brush='#28A745'), 'Ingresos')
                legend.addItem(pg.BarGraphItem(x=[0], height=[1], width=bar_width, brush='#DC3545'), 'Gastos')

    def update_expense_categories_chart(self, categories, values, colors):
        """Update expense categories pie chart with new data."""
        # Find the charts frame
        charts_frame = None
        for frame in self.findChildren(QFrame, "chartsFrame"):
            charts_frame = frame
            break
            
        if charts_frame:
            # Find the plot widgets in the charts section
            plot_widgets = charts_frame.findChildren(pg.PlotWidget)
            if plot_widgets and len(plot_widgets) > 1:
                widget = plot_widgets[1]  # Second plot widget is expense categories
                
                # Clear existing items
                widget.clear()
                
                # Set title
                widget.setTitle("Gastos por Categoría (este mes)")

                # Create a custom view box
                view_box = pg.ViewBox()
                widget.setCentralItem(view_box)

                # Create a custom pie chart item
                if categories and values and len(categories) > 0 and len(values) > 0:
                    pie = PieChartItem(values, colors, categories)
                    view_box.addItem(pie)

    def update_recent_transactions(self, transactions):
        """Update recent transactions table with new data."""
        # Find the transactions table
        for table in self.findChildren(QTableWidget):
            if table.columnCount() == 5 and table.horizontalHeaderItem(0).text() == "Fecha":
                # Clear existing rows
                table.setRowCount(0)

                # Add new transactions
                table.setRowCount(len(transactions))
                for row, transaction in enumerate(transactions):
                    # Format date
                    date = transaction['date'].split()[0] if ' ' in transaction['date'] else transaction['date']
                    table.setItem(row, 0, QTableWidgetItem(date))
                    
                    # Description
                    desc = transaction.get('description', '')
                    table.setItem(row, 1, QTableWidgetItem(desc))
                    
                    # Category
                    category = transaction.get('category_name', '')
                    table.setItem(row, 2, QTableWidgetItem(category))
                    
                    # Account (would need to be added to transaction data)
                    account = transaction.get('account_name', '')
                    table.setItem(row, 3, QTableWidgetItem(account))
                    
                    # Amount
                    amount = transaction['amount']
                    sign = '-' if transaction['type'] == 'expense' else '+'
                    amount_text = f"{sign}${abs(amount):,.2f}"
                    amount_item = QTableWidgetItem(amount_text)
                    
                    if transaction['type'] == 'expense':
                        amount_item.setForeground(QColor("#DC3545"))  # Red for expenses
                    else:
                        amount_item.setForeground(QColor("#28A745"))  # Green for income
                    
                    table.setItem(row, 4, amount_item)
                break