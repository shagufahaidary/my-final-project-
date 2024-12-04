import requests
from tinydb import TinyDB, Query
# Database for managing users
class UserDatabase:
    def __init__(self):
        self.db = TinyDB("users.json")
    def add_user(self, username, password):
        if not self.get_user(username):  # Avoid duplicate users
            self.db.insert({"username": username, "password": password, "accounts": []})
            return True
        return False
    def get_user(self, username):
        return self.db.search(Query().username == username)
    def update_password(self, username, password):
        self.db.update({"password": password}, Query().username == username)
    def delete_user(self, username):
        self.db.remove(Query().username == username)
    def authenticate_user(self, username, password):
        user = self.get_user(username)
        if user and user[0]["password"] == password:
            return True
        return False
# User Class
class User:
    def __init__(self, username, password):
        self.userdb = UserDatabase()
        self.username = username
        self.password = password
        self.bank_accounts = []  # List of linked accounts
        if not self.userdb.authenticate_user(username, password):
            if self.userdb.add_user(username, password):
                print(f"User '{username}' registered successfully.")
            else:
                print(f"User '{username}' already exists.")
        else:
            print("User authenticated.")
    def add_bank_account(self, account):
        self.bank_accounts.append(account)
    def list_bank_accounts(self):
        for account in self.bank_accounts:
            print(f"Account Number: {account.account_number}, Balance: {account.account_balance}")
    def remove_bank_account(self, account_number):
        self.bank_accounts = [acc for acc in self.bank_accounts if acc.account_number != account_number]
# Bank Account Class
class BankAccount:
    def __init__(self, account_number, account_balance):
        self.account_number = account_number
        self.account_balance = account_balance
        self.cryptocurrencies = []
        self.transaction_history = []
        self.cryptocurrency_portfolio = {}
    def add_crypto(self, crypto):
        self.cryptocurrencies.append(crypto)
    def calculate_purchases(self):
        print("\nWith your current account balance, you can buy:")
        for crypto in self.cryptocurrencies:
            amount = round(self.account_balance / crypto.price, 6)
            print(f"{crypto.name}: {amount}")
    def buy_crypto(self, crypto_name, amount_usd):
        for crypto in self.cryptocurrencies:
            if crypto.name.lower() == crypto_name.lower():
                if amount_usd > self.account_balance:
                    print("Insufficient funds!")
                    return
                self.account_balance -= amount_usd
                amount_crypto = round(amount_usd / crypto.price, 6)
                self.transaction_history.append(f"Bought {amount_crypto} {crypto.name}")
                self.cryptocurrency_portfolio[crypto_name] = self.cryptocurrency_portfolio.get(crypto_name, 0) + amount_crypto
                print(f"Successfully bought {amount_crypto} {crypto.name}")
                return
        print(f"Cryptocurrency {crypto_name} not found!")
    def sell_crypto(self, crypto_name, amount_crypto):
        if crypto_name not in self.cryptocurrency_portfolio or self.cryptocurrency_portfolio[crypto_name] < amount_crypto:
            print("Insufficient cryptocurrency to sell!")
            return
        for crypto in self.cryptocurrencies:
            if crypto.name.lower() == crypto_name.lower():
                self.cryptocurrency_portfolio[crypto_name] -= amount_crypto
                amount_usd = round(amount_crypto * crypto.price, 2)
                self.account_balance += amount_usd
                self.transaction_history.append(f"Sold {amount_crypto} {crypto.name} for ${amount_usd}")
                print(f"Successfully sold {amount_crypto} {crypto.name}")
                return
        print(f"Cryptocurrency {crypto_name} not found!")
    def show_transaction_history(self):
        print("\nTransaction History:")
        if not self.transaction_history:
            print("No transactions found.")
        else:
            for transaction in self.transaction_history:
                print(transaction)
    def show_portfolio(self):
        print("\nCryptocurrency Portfolio:")
        if not self.cryptocurrency_portfolio:
            print("No cryptocurrencies in portfolio.")
        else:
            for crypto_name, amount in self.cryptocurrency_portfolio.items():
                print(f"{crypto_name}: {amount}")
        print(f"\nAccount Balance: ${self.account_balance}")
# Cryptocurrencies Class
class CryptoCurrency:
    def __init__(self, name, price):
        self.name = name
        self.price = price
# Fetch Cryptocurrency Prices Using API
def fetch_crypto_prices():
    api_url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,litecoin&vs_currencies=usd"
    response = requests.get(api_url)
    if response.status_code == 200:
        data = response.json()
        return {
            "Bitcoin": data["bitcoin"]["usd"],
            "Ethereum": data["ethereum"]["usd"],
            "Litecoin": data["litecoin"]["usd"],
        }
    else:
        print("Error fetching cryptocurrency prices. Default prices will be used.")
        return {"Bitcoin": 50000, "Ethereum": 4000, "Litecoin": 300}
# Main Function
def main():
    username = input("Enter your username: ")
    password = input("Enter your password: ")
    user = User(username, password)
    account_number = input("Enter your account number: ")
    try:
        account_balance = float(input("Enter your account balance: "))
    except ValueError:
        print("Invalid input! Setting account balance to 0.")
        account_balance = 0
    bank_account = BankAccount(account_number, account_balance)
    user.add_bank_account(bank_account)
    crypto_prices = fetch_crypto_prices()
    for crypto_name, price in crypto_prices.items():
        crypto = CryptoCurrency(crypto_name, price)
        bank_account.add_crypto(crypto)
    while True:
        action = input("\nWhat would you like to do? (buy/sell/portfolio/transactions/exit): ").lower()
        if action == "buy":
            crypto_name = input("Enter cryptocurrency name: ")
            amount_usd = float(input("Enter amount in USD: "))
            bank_account.buy_crypto(crypto_name, amount_usd)
        elif action == "sell":
            crypto_name = input("Enter cryptocurrency name: ")
            amount_crypto = float(input("Enter amount in cryptocurrency: "))
            bank_account.sell_crypto(crypto_name, amount_crypto)
        elif action == "portfolio":
            bank_account.show_portfolio()
        elif action == "transactions":
            bank_account.show_transaction_history()
        elif action == "exit":
            print("Exiting program.")
            break
        else:
            print("Invalid action. Try again.")
# Run the program
if __name__ == "__main__":
    main()