import requests
from bs4 import BeautifulSoup
import csv
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from io import BytesIO
from PIL import Image, ImageTk

# -------------------------------------------------
# SCRAPING FUNCTION
# -------------------------------------------------
def scrape_data(category):
    link = f'https://te.eg/wps/portal/te/Personal/Devices/{category}'
    page = requests.get(link)
    soup = BeautifulSoup(page.text, 'html.parser')

    devices_details = soup.find_all('div', {'class', 'compound-title'})
    we_list = []

    for device in devices_details:
        title = device.find('div', {'class', 'pro-card-head'})
        price = device.find('span', {'class', 'price'})
        company = device.find('span', {'class', 'manufactur'})

        we_list.append({
            'Title': title.text.strip() if title else '',
            'Company': company.text.strip() if company else '',
            'Price': price.text.strip() if price else ''
        })

    return we_list


# -------------------------------------------------
# BUTTON ACTIONS
# -------------------------------------------------
def start_scrape():
    category = category_var.get()
    if not category:
        messagebox.showwarning("Warning", "Please select a category first!")
        return

    tree.delete(*tree.get_children())
    data = scrape_data(category)

    if not data:
        messagebox.showinfo("Result", "No devices found for this category.")
        return

    for item in data:
        tree.insert("", tk.END, values=(item['Title'], item['Company'], item['Price']))

    messagebox.showinfo("Success", f"Fetched {len(data)} devices from WE.")
    global scraped_data
    scraped_data = data


def save_csv():
    if not scraped_data:
        messagebox.showwarning("Warning", "No data to save!")
        return

    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV Files", "*.csv")],
        title="Save file as"
    )

    if file_path:
        with open(file_path, 'w', encoding='utf-8', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=scraped_data[0].keys())
            writer.writeheader()
            writer.writerows(scraped_data)
        messagebox.showinfo("Saved", f"Data saved successfully:\n{file_path}")


# -------------------------------------------------
# GUI SETUP
# -------------------------------------------------
root = tk.Tk()
root.title("WE Devices Scraper")
root.geometry("850x550")
root.config(bg="#f5f5f5")

scraped_data = []
category_var = tk.StringVar()

# WE COLORS
main_color = "#6f2c91"  # purple (WE)
accent_color = "#9b59b6"
bg_color = "#f5f5f5"
text_color = "#333333"

# -------------------------------------------------
# LOAD LOGO (online or local)
# -------------------------------------------------
try:
    import requests
    response = requests.get("https://upload.wikimedia.org/wikipedia/en/thumb/2/23/Telecom_Egypt_logo.svg/512px-Telecom_Egypt_logo.svg.png")
    img_data = Image.open(BytesIO(response.content))
    img_data = img_data.resize((120, 120))
    logo = ImageTk.PhotoImage(img_data)
    logo_label = tk.Label(root, image=logo, bg=bg_color)
    logo_label.pack(pady=(15, 5))
except Exception:
    pass

# -------------------------------------------------
# TITLE
# -------------------------------------------------
title_label = tk.Label(root, text="WE Devices Scraper", font=("Arial", 18, "bold"),
                       fg=main_color, bg=bg_color)
title_label.pack(pady=(0, 10))

# -------------------------------------------------
# CATEGORY SELECTION
# -------------------------------------------------
categories = [
    "5G-Devices-Mobile",
    "Accessories",
    "4G-Routers",
    "Routers",
    "USB-Modems",
    "Mobile-Phones",
    "Fixed-Landline-Phones"
]

frame_top = tk.Frame(root, bg=bg_color)
frame_top.pack(pady=10)

category_label = tk.Label(frame_top, text="Select Category:", font=("Arial", 12),
                          bg=bg_color, fg=text_color)
category_label.grid(row=0, column=0, padx=10)

dropdown = ttk.Combobox(frame_top, textvariable=category_var, values=categories,
                        width=40, state="readonly", font=("Arial", 11))
dropdown.grid(row=0, column=1, padx=5)

# -------------------------------------------------
# BUTTONS
# -------------------------------------------------
btn_frame = tk.Frame(root, bg=bg_color)
btn_frame.pack(pady=10)

style = ttk.Style()
style.configure("TButton", font=("Arial", 11, "bold"), padding=6)

scrape_btn = tk.Button(btn_frame, text="Fetch Data", command=start_scrape,
                       bg=main_color, fg="white", activebackground=accent_color,
                       width=15, relief="flat", cursor="hand2")
scrape_btn.grid(row=0, column=0, padx=10)

save_btn = tk.Button(btn_frame, text="Save as CSV", command=save_csv,
                     bg="#27ae60", fg="white", activebackground="#2ecc71",
                     width=15, relief="flat", cursor="hand2")
save_btn.grid(row=0, column=1, padx=10)

# -------------------------------------------------
# RESULTS TABLE
# -------------------------------------------------
columns = ("Title", "Company", "Price")
tree = ttk.Treeview(root, columns=columns, show="headings", height=15)
tree.heading("Title", text="Device Name")
tree.heading("Company", text="Company")
tree.heading("Price", text="Price")
tree.column("Title", width=400)
tree.column("Company", width=200)
tree.column("Price", width=100)

style.configure("Treeview.Heading", font=("Arial", 11, "bold"), foreground=main_color)
style.configure("Treeview", font=("Arial", 10), rowheight=25)

tree.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

root.mainloop()
