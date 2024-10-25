import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from customtkinter import CTk, CTkEntry, CTkLabel, CTkTextbox, CTkButton
from scraper import Scraper

import threading


class CraigslistScraperGUI:
    def __init__(self):
        self.root = CTk()
        self.root.title("Craigslist Phone Numbers Extractor")
        self.root.geometry("600x800")

        font_style = ("Arial", 20)

        CTkLabel(self.root, text="City:", font=font_style).pack(pady=10)
        self.city_entry = CTkEntry(self.root, font=font_style, width=400, height=40)
        self.city_entry.pack(pady=10)

        CTkLabel(self.root, text="State:", font=font_style).pack(pady=10)
        self.state_entry = CTkEntry(self.root, font=font_style, width=400, height=40)
        self.state_entry.pack(pady=10)

        CTkLabel(self.root, text="Radius (Mile):", font=font_style).pack(pady=10)
        self.distance_entry = CTkEntry(self.root, font=font_style, width=400, height=40)
        self.distance_entry.pack(pady=10)

        self.scrape_button = CTkButton(self.root, text="Scrape", font=font_style, width=200, height=50,
                                       command=self.submit_data)
        self.scrape_button.pack(pady=20)

        self.state_label = tk.Label(self.root, font=font_style, fg="white", bg=self.root.cget("bg"),bd=0)  # Set bg to match root bg and remove border
        self.state_label.pack(pady=5)  # Place the label just below the progress bar

        self.progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(self.root, variable=self.progress_var, maximum=100)
        progress_bar.pack(pady=20, fill=tk.X, padx=20)

        self.progress_label = tk.Label(self.root, text="0%", font=font_style,fg="white", bg=self.root.cget("bg"), bd=0)
        self.progress_label.pack(pady=5)

        self.output_text = CTkTextbox(self.root, width=560, height=300, font=font_style)
        self.output_text.pack(pady=20)
        self.output_text.configure(state="disabled")
        self.scraper = Scraper(self.update_progress,self.update_state,self.log_message)  # Pass the update function to Scraper
    def submit_data(self):
        self.progress_label.configure(text="0%")
        self.progress_var.set(0)
        self.root.update_idletasks()
        self.output_text.configure(state="normal")
        self.output_text.delete(1.0, "end")
        self.output_text.configure(state="disabled")
        city = self.city_entry.get().lower()
        state = self.state_entry.get().lower()
        distance = self.distance_entry.get()

        if city and state and distance:
            try:
                distance = float(distance)
                threading.Thread(target=self.scraper.run_scraping, args=(city, state, distance), daemon=True).start()
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid number for radius.")
                self.scrape_button.configure(state=tk.NORMAL)
        else:
            messagebox.showerror("Error", "All fields must be filled out.")
            return

        self.scrape_button.pack_forget()



    def update_progress(self, value):
        self.progress_var.set(value)
        self.progress_label.configure(text=f"{int(value)}%")
        self.root.update_idletasks()

    def update_state(self, message):
        self.state_label.configure(text=message)  # Update the state label
        self.root.update_idletasks()

    def update_output(self, message):
        self.output_text.configure(state="normal")
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.configure(state="disabled")
        self.output_text.see(tk.END)  # Scroll to the end

    def log_message(self, message):
        self.output_text.configure(state=tk.NORMAL)  # Enable editing of the text widget
        self.output_text.insert(tk.END, f"{message}\n \n")
        self.output_text.configure(state=tk.DISABLED)  # Disable editing
        self.output_text.yview(tk.END)  # Scroll to the end

    def run(self):
        self.root.mainloop()

