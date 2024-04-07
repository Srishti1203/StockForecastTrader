import yfinance as yf
from datetime import date, timedelta
from prophet import Prophet
import numpy as np
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from yahoo_fin import stock_info
import matplotlib.pyplot as plt
import mysql.connector
from datetime import datetime

stocks = {
    "AAPL": "Apple",
    "TSLA": "Tesla",
    "AMZN": "Amazon",
    "RELIANCE.NS": "Reliance Industries",
    "INFY.NS": "Infosys",
    "TCS.NS": "Tata Consultancy Services",
    "HINDUNILVR.NS": "Hindustan Unilever",
    "SBIN.NS": "State Bank of India",
    "LT.NS": "Larsen & Toubro",
    "HCLTECH.NS": "HCL Technologies",
    "WIPRO.NS": "Wipro",
    "GOOGL": "Alphabet Inc.",
    "MSFT": "Microsoft",
    "META": "Meta Platforms, Inc.",
    "IBM": "IBM",
    "INTC": "Intel",
    "CSCO": "Cisco Systems",
    "AXISBANK.NS": "Axis Bank",
    "ONGC.NS": "Oil and Natural Gas Corporation",
    "CIPLA.NS": "Cipla"
}


def load_data(ticker):
    data = yf.download(ticker, start=START, end=TODAY)
    return data

START = (date.today() - timedelta(days=365)).strftime("%Y-%m-%d")
TODAY = date.today().strftime("%Y-%m-%d")

class StockApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Stock Market Analysis')
        self.data = None
        self.forecast = None
        self.root.geometry("800x600")
        self.set_styles()

        self.user_name = simpledialog.askstring("Input", "What is your name?")
        self.user_birthdate = simpledialog.askstring("Input", "Enter your birthdate (YYYY-MM-DD):")

        self.selected_stock = tk.StringVar()
        self.n_years = tk.IntVar()

        self.nominee_name = ""
        self.nominee_id = ""

        self.db = mysql.connector.connect(
            host="DESKTOP-U05QIL0",
            user="root@localhost",
            password="srishti pandey",
            database="stock_market"
        )
        self.cursor = self.db.cursor()

        self.verify_user_age()

    def set_styles(self):
        style = ttk.Style()

        style.configure("Heading.TLabel", font=("Helvetica", 20, "bold"), foreground="blue")

        style.configure("Subheading.TLabel", font=("Helvetica", 14, "italic"), foreground="green")

        style.configure("TLabel", font=("Helvetica", 12))

        style.configure("TButton", font=("Helvetica", 12))

    def verify_user_age(self):
        try:
            birthdate = date.fromisoformat(self.user_birthdate)
            age = (date.today() - birthdate).days // 365
            if age < 18:
                messagebox.showwarning("Warning", "You must be 18 or above to proceed.")
                self.root.destroy()
            else:
                self.verify_user_identity()
        except ValueError:
            messagebox.showerror("Error", "Invalid birthdate format. Please use YYYY-MM-DD.")
            self.root.destroy()

    def save_user_info(self):
        query = "INSERT INTO user (name, birthdate, card_number, income, nominee_name, nominee_id) " \
                "VALUES (%s, %s, %s, %s, %s, %s)"
        values = (self.user_name, self.user_birthdate, self.card_number, self.income, self.nominee_name, self.nominee_id)
        print("Inserting user information into the database:", values)
        self.cursor.execute(query, values)
        self.db.commit()
        print("User information inserted successfully.")

    def save_stock_prices(self, stock, prev_price, latest_price):
        query = "INSERT INTO stockprices (stock, prev_price, latest_price) VALUES (%s, %s, %s)"
        values = (stocks[stock], prev_price, latest_price)
        self.cursor.execute(query, values)
        self.db.commit()

    def verify_user_identity(self):
        self.card_number = simpledialog.askstring("Input", "Enter your 12-digit card number:")
        self.income = simpledialog.askfloat("Input", "Enter your monthly income:")

        self.nominee_name = simpledialog.askstring("Input", "Enter your nominee's name:")
        self.nominee_id = simpledialog.askstring("Input", "Enter your nominee's 12-digit ID number:")
        self.save_user_info()
        print("Nominee information collected:", self.nominee_name, self.nominee_id)
 
        self.show_investment_suggestions()

    def show_investment_suggestions(self):
 
        self.create_widgets()
    def trade_stock(self, stock, quantity, buy=True):
        if buy:
            print(f"Buying {quantity} shares of {stocks[stock]}")

            current_price = stock_info.get_live_price(stock)

            total_cost = current_price * quantity

            self.save_user_transaction(stock, "BUY", current_price, quantity)

            messagebox.showinfo("Success", f"You have successfully bought {quantity} stocks of {stocks[stock]} at a total cost of {total_cost:.2f}.")

        else:
            print(f"Selling {quantity} shares of {stocks[stock]}")

            current_price = stock_info.get_live_price(stock)

            total_revenue = current_price * quantity

            self.save_user_transaction(stock, "SELL", current_price, quantity)

            messagebox.showinfo("Success", f"You have successfully sold {quantity} stocks of {stocks[stock]} at a total revenue of {total_revenue:.2f}.")

        self.reload_prices()
    def reload_prices(self):

        for ticker in stocks.keys():
            prev_price = float(self.live_price_labels[ticker].cget("text").split(":")[1])
            latest_price = stock_info.get_live_price(ticker)
            self.live_price_labels[ticker].config(text=f"Price: {latest_price:.2f}")

            self.update_table(ticker, prev_price, latest_price)

            self.save_stock_prices(ticker, prev_price, latest_price)

    def create_table(self):
        columns = ["Stock", "Previous Price", "Latest Price"]
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings", height=5)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor="center")

        self.tree.grid(row=0, column=0)

    def update_table(self, stock, prev_price, latest_price):

        self.tree.insert("", "end", values=(stocks[stock], f"{prev_price:.2f}", f"{latest_price:.2f}"))

    def create_widgets(self):
           def show_investment_suggestions(self):

                self.create_widgets()

    def create_widgets(self):

        canvas = tk.Canvas(self.root)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(self.root, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=frame, anchor="nw")

        user_frame = ttk.Frame(frame)
        user_frame.grid(row=0, column=2, padx=10, pady=10, sticky="ne")

        ttk.Label(user_frame, text="User Information", style="Heading.TLabel").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        ttk.Label(user_frame, text=f"Name: {self.user_name}", style="TLabel").grid(row=1, column=0, padx=5, pady=2, sticky="e")
        ttk.Label(user_frame, text=f"DOB: {self.user_birthdate}", style="TLabel").grid(row=2, column=0, padx=5, pady=2, sticky="e")
        ttk.Label(user_frame, text=f"Nominee: {self.nominee_name}", style="TLabel").grid(row=3, column=0, padx=5, pady=2, sticky="e")
        ttk.Label(user_frame, text=f"Nominee ID: {self.nominee_id}", style="TLabel").grid(row=4, column=0, padx=5, pady=2, sticky="e")

        ttk.Label(frame, text="Live Stock Prices", style="Heading.TLabel").grid(row=0, column=0, padx=10, pady=10, columnspan=3)

        self.live_price_labels = {}

        row_index = 1
        for ticker, name in stocks.items():
            ttk.Label(frame, text=f"{name} ({ticker})", style="TLabel").grid(row=row_index, column=0, padx=5, pady=5)
            price = stock_info.get_live_price(ticker)
            label = ttk.Label(frame, text=f"Price: {price:.2f}", style="TLabel")
            label.grid(row=row_index, column=1, padx=5, pady=5)
            self.live_price_labels[ticker] = label
            row_index += 1

        ttk.Button(frame, text="Reload", command=self.reload_prices, style="TButton").grid(row=row_index, column=0, columnspan=2, pady=10)

        ttk.Label(frame, text="Stock Forecast App", style="Heading.TLabel").grid(row=row_index, column=2, padx=10, pady=10, columnspan=2)
        row_index += 1

        ttk.Label(frame, text="Previous Price").grid(row=row_index + 1, column=2, padx=5, pady=5)
        ttk.Label(frame, text="Latest Price").grid(row=row_index + 1, column=3, padx=5, pady=5)

        
        self.table_frame = ttk.Frame(frame)
        self.table_frame.grid(row=row_index + 2, column=2, columnspan=2, pady=10)
        self.create_table()

        row_index += 3  

        ttk.Label(frame, text="Select dataset for prediction:").grid(row=row_index, column=0, padx=5, pady=5)
        stock_dropdown = ttk.Combobox(frame, textvariable=self.selected_stock, values=list(stocks.keys()))
        stock_dropdown.grid(row=row_index, column=1, padx=5, pady=5)

        row_index += 1

        ttk.Label(frame, text="Years of prediction:").grid(row=row_index, column=0, padx=5, pady=5)
        years_slider = ttk.Scale(frame, from_=1, to=4, variable=self.n_years, orient="horizontal", length=200)
        years_slider.grid(row=row_index, column=1, padx=5, pady=5)

        row_index += 1

        ttk.Button(frame, text="Analyze", command=self.analyze_stock).grid(row=row_index, column=0, columnspan=2, pady=10)

        suggestion_label = ttk.Label(frame, text="Suggestion: Follow the 50/30/20 rule for budgeting.", font=("Helvetica", 10, "italic"), foreground="green")
        suggestion_label.grid(row=row_index + 1, column=2, columnspan=2, pady=10)

        ttk.Label(user_frame, text=f"Nominee: {self.nominee_name}").grid(row=3, column=0, padx=5, pady=2, sticky="e")
        ttk.Label(user_frame, text=f"Nominee ID: {self.nominee_id}").grid(row=4, column=0, padx=5, pady=2, sticky="e")
        ttk.Label(frame, text="Select stock:").grid(row=row_index, column=0, padx=5, pady=5)
        stock_to_trade_dropdown = ttk.Combobox(frame, values=list(stocks.keys()))
        stock_to_trade_dropdown.grid(row=row_index, column=1, padx=5, pady=5)

        row_index += 1

        ttk.Label(frame, text="Quantity:").grid(row=row_index, column=0, padx=5, pady=5)
        quantity_entry = ttk.Entry(frame)
        quantity_entry.grid(row=row_index, column=1, padx=5, pady=5)

        row_index += 1

        ttk.Button(frame, text="Buy", command=lambda: self.trade_stock(stock_to_trade_dropdown.get(), int(quantity_entry.get()), buy=True)).grid(row=row_index, column=0, pady=10)
        ttk.Button(frame, text="Sell", command=lambda: self.trade_stock(stock_to_trade_dropdown.get(), int(quantity_entry.get()), buy=False)).grid(row=row_index, column=1, pady=10)
    def trade_stock(self, stock, quantity, buy=True):
        if buy:
            print(f"Buying {quantity} shares of {stocks[stock]}")
        else:
            print(f"Selling {quantity} shares of {stocks[stock]}")
    def reload_prices(self):
        for ticker in stocks.keys():
            prev_price = float(self.live_price_labels[ticker].cget("text").split(":")[1])
            latest_price = stock_info.get_live_price(ticker)
            self.live_price_labels[ticker].config(text=f"Price: {latest_price:.2f}")

            self.update_table(ticker, prev_price, latest_price)

    def create_table(self):
        columns = ["Stock", "Previous Price", "Latest Price"]
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings", height=5)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor="center")

        self.tree.grid(row=0, column=0)

    def update_table(self, stock, prev_price, latest_price):
        self.tree.insert("", "end", values=(stocks[stock], f"{prev_price:.2f}", f"{latest_price:.2f}"))

    def analyze_stock(self):
        selected_stock = self.selected_stock.get()
        n_years = self.n_years.get()
        period = n_years * 365

        print('Loading data...')
        self.data = load_data(selected_stock)
        print('Loading data... done!')

        if self.data['Close'].count() < 2:
            print("Insufficient data for training. Please select a different stock or time period.")
            return

        print('Raw data:')
        print(self.data.tail())
        df_train = self.data[['Close']].rename(columns={"Close": "y"}).reset_index().rename(columns={"Date": "ds"})

        m = Prophet()
        m.fit(df_train)
        future = m.make_future_dataframe(periods=period)
        forecast = m.predict(future)

        self.forecast = forecast
        self.display_analysis_results()

        print('Forecast data:')
        print(forecast.tail())

        fig, ax = plt.subplots()
        ax.plot(self.data.index, self.data['Close'], label="Stock Price")
        ax.set_title('Stock Performance')
        ax.set_xlabel('Date')
        ax.set_ylabel('Price')
        ax.legend()
        plt.show()
        fig1 = m.plot(forecast)
        plt.title(f'Forecast plot for {n_years} years')
        plt.show()

        fig2 = m.plot_components(forecast)
        plt.show()

        self.display_analysis_results()
    def display_analysis_results(self):
        if self.data is None or self.forecast is None: 
            messagebox.showwarning("Warning", "Please analyze stock first.")
            return

        data = self.data
        forecast = self.forecast
        if 'yhat' not in self.forecast.columns:
            messagebox.showwarning("Warning", "Analysis results are not available. Please analyze stock first.")
            return

        last_forecasted_price = self.forecast['yhat'].iloc[-1]
        self.show_buy_sell_prompt(last_forecasted_price)
    def show_buy_sell_prompt(self, last_forecasted_price):      
        suggestion = "Buy" if last_forecasted_price > self.forecast['yhat'].iloc[-2] else "Don't Buy"

        messagebox.showinfo("Stock Analysis", f"Suggestion: {suggestion}")
        print(f"Suggestion: {suggestion}")

        df_train = self.data[['Close']].rename(columns={"Close": "y"}).reset_index().rename(columns={"Date": "ds"})

        m = Prophet()
        m.fit(df_train)
        future = m.make_future_dataframe(periods=365)
        forecast = m.predict(future)

        print('Forecast data:')
        print(forecast.tail())

if __name__ == "__main__":
    root = tk.Tk()
    app = StockApp(root)
    root.mainloop()
