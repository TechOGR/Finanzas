#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sqlite3
from datetime import datetime

class DatabaseManager:
    """Manages all database operations for the financial management software."""
    
    def __init__(self, db_path=None):
        """Initialize the database manager.
        
        Args:
            db_path (str, optional): Path to the database file. Defaults to None.
        """
        if db_path is None:
            # Create database in the data directory
            data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
            os.makedirs(data_dir, exist_ok=True)
            self.db_path = os.path.join(data_dir, 'finanzas.db')
        else:
            self.db_path = db_path
        
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """Connect to the database."""
        self.conn = sqlite3.connect(self.db_path)
        # Enable foreign keys
        self.conn.execute('PRAGMA foreign_keys = ON')
        # Return dictionary-like objects instead of tuples
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
    
    def disconnect(self):
        """Disconnect from the database."""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None
    
    def commit(self):
        """Commit changes to the database."""
        if self.conn:
            self.conn.commit()
    
    def setup_database(self):
        """Create database tables if they don't exist."""
        self.connect()
        
        # Create categories table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            type TEXT NOT NULL,
            color TEXT NOT NULL,
            icon TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create accounts table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            type TEXT NOT NULL,
            currency TEXT NOT NULL,
            initial_balance REAL NOT NULL DEFAULT 0,
            current_balance REAL NOT NULL DEFAULT 0,
            description TEXT,
            color TEXT,
            icon TEXT,
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create transactions table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER NOT NULL,
            category_id INTEGER,
            amount REAL NOT NULL,
            type TEXT NOT NULL,
            description TEXT,
            date TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE,
            FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
        )
        ''')
        
        # Create budgets table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER,
            amount REAL NOT NULL,
            period TEXT NOT NULL,
            start_date TIMESTAMP NOT NULL,
            end_date TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
        )
        ''')
        
        # Create financial goals table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            target_amount REAL NOT NULL,
            current_amount REAL NOT NULL DEFAULT 0,
            deadline TIMESTAMP,
            description TEXT,
            is_completed INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create recurring transactions table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS recurring_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER NOT NULL,
            category_id INTEGER,
            amount REAL NOT NULL,
            type TEXT NOT NULL,
            description TEXT,
            frequency TEXT NOT NULL,
            start_date TIMESTAMP NOT NULL,
            end_date TIMESTAMP,
            last_occurrence TIMESTAMP,
            next_occurrence TIMESTAMP,
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE,
            FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
        )
        ''')
        
        # Insert default categories if they don't exist
        default_categories = [
            ('Alimentación', 'expense', '#FF5733', 'food'),
            ('Transporte', 'expense', '#33A8FF', 'car'),
            ('Vivienda', 'expense', '#33FF57', 'home'),
            ('Entretenimiento', 'expense', '#A833FF', 'movie'),
            ('Salud', 'expense', '#FF33A8', 'health'),
            ('Educación', 'expense', '#FFFF33', 'education'),
            ('Ropa', 'expense', '#33FFFF', 'clothes'),
            ('Servicios', 'expense', '#FF8333', 'utilities'),
            ('Salario', 'income', '#33FF33', 'money'),
            ('Inversiones', 'income', '#3333FF', 'chart'),
            ('Regalos', 'income', '#FF33FF', 'gift'),
            ('Otros Ingresos', 'income', '#FFFF33', 'other'),
            ('Transferencia', 'transfer', '#888888', 'transfer')
        ]
        
        for category in default_categories:
            self.cursor.execute('''
            INSERT OR IGNORE INTO categories (name, type, color, icon)
            VALUES (?, ?, ?, ?)
            ''', category)
        
        # Commit changes and disconnect
        self.commit()
        self.disconnect()
    
    # Account methods
    def add_account(self, name, type, currency, initial_balance, description=None, color=None, icon=None):
        """Add a new account."""
        self.connect()
        try:
            self.cursor.execute('''
            INSERT INTO accounts (name, type, currency, initial_balance, current_balance, description, color, icon)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, type, currency, initial_balance, initial_balance, description, color, icon))
            account_id = self.cursor.lastrowid
            self.commit()
            return account_id
        finally:
            self.disconnect()
    
    def get_accounts(self, active_only=True):
        """Get all accounts."""
        self.connect()
        try:
            if active_only:
                self.cursor.execute('SELECT * FROM accounts WHERE is_active = 1 ORDER BY name')
            else:
                self.cursor.execute('SELECT * FROM accounts ORDER BY name')
            return [dict(account) for account in self.cursor.fetchall()]
        finally:
            self.disconnect()
    
    def get_account(self, account_id):
        """Get account by ID."""
        self.connect()
        try:
            self.cursor.execute('SELECT * FROM accounts WHERE id = ?', (account_id,))
            account = self.cursor.fetchone()
            return dict(account) if account else None
        finally:
            self.disconnect()
    
    def update_account(self, account_id, **kwargs):
        """Update account details."""
        self.connect()
        try:
            # Build the SET part of the SQL query
            set_clause = ', '.join([f'{key} = ?' for key in kwargs.keys()])
            values = list(kwargs.values())
            values.append(account_id)
            
            self.cursor.execute(f'UPDATE accounts SET {set_clause} WHERE id = ?', values)
            self.commit()
            return self.cursor.rowcount > 0
        finally:
            self.disconnect()
    
    # Transaction methods
    def add_transaction(self, account_id, amount, type, date, category_id=None, description=None):
        """Add a new transaction."""
        self.connect()
        try:
            # Convert date string to datetime if needed
            if isinstance(date, str):
                date = datetime.strptime(date, '%Y-%m-%d')
            
            # Insert the transaction
            self.cursor.execute('''
            INSERT INTO transactions (account_id, category_id, amount, type, description, date)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (account_id, category_id, amount, type, description, date))
            transaction_id = self.cursor.lastrowid
            
            # Update account balance
            if type == 'income':
                self.cursor.execute('''
                UPDATE accounts SET current_balance = current_balance + ? WHERE id = ?
                ''', (amount, account_id))
            elif type == 'expense':
                self.cursor.execute('''
                UPDATE accounts SET current_balance = current_balance - ? WHERE id = ?
                ''', (amount, account_id))
            elif type == 'transfer':
                # For transfers, we need the destination account ID in the description
                # Format: "Transfer to/from Account:ID"
                if description and ':' in description:
                    dest_account_id = int(description.split(':')[-1])
                    self.cursor.execute('''
                    UPDATE accounts SET current_balance = current_balance - ? WHERE id = ?
                    ''', (amount, account_id))
                    self.cursor.execute('''
                    UPDATE accounts SET current_balance = current_balance + ? WHERE id = ?
                    ''', (amount, dest_account_id))
            
            self.commit()
            return transaction_id
        finally:
            self.disconnect()
    
    def get_transactions(self, account_id=None, category_id=None, start_date=None, end_date=None, transaction_type=None, limit=None):
        """Get transactions with optional filtering."""
        self.connect()
        try:
            query = '''
            SELECT t.*, c.name as category_name, c.color as category_color, c.icon as category_icon,
                   a.name as account_name, a.color as account_color
            FROM transactions t 
            LEFT JOIN categories c ON t.category_id = c.id
            LEFT JOIN accounts a ON t.account_id = a.id
            WHERE 1=1
            '''
            params = []
            
            if account_id is not None:
                query += ' AND t.account_id = ?'
                params.append(account_id)
            
            if category_id is not None:
                query += ' AND t.category_id = ?'
                params.append(category_id)
            
            if start_date is not None:
                query += ' AND t.date >= ?'
                params.append(start_date)
            
            if end_date is not None:
                query += ' AND t.date <= ?'
                params.append(end_date)
            
            if transaction_type is not None:
                query += ' AND t.type = ?'
                params.append(transaction_type)
            
            query += ' ORDER BY t.date DESC'
            
            if limit is not None:
                query += ' LIMIT ?'
                params.append(limit)
            
            self.cursor.execute(query, params)
            return [dict(transaction) for transaction in self.cursor.fetchall()]
        finally:
            self.disconnect()
    
    # Category methods
    def get_categories(self, category_type=None):
        """Get all categories or categories of a specific type."""
        self.connect()
        try:
            if category_type:
                self.cursor.execute('SELECT * FROM categories WHERE type = ? ORDER BY name', (category_type,))
            else:
                self.cursor.execute('SELECT * FROM categories ORDER BY type, name')
            return [dict(category) for category in self.cursor.fetchall()]
        finally:
            self.disconnect()
    
    def add_category(self, name, type, color, icon=None):
        """Add a new category."""
        self.connect()
        try:
            self.cursor.execute('''
            INSERT INTO categories (name, type, color, icon)
            VALUES (?, ?, ?, ?)
            ''', (name, type, color, icon))
            category_id = self.cursor.lastrowid
            self.commit()
            return category_id
        finally:
            self.disconnect()
    
    # Budget methods
    def add_budget(self, category_id, amount, period, start_date, end_date):
        """Add a new budget."""
        self.connect()
        try:
            self.cursor.execute('''
            INSERT INTO budgets (category_id, amount, period, start_date, end_date)
            VALUES (?, ?, ?, ?, ?)
            ''', (category_id, amount, period, start_date, end_date))
            budget_id = self.cursor.lastrowid
            self.commit()
            return budget_id
        finally:
            self.disconnect()
    
    def get_budgets(self, active_only=True):
        """Get all budgets."""
        self.connect()
        try:
            query = '''
            SELECT b.*, c.name as category_name, c.color as category_color, c.icon as category_icon 
            FROM budgets b 
            LEFT JOIN categories c ON b.category_id = c.id
            '''
            
            if active_only:
                current_date = datetime.now().strftime('%Y-%m-%d')
                query += f" WHERE b.end_date >= '{current_date}'"
            
            query += ' ORDER BY b.start_date'
            
            self.cursor.execute(query)
            return [dict(budget) for budget in self.cursor.fetchall()]
        finally:
            self.disconnect()
    
    # Goal methods
    def add_goal(self, name, target_amount, deadline=None, description=None):
        """Add a new financial goal."""
        self.connect()
        try:
            self.cursor.execute('''
            INSERT INTO goals (name, target_amount, deadline, description)
            VALUES (?, ?, ?, ?)
            ''', (name, target_amount, deadline, description))
            goal_id = self.cursor.lastrowid
            self.commit()
            return goal_id
        finally:
            self.disconnect()
    
    def get_goals(self, active_only=True):
        """Get all goals."""
        self.connect()
        try:
            query = 'SELECT * FROM goals'
            if active_only:
                query += ' WHERE is_completed = 0'
            self.cursor.execute(query)
            return [dict(goal) for goal in self.cursor.fetchall()]
        finally:
            self.disconnect()