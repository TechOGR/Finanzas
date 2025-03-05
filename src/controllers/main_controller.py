#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.models.database_manager import DatabaseManager
from src.views.main_window import MainWindow

class MainController:
    """Main controller for the financial management application.
    
    This controller connects the views with the database model and
    handles the application logic and data flow.
    """
    
    def __init__(self, main_window, db_manager):
        """Initialize the main controller.
        
        Args:
            main_window (MainWindow): The main window view
            db_manager (DatabaseManager): The database manager model
        """
        self.main_window = main_window
        self.db_manager = db_manager
        
        # Connect signals and slots
        self.connect_signals()
        
        # Load initial data
        self.load_initial_data()
    
    def connect_signals(self):
        """Connect UI signals to controller slots."""
        # Connect main window actions
        self.main_window.accounts_view.add_account_requested.connect(self.add_account)
        self.main_window.transactions_view.add_transaction_requested.connect(self.add_transaction)
        self.main_window.budgets_view.add_budget_requested.connect(self.add_budget)
        self.main_window.goals_view.add_goal_requested.connect(self.add_goal)
        self.main_window.goals_view.edit_goal_requested.connect(self.edit_goal)
        self.main_window.goals_view.delete_goal_requested.connect(self.delete_goal)
        
        # Connect settings signals
        self.main_window.settings_view.settings_saved.connect(self.save_settings)
        
        # Connect toolbar and menu actions
        self.main_window.generate_report_signal.connect(self.generate_report)
    
    def load_initial_data(self):
        """Load initial data from the database to the views."""
        # Load accounts data
        accounts = self.db_manager.get_accounts()
        self.main_window.accounts_view.load_accounts(accounts)
        
        # Load recent transactions
        transactions = self.db_manager.get_transactions(limit=10)
        self.main_window.transactions_view.load_transactions(transactions)
        
        # Load budgets
        budgets = self.db_manager.get_budgets()
        self.main_window.budgets_view.load_budgets(budgets)
        
        # Update dashboard with summary data
        self.update_dashboard()
    
    def update_dashboard(self):
        """Update dashboard with current financial data."""
        # Get financial summary data
        accounts = self.db_manager.get_accounts()
        
        # Calculate total balance
        total_balance = sum(account['current_balance'] for account in accounts)
        
        # Get transactions for the current month
        from datetime import datetime, timedelta
        today = datetime.now()
        first_day = datetime(today.year, today.month, 1)
        last_month = first_day - timedelta(days=1)
        first_day_last_month = datetime(last_month.year, last_month.month, 1)
        
        # Get current month transactions
        current_month_transactions = self.db_manager.get_transactions(
            start_date=first_day.strftime('%Y-%m-%d'),
            end_date=today.strftime('%Y-%m-%d')
        )
        
        # Get last month transactions
        last_month_transactions = self.db_manager.get_transactions(
            start_date=first_day_last_month.strftime('%Y-%m-%d'),
            end_date=last_month.strftime('%Y-%m-%d')
        )
        
        # Calculate income and expenses for current month
        current_income = sum(t['amount'] for t in current_month_transactions if t['type'] == 'income')
        current_expenses = sum(t['amount'] for t in current_month_transactions if t['type'] == 'expense')
        
        # Calculate income and expenses for last month
        last_income = sum(t['amount'] for t in last_month_transactions if t['type'] == 'income')
        last_expenses = sum(t['amount'] for t in last_month_transactions if t['type'] == 'expense')
        
        # Calculate percentage changes
        income_change = ((current_income - last_income) / last_income * 100) if last_income > 0 else 0
        expense_change = ((current_expenses - last_expenses) / last_expenses * 100) if last_expenses > 0 else 0
        
        # Calculate savings
        savings = current_income - current_expenses
        savings_percentage = (savings / current_income * 100) if current_income > 0 else 0
        
        # Get active budgets
        budgets = self.db_manager.get_budgets(active_only=True)
        
        # Calculate budget remaining
        total_budget = sum(budget['amount'] for budget in budgets)
        budget_spent = current_expenses
        budget_remaining = total_budget - budget_spent
        budget_percentage = (budget_remaining / total_budget * 100) if total_budget > 0 else 0
        
        # Get active goals
        goals = self.db_manager.get_goals(active_only=True)
        active_goals_count = len(goals)
        
        # Calculate goals progress
        if active_goals_count > 0:
            goals_progress = sum(goal['current_amount'] / goal['target_amount'] for goal in goals if goal['target_amount'] > 0) / active_goals_count * 100
        else:
            goals_progress = 0
        
        # Get expense categories data for pie chart
        categories = {}
        for transaction in current_month_transactions:
            if transaction['type'] == 'expense' and transaction['category_name']:
                category = transaction['category_name']
                if category not in categories:
                    categories[category] = {
                        'amount': 0,
                        'color': transaction['category_color'] or '#FF5733'
                    }
                categories[category]['amount'] += transaction['amount']
        
        # Prepare data for expense categories chart
        category_names = list(categories.keys())
        category_values = [categories[cat]['amount'] for cat in category_names]
        category_colors = [categories[cat]['color'] for cat in category_names]
        
        # Get monthly data for income vs expenses chart
        months_data = {}
        for i in range(6):
            month_date = today - timedelta(days=30*i)
            month_name = month_date.strftime('%b')
            first_day = datetime(month_date.year, month_date.month, 1)
            if month_date.month == 12:
                last_day = datetime(month_date.year + 1, 1, 1) - timedelta(days=1)
            else:
                last_day = datetime(month_date.year, month_date.month + 1, 1) - timedelta(days=1)
            
            # Get transactions for this month
            month_transactions = self.db_manager.get_transactions(
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
        
        # Prepare data for income vs expenses chart
        chart_months = list(reversed(list(months_data.keys())))
        chart_income = [months_data[month]['income'] for month in chart_months]
        chart_expenses = [months_data[month]['expenses'] for month in chart_months]
        
        # Get recent transactions
        recent_transactions = self.db_manager.get_transactions(limit=5)
        
        # Update dashboard view with real data
        dashboard = self.main_window.dashboard_view
        
        # Update financial summary cards
        dashboard.update_summary_card("Balance Total", f"${total_balance:,.2f}", "#007ACC", 
                                    f"{'↑' if income_change >= 0 else '↓'} {abs(income_change):.1f}% desde el mes pasado")
        
        dashboard.update_summary_card("Ingresos (este mes)", f"${current_income:,.2f}", "#28A745", 
                                    f"{'↑' if income_change >= 0 else '↓'} {abs(income_change):.1f}% desde el mes pasado")
        
        dashboard.update_summary_card("Gastos (este mes)", f"${current_expenses:,.2f}", "#DC3545", 
                                    f"{'↓' if expense_change <= 0 else '↑'} {abs(expense_change):.1f}% desde el mes pasado")
        
        dashboard.update_summary_card("Ahorros", f"${savings:,.2f}", "#FFC107", 
                                    f"{savings_percentage:.1f}% de los ingresos")
        
        dashboard.update_summary_card("Presupuesto Restante", f"${budget_remaining:,.2f}", "#17A2B8", 
                                    f"{budget_percentage:.1f}% disponible")
        
        dashboard.update_summary_card("Progreso de Metas", f"{goals_progress:.0f}%", "#6F42C1", 
                                    f"{active_goals_count} metas activas")
        
        # Update charts
        dashboard.update_income_expenses_chart(chart_months, chart_income, chart_expenses)
        dashboard.update_expense_categories_chart(category_names, category_values, category_colors)
        
        # Update recent transactions
        dashboard.update_recent_transactions(recent_transactions)
    
    # Action handlers
    def add_account(self, account_data):
        """Add a new account to the database.
        
        Args:
            account_data (dict): Account data including name, type, etc.
        """
        account_id = self.db_manager.add_account(
            name=account_data['name'],
            type=account_data['type'],
            currency=account_data['currency'],
            initial_balance=account_data['initial_balance'],
            description=account_data.get('description'),
            color=account_data.get('color'),
            icon=account_data.get('icon')
        )
        
        # Refresh accounts view
        accounts = self.db_manager.get_accounts()
        self.main_window.accounts_view.load_accounts(accounts)
        
        # Update dashboard
        self.update_dashboard()
        
        return account_id
    
    def add_transaction(self, transaction_data):
        """Add a new transaction to the database.
        
        Args:
            transaction_data (dict): Transaction data including account_id, amount, etc.
        """
        transaction_id = self.db_manager.add_transaction(
            account_id=transaction_data['account_id'],
            amount=transaction_data['amount'],
            type=transaction_data['type'],
            date=transaction_data['date'],
            category_id=transaction_data.get('category_id'),
            description=transaction_data.get('description')
        )
        
        # Refresh transactions view
        transactions = self.db_manager.get_transactions(limit=10)
        self.main_window.transactions_view.load_transactions(transactions)
        
        # Update dashboard
        self.update_dashboard()
        
        return transaction_id
    
    def add_budget(self, budget_data):
        """Add a new budget to the database.
        
        Args:
            budget_data (dict): Budget data including category_id, amount, etc.
        """
        budget_id = self.db_manager.add_budget(
            category_id=budget_data['category_id'],
            amount=budget_data['amount'],
            period=budget_data['period'],
            start_date=budget_data['start_date'],
            end_date=budget_data['end_date']
        )
        
        # Refresh budgets view
        budgets = self.db_manager.get_budgets()
        self.main_window.budgets_view.load_budgets(budgets)
        
        # Update dashboard
        self.update_dashboard()
        
        return budget_id
    
    def add_goal(self, goal_data):
        """Add a new financial goal to the database.
        
        Args:
            goal_data (dict): Goal data including name, target_amount, etc.
        """
        goal_id = self.db_manager.add_goal(
            name=goal_data['name'],
            target_amount=goal_data['target_amount'],
            deadline=goal_data.get('deadline'),
            description=goal_data.get('description')
        )
        
        # Refresh goals view
        goals = self.db_manager.get_goals()
        self.main_window.goals_view.load_goals(goals)
        
        # Update dashboard
        self.update_dashboard()
        
        return goal_id
        
    def edit_goal(self, goal_id, goal_data):
        """Edit an existing financial goal.
        
        Args:
            goal_id (int): ID of the goal to edit
            goal_data (dict): Updated goal data
        """
        self.db_manager.connect()
        try:
            # Build the SET part of the SQL query
            set_clause = ', '.join([f'{key} = ?' for key in goal_data.keys()])
            values = list(goal_data.values())
            values.append(goal_id)
            
            self.db_manager.cursor.execute(f'UPDATE goals SET {set_clause} WHERE id = ?', values)
            self.db_manager.commit()
            
            # Refresh goals view
            goals = self.db_manager.get_goals()
            self.main_window.goals_view.load_goals(goals)
            
            # Update dashboard
            self.update_dashboard()
            
            return True
        finally:
            self.db_manager.disconnect()
    
    def delete_goal(self, goal_id):
        """Delete a financial goal.
        
        Args:
            goal_id (int): ID of the goal to delete
        """
        self.db_manager.connect()
        try:
            self.db_manager.cursor.execute('DELETE FROM goals WHERE id = ?', (goal_id,))
            self.db_manager.commit()
            
            # Refresh goals view
            goals = self.db_manager.get_goals()
            self.main_window.goals_view.load_goals(goals)
            
            # Update dashboard
            self.update_dashboard()
            
            return True
        finally:
            self.db_manager.disconnect()
    
    def save_settings(self, settings):
        """Save application settings.
        
        Args:
            settings (dict): Dictionary of settings
        """
        # In a real app, this would save to a settings file or database
        # For now, we'll just print the settings
        print("Saving settings:", settings)
        
        # Apply theme if changed
        if 'theme' in settings:
            theme = settings['theme']
            # Apply theme changes
            
        # Apply language if changed
        if 'language' in settings:
            language = settings['language']
            # Apply language changes
            
        return True
    
    def generate_report(self, report_type=None):
        """Generate a financial report.
        
        Args:
            report_type (str, optional): Type of report to generate. Defaults to None.
        """
        # Switch to reports tab
        self.main_window.tab_widget.setCurrentIndex(4)  # Index of reports tab
        
        # Generate the report
        self.main_window.reports_view.generate_report(report_type)