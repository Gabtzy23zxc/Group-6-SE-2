import os
import json
import datetime
import threading
import customtkinter as ctk  # type: ignore
import numpy as np
import torch
import onnxruntime as ort  # type: ignore
from tkinter import filedialog
from PIL import Image, ImageTk
from transformers import AutoImageProcessor
from history import HistoryPage


# ==============================
# THEME SETUP
# ==============================
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class MainPage(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("AI-nspect")
        self.geometry("600x400")
        self.resizable(True, True)

        # --- Background container ---
        self.bg_frame = ctk.CTkFrame(self, corner_radius=20)
        self.bg_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.9, relheight=0.9)
        self.bg_frame.configure(fg_color="#8EA8FF")  # light blue background

        # Frames for main and history
        self.main_frame = ctk.CTkFrame(self.bg_frame, fg_color="transparent")
        self.history_page = HistoryPage(self.bg_frame, self.show_main)

        for frame in (self.main_frame, self.history_page):
            frame.place(relwidth=1, relheight=1)

        # --- Header ---
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

        # Dropdown (Model version)
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

        # --- Select Image Button ---
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
    # IMAGE SELECTION + LOADING
    # =============================
    def select_image(self):
        file_path = filedialog.askopenfilename(
            title="Select an Image",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;")]
        )
        if not file_path:
            return

        # 🩵 Fade-in loading overlay
        overlay = ctk.CTkFrame(self.bg_frame, fg_color=("gray10", "gray10"), corner_radius=0)
        overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        box = ctk.CTkFrame(overlay, fg_color="white", corner_radius=20)
        box.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.4, relheight=0.3)

        title = ctk.CTkLabel(
            box,
            text="🔍 Processing image...",
            text_color="black",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title.pack(pady=(30, 10))

        progress = ctk.CTkProgressBar(box, mode="indeterminate", width=200)
        progress.pack(pady=(0, 20))
        progress.start()

        self.update_idletasks()

        # ✨ Fade-in effect for overlay
        def fade_in_overlay(alpha=0.0):
            if alpha < 0.8:
                overlay.configure(fg_color=(f"gray{int(10 + alpha * 100)}", f"gray{int(10 + alpha * 100)}"))
                self.after(30, lambda: fade_in_overlay(alpha + 0.05))

        fade_in_overlay()

        # --- Threaded Processing ---
        def process_image():
            try:
                file_name = os.path.basename(file_path)
                current_time = datetime.datetime.now().strftime("%B %d, %Y %I:%M %p")

                so = ort.SessionOptions()
                so.intra_op_num_threads = 4
                so.inter_op_num_threads = 1
                so.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
                so.execution_mode = ort.ExecutionMode.ORT_PARALLEL

                session = ort.InferenceSession("ai_detector_v2_optimized.onnx", so, providers=["CPUExecutionProvider"])
                processor = AutoImageProcessor.from_pretrained("google/vit-base-patch16-224")

                img = Image.open(file_path).convert("RGB")
                inputs = processor(img, return_tensors="np")

                outputs = session.run(None, {"pixel_values": inputs["pixel_values"]})
                logits = torch.tensor(outputs[0])
                probs = torch.nn.functional.softmax(logits, dim=-1)
                labels = ["real", "fake"]
                label_id = torch.argmax(probs).item()

                confidence = float(probs[0][label_id] * 100)
                confidence_str = f"{confidence:.2f}%"
                authenticity = labels[label_id].capitalize()

                # --- Save to history ---
                history = []
                if os.path.exists("history.json"):
                    with open("history.json", "r") as f:
                        try:
                            history = json.load(f)
                        except json.JSONDecodeError:
                            history = []

                history.append({
                    "File Name": file_name,
                    "Date": current_time,
                    "Authenticity": authenticity,
                    "Confidence": confidence_str
                })

                with open("history.json", "w") as f:
                    json.dump(history, f, indent=4)

            except Exception as e:
                authenticity = "Error"
                confidence_str = str(e)
                print("❌ Error processing image:", e)

            finally:
                # Fade-out overlay before showing results
                def fade_out_overlay(alpha=0.8):
                    if alpha > 0:
                        overlay.configure(fg_color=(f"gray{int(10 + alpha * 100)}", f"gray{int(10 + alpha * 100)}"))
                        self.after(30, lambda: fade_out_overlay(alpha - 0.05))
                    else:
                        overlay.destroy()
                        self.display_result(file_path, authenticity, confidence_str)

                self.after(0, lambda: fade_out_overlay(0.8))

        threading.Thread(target=process_image, daemon=True).start()

    # =============================
    # RESULT DISPLAY FUNCTION
    # =============================
    def display_result(self, file_path, authenticity, confidence_str):
        result_frame = ctk.CTkFrame(self.bg_frame, corner_radius=20)
        result_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.6, relheight=0.5)
        result_frame.attributes = {"alpha": 0.0}

        # Divide layout: left=image, right=text
        left = ctk.CTkFrame(result_frame, fg_color="white", corner_radius=15)
        left.place(relx=0.02, rely=0.5, anchor="w", relwidth=0.45, relheight=0.9)

        right = ctk.CTkFrame(result_frame, fg_color="white", corner_radius=15)
        right.place(relx=0.55, rely=0.5, anchor="w", relwidth=0.43, relheight=0.9)

        # 🖼️ Image preview
        try:
            preview = Image.open(file_path)
            preview.thumbnail((200, 200))
            preview_tk = ImageTk.PhotoImage(preview)
            image_label = ctk.CTkLabel(left, image=preview_tk, text="")
            image_label.image = preview_tk
            image_label.pack(expand=True)
        except Exception as e:
            ctk.CTkLabel(left, text=f"Error loading image:\n{e}", text_color="red").pack(pady=10)

        # 🧠 AI result
        color = "#00C853" if authenticity.lower() == "real" else "#FF5252"

        result_label = ctk.CTkLabel(
            right,
            text=f"Authenticity: {authenticity}",
            text_color=color,
            font=ctk.CTkFont(size=20, weight="bold")
        )
        result_label.pack(pady=(40, 10))

        confidence_label = ctk.CTkLabel(
            right,
            text=f"Confidence: {confidence_str}",
            text_color="black",
            font=ctk.CTkFont(size=16)
        )
        confidence_label.pack(pady=(0, 20))

        close_btn = ctk.CTkButton(
            right,
            text="Close",
            fg_color="#E53935",
            hover_color="#D32F2F",
            text_color="white",
            width=100,
            command=lambda: result_frame.destroy()
        )
        close_btn.pack(pady=(20, 10))

        result_frame.lift()

        # ✨ Fade-in animation for result card
        def fade_in(alpha=0.0):
            if alpha < 1.0:
                try:
                    result_frame.tk.call("tk", "scaling")
                    result_frame.update_idletasks()
                except:
                    pass
                result_frame.place(relx=0.5, rely=0.5, anchor="center")
                result_frame.attributes["alpha"] = alpha
                result_frame.configure(fg_color=(f"gray{int(90 - alpha * 80)}", f"gray{int(90 - alpha * 80)}"))
                self.after(20, lambda: fade_in(alpha + 0.05))
            else:
                result_frame.attributes["alpha"] = 1.0

        fade_in()


# ==============================
# RUN APP
# ==============================
if __name__ == "__main__":
    app = MainPage()
    app.mainloop()
