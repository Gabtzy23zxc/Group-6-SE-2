import json
import customtkinter as ctk  # type: ignore
from tkinter import ttk

class HistoryPage(ctk.CTkFrame):
    def __init__(self, parent, go_back_callback):
        super().__init__(parent, fg_color="transparent")

        self.go_back_callback = go_back_callback

        # Background gradient frame
        self.bg_frame = ctk.CTkFrame(self, corner_radius=20)
        self.bg_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.9, relheight=0.9)
        self.bg_frame.configure(fg_color=("lightblue", "#7FA6F3"))  # soft blue tone

        # --- HEADER AREA ---
        header = ctk.CTkFrame(self.bg_frame, fg_color="white", height=60, corner_radius=20)
        header.pack(fill="x", pady=(10, 5), padx=10)

        title = ctk.CTkLabel(
            header,
            text="View History",
            text_color="black",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        title.place(relx=0.5, rely=0.5, anchor="center")

        back_btn = ctk.CTkButton(
            header,
            text="←",
            width=40,
            height=30,
            fg_color="transparent",
            hover_color="#E5E5E5",
            text_color="black",
            font=ctk.CTkFont(size=18, weight="bold"),
            command=self.go_back_callback
        )
        back_btn.place(x=10, rely=0.5, anchor="w")

        # --- TABLE AREA ---
        table_frame = ctk.CTkFrame(self.bg_frame, fg_color="white", corner_radius=15)
        table_frame.pack(fill="both", expand=True, padx=20, pady=(5, 20))

        columns = ("File Name", "Date","Authenticity","Confidence",)
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
        self.tree.heading("File Name", text="File Name")
        self.tree.heading("Date", text="Date")
        self.tree.heading("Authenticity", text="Authenticity")
        self.tree.heading("Confidence", text="Confidence")
        # Column widths
        self.tree.column("File Name", width=125, anchor="center")
        self.tree.column("Date", width=125, anchor="center")
        self.tree.column("Authenticity", width=125, anchor="center")
        self.tree.column("Confidence", width=125, anchor="center")
        # Style the table
        style = ttk.Style()
        style.configure(
            "Treeview",
            font=("Arial", 12),
            rowheight=28,
            background="white",
            fieldbackground="white"
        )
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"), background="white")
        style.map("Treeview", background=[("selected", "#D1E2FF")])

        # Add red line (separator under header)
        red_line = ctk.CTkFrame(table_frame, height=2, fg_color="red")
        red_line.pack(fill="x", pady=(5, 0))

        # Place the table
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

    # --- Function to load data from JSON ---
    def load_history_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            with open("history.json", "r") as f:
                data = json.load(f)
            for item in data:
                self.tree.insert("", "end", values=(item["File Name"], item["Date"], item["Authenticity"],item["Confidence"]))
        except Exception as e:
            print("Error loading history:", e)
