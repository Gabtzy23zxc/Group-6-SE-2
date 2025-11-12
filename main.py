import os
import json
import datetime
import customtkinter as ctk   # type: ignore
from tkinter import filedialog
from history import HistoryPage

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class MainPage(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("AI-nspect")
        self.geometry("600x400")
        self.resizable(True,True)

        # --- Gradient background container ---
        self.bg_frame = ctk.CTkFrame(self, corner_radius=20)
        self.bg_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.9, relheight=0.9)
        self.bg_frame.configure(fg_color="#8EA8FF")  # light blue tone background

        # Create frames for main and history
        self.main_frame = ctk.CTkFrame(self.bg_frame, fg_color="transparent")
        self.history_page = HistoryPage(self.bg_frame, self.show_main)

        for frame in (self.main_frame, self.history_page):
            frame.place(relwidth=1, relheight=1)

        # --- HEADER SECTION ---
        header = ctk.CTkFrame(self.main_frame, fg_color="transparent", height=60, corner_radius=20)
        header.pack(fill="x", pady=(10, 20), padx=10)

        # “View History” button
        view_history_btn = ctk.CTkButton(
            header,
            text="View History",
            fg_color="white",
            hover_color="#E5E5E5",
            text_color="black",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=100,
            command=self.show_history
        )
        view_history_btn.place(x=10, rely=0.5, anchor="w")

        # Dropdown placeholder (Model version)
        self.model_var = ctk.StringVar(value="Model ver. 1.0")
        model_dropdown = ctk.CTkOptionMenu(
            header,
            variable=self.model_var,
            values=["Model ver. 1.0", "Add New Model +"],
            fg_color="white",
            text_color="black",
            button_color="#E5E5E5",
            dropdown_fg_color="white",
            dropdown_text_color="black",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        model_dropdown.place(relx=0.95, rely=0.5, anchor="e")

        # --- SELECT IMAGE BUTTON ---
        select_image_btn = ctk.CTkButton(
            self.main_frame,
            text="Select Image",
            width=180,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            corner_radius=15,
            command=self.select_image
        )
        select_image_btn.place(relx=0.5, rely=0.6, anchor="center")

        self.show_main()

    # =============================
    # PAGE SWITCHING
    # =============================
    def show_main(self):
        self.main_frame.tkraise()

    def show_history(self):
        self.history_page.load_history_data()
        self.history_page.tkraise()

    # =============================
    # SELECT IMAGE & SAVE HISTORY
    # =============================
    def select_image(self):
        file_path = filedialog.askopenfilename(
            title="Select an Image",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;")]
        )
        if file_path:
            file_name = os.path.basename(file_path)
            current_time = datetime.datetime.now().strftime("%B %d, %Y %I:%M %p")

            # Load or initialize history
            history = []
            if os.path.exists("history.json"):
                with open("history.json", "r") as f:
                    try:
                        history = json.load(f)
                    except json.JSONDecodeError:
                        history = []

            # Add new record
            history.append({"File Name": file_name, "Date": current_time})

            # Save back
            with open("history.json", "w") as f:
                json.dump(history, f, indent=4)

            print(f"✅ Added {file_name} at {current_time} to history.")


if __name__ == "__main__":
    app = MainPage()
    app.mainloop()
