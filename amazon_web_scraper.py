import tkinter as tk
from tkinter import messagebox
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from twilio.rest import Client

TWILIO_ACCOUNT_SID = 'YOUR_TWILIO_ACCOUNT_SID'
TWILIO_AUTH_TOKEN = 'YOUR_TWILIO_AUTH_TOKEN'
TWILIO_PHONE_NUMBER = 'YOUR_TWILIO_PHONE_NUMBER'


class PriceDropApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Price Drop Tracker")
        self.root.geometry("500x400")
        self.root.configure(bg="#333")
        self.interval = 60000

        self.label_font = ("Helvetica", 12, "bold")
        self.entry_font = ("Helvetica", 10)
        self.btn_font = ("Helvetica", 10, "bold")

        self.main_frame = tk.Frame(self.root, bg="#333")
        self.main_frame.pack(pady=20)

        self.create_widgets()

    def create_widgets(self):
        header_label = tk.Label(self.main_frame, text="Track Price Drops", font=("Helvetica", 16, "bold"), fg="#f4f4f9", bg="#333")
        header_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        tk.Label(self.main_frame, text="Product URL:", font=self.label_font, fg="#f4f4f9", bg="#333").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.product_url_entry = tk.Entry(self.main_frame, font=self.entry_font, width=40)
        self.product_url_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(self.main_frame, text="Desired Price ($):", font=self.label_font, fg="#f4f4f9", bg="#333").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.desired_price_entry = tk.Entry(self.main_frame, font=self.entry_font, width=20)
        self.desired_price_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(self.main_frame, text="Mobile Number:", font=self.label_font, fg="#f4f4f9", bg="#333").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.mobile_number_entry = tk.Entry(self.main_frame, font=self.entry_font, width=20)
        self.mobile_number_entry.grid(row=3, column=1, padx=5, pady=5)

        self.start_button = tk.Button(self.main_frame, text="Start Tracking", font=self.btn_font, fg="#ffffff", bg="#4CAF50", activebackground="#45a049", command=self.start_tracking)
        self.start_button.grid(row=4, column=0, columnspan=2, pady=20)

    def start_tracking(self):
        self.product_url = self.product_url_entry.get()
        self.desired_price = float(self.desired_price_entry.get())
        self.mobile_number = self.mobile_number_entry.get()

        if not self.product_url or not self.desired_price or not self.mobile_number:
            messagebox.showwarning("Input Error", "Please fill out all fields.")
            return

        messagebox.showinfo("Tracking Started", "Price tracking started. You’ll get notified if price drops.")
        self.check_price_loop()

    def check_price_loop(self):
        current_price = asyncio.run(self.get_price(self.product_url))
        if current_price and current_price <= self.desired_price:
            self.send_sms_notification(self.mobile_number, self.product_url, current_price)
        else:
            print(f"Checked price: ${current_price}. No notification.")

        self.root.after(self.interval, self.check_price_loop)

    async def get_price(self, product_url):
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36",
                    "Accept-Language": "en-US,en;q=0.9",
                }
                async with session.get(product_url, headers=headers) as response:
                    soup = BeautifulSoup(await response.text(), "html.parser")
                    price_tag = soup.find("span", {"id": "priceblock_ourprice"})
                    if price_tag:
                        return float(price_tag.get_text().replace("$", "").replace(",", ""))
                    return None
        except Exception as e:
            print(f"Error: {e}")
            return None

    def send_sms_notification(self, mobile_number, product_url, price):
        try:
            client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            message = client.messages.create(
                body=f"Price Alert! Product dropped to ${price}. Check it here: {product_url}",
                from_=TWILIO_PHONE_NUMBER,
                to=mobile_number
            )
            messagebox.showinfo("notification Sent", "price drop SMS sent.")
        except Exception as e:
            print(f"SMS failed: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = PriceDropApp(root)
    root.mainloop()
