from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import os
import threading

# متغیر برای کنترل وضعیت کنسل شدن پردازش
cancel_processing = False

# تابع برای اضافه کردن لوگو به تصاویر
def add_logo(main_image_paths, logo_image_path, position, logo_scale, output_dir):
    global cancel_processing
    margin = 10  # فاصله از گوشه‌ها
    total_files = len(main_image_paths)
    processed_files = 0
    output_files = []  # لیستی از فایل‌های خروجی ایجاد شده
    
    # به‌روزرسانی نوار پیشرفت
    progress_bar['maximum'] = total_files
    
    for main_image_path in main_image_paths:
        if cancel_processing:
            break
        
        main_image = Image.open(main_image_path)
        logo_image = Image.open(logo_image_path)

        # تنظیم اندازه لوگو با حفظ نسبت تصویر برای هر تصویر
        logo_width = int(main_image.width * logo_scale)
        logo_height = int(logo_width * logo_image.height / logo_image.width)
        resized_logo = logo_image.resize((logo_width, logo_height), Image.ANTIALIAS)

        # موقعیت لوگو بر اساس انتخاب کاربر با در نظر گرفتن فاصله از گوشه‌ها
        if position == "بالا-چپ":
            logo_position = (margin, margin)
        elif position == "بالا-راست":
            logo_position = (main_image.width - resized_logo.width - margin, margin)
        elif position == "پایین-چپ":
            logo_position = (margin, main_image.height - resized_logo.height - margin)
        elif position == "پایین-راست":
            logo_position = (main_image.width - resized_logo.width - margin, main_image.height - resized_logo.height - margin)

        # اضافه کردن لوگو به تصویر اصلی
        main_image.paste(resized_logo, logo_position, resized_logo)

        # ذخیره تصویر جدید
        output_path = os.path.join(output_dir, os.path.basename(main_image_path))
        main_image.save(output_path)
        output_files.append(output_path)  # ذخیره مسیر فایل خروجی در لیست

        # به‌روزرسانی تعداد فایل‌های پردازش شده و نوار پیشرفت
        processed_files += 1
        progress_bar['value'] = processed_files
        progress_label.config(text=f"فایل‌های آماده شده: {processed_files}/{total_files}")
        root.update_idletasks()  # به‌روزرسانی رابط کاربری

    if cancel_processing:
        ask_delete_files(output_files)
    else:
        messagebox.showinfo("اتمام", "تمامی تصاویر با موفقیت ذخیره شدند!")

# تابع برای پرسش درباره حذف فایل‌های ایجاد شده
def ask_delete_files(output_files):
    response = messagebox.askyesno("کنسل شد", "آیا می‌خواهید فایل‌های خروجی ایجاد شده را حذف کنید؟")
    if response:
        for file_path in output_files:
            try:
                os.remove(file_path)
            except OSError:
                pass
        messagebox.showinfo("حذف شد", "فایل‌های خروجی با موفقیت حذف شدند!")
    else:
        messagebox.showinfo("نگهداری شد", "فایل‌های خروجی در پوشه باقی ماندند.")

# تابع برای اجرای اضافه کردن لوگو در یک ترد جداگانه
def start_processing():
    global cancel_processing
    cancel_processing = False
    
    main_image_paths = filedialog.askopenfilenames(title="انتخاب تصاویر اصلی", filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
    logo_image_path = filedialog.askopenfilename(title="انتخاب لوگو", filetypes=[("PNG files", "*.png")])
    
    if main_image_paths and logo_image_path:
        output_dir = filedialog.askdirectory(title="انتخاب پوشه ذخیره‌سازی")
        if not output_dir:
            messagebox.showerror("خطا", "پوشه ذخیره‌سازی انتخاب نشده است!")
            return
        
        position = position_var.get()
        logo_scale = scale_var.get() / 100
        
        # ایجاد و اجرای ترد برای پردازش تصاویر
        processing_thread = threading.Thread(target=add_logo, args=(main_image_paths, logo_image_path, position, logo_scale, output_dir))
        processing_thread.start()

# تابع برای کنسل کردن پردازش
def cancel_processing_action():
    global cancel_processing
    cancel_processing = True

# ایجاد پنجره اصلی
root = tk.Tk()
root.title("اضافه کردن لوگو به تصاویر")

# فریم اصلی
main_frame = ttk.Frame(root, padding="10")
main_frame.pack(fill="both", expand=True)

# گزینه‌های موقعیت لوگو
position_var = tk.StringVar(value="پایین-راست")
positions = ["بالا-چپ", "بالا-راست", "پایین-چپ", "پایین-راست"]

position_label = ttk.Label(main_frame, text="انتخاب موقعیت لوگو:")
position_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

for idx, position in enumerate(positions):
    rb = ttk.Radiobutton(main_frame, text=position, variable=position_var, value=position)
    rb.grid(row=0, column=idx+1, padx=5, pady=5, sticky="w")

# اسلایدر تنظیم سایز لوگو
scale_var = tk.IntVar(value=20)
scale_label = ttk.Label(main_frame, text="اندازه لوگو (% از تصویر اصلی):")
scale_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")

scale_slider = ttk.Scale(main_frame, from_=5, to_=50, orient="horizontal", variable=scale_var)
scale_slider.grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky="ew")

# برچسب برای نمایش مقدار اسلایدر
scale_value_label = ttk.Label(main_frame, text=f"{scale_var.get()}%")
scale_value_label.grid(row=1, column=4, padx=5, pady=5, sticky="w")

# به‌روزرسانی مقدار اسلایدر به‌صورت زنده
def update_scale_value(event):
    scale_value_label.config(text=f"{scale_var.get()}%")

scale_slider.bind("<Motion>", update_scale_value)

# نوار پیشرفت
progress_bar = ttk.Progressbar(main_frame, orient="horizontal", mode="determinate")
progress_bar.grid(row=2, column=0, columnspan=3, padx=5, pady=10, sticky="ew")

# برچسب نوار پیشرفت
progress_label = ttk.Label(main_frame, text="فایل‌های آماده شده: 0/0")
progress_label.grid(row=2, column=4, padx=5, pady=10, sticky="w")

# دکمه انتخاب فایل‌ها
select_button = ttk.Button(main_frame, text="انتخاب تصاویر و اضافه کردن لوگو", command=start_processing)
select_button.grid(row=3, column=0, columnspan=4, padx=5, pady=20, sticky="ew")

# دکمه کنسل کردن پردازش
cancel_button = ttk.Button(main_frame, text="کنسل کردن", command=cancel_processing_action)
cancel_button.grid(row=3, column=4, padx=5, pady=20, sticky="ew")

# استایل دهی به رابط کاربری
style = ttk.Style()
style.configure("TFrame", background="#f0f0f0")
style.configure("TButton", padding=6, relief="flat", background="#d9d9d9")
style.configure("TRadiobutton", background="#f0f0f0")
style.configure("TLabel", background="#f0f0f0")
style.configure("TProgressbar", thickness=15)

# شروع رابط کاربری
root.mainloop()
