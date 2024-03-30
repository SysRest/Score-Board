import tkinter as tk
from tkinter import messagebox, simpledialog
import time
import pickle
import os
import pystray

class ScoreboardApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("计分板")
        
        self.scores = [0, 0, 0, 0]  # scores for four groups
        
        self.load_history()
        
        self.create_widgets()
        self.check_autorun()
        
    def create_widgets(self):
        self.label_scores = []
        for i in range(4):
            label = tk.Label(self.root, text=f"{i+1}组: {self.scores[i]}", font=("Helvetica", 16))
            label.grid(row=i, column=0, padx=5, pady=5, sticky="w")
            self.label_scores.append(label)
        
        button_frame = tk.Frame(self.root)
        button_frame.grid(row=0, column=1, rowspan=4, padx=5, pady=5)
        
        buttons = [
            ("+1", 1), ("-1", -1),
            ("+2", 2), ("-2", -2),
            ("+5", 5), ("-5", -5),
            ("+10", 10), ("-10", -10),
            ("+20", 20), ("-20", -20),
            ("+50", 50), ("-50", -50)
        ]
        
        current_row = 0
        for i, (text, value) in enumerate(buttons):
            btn = tk.Button(button_frame, text=text, command=lambda v=value: self.show_group_selection(v))
            if i % 2 == 0:
                btn.grid(row=current_row, column=0, padx=5, pady=5, sticky="ew")
            else:
                btn.grid(row=current_row, column=1, padx=5, pady=5, sticky="ew")
                current_row += 1
        
        # 添加自定义按钮
        custom_btn = tk.Button(button_frame, text="自定义", command=self.show_custom_input)
        custom_btn.grid(row=current_row, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        
        self.btn_history = tk.Button(self.root, text="查看历史记录", command=self.view_history)
        self.btn_history.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        
        self.btn_clear_history = tk.Button(self.root, text="清空历史记录", command=self.clear_history)
        self.btn_clear_history.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        
        self.btn_clear_scores = tk.Button(self.root, text="清空所有分数", command=self.clear_scores)
        self.btn_clear_scores.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        # 在底部居中显示“Made by 林铮”
        made_by_label = tk.Label(self.root, text="v1.0 | By 林铮 | ©版权所有")
        made_by_label.grid(row=7, columnspan=2, padx=5, pady=5, sticky="ew")
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        
    def show_group_selection(self, value):
        group_selection_window = tk.Toplevel(self.root)
        group_selection_window.title("")
        
        title_label = tk.Label(group_selection_window, text="选择操作组别", font=("Helvetica", 16))
        title_label.pack()
        
        width = 200
        height = 150
        x = self.root.winfo_x() + (self.root.winfo_width() - width) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - height) // 2
        group_selection_window.geometry(f"{width}x{height}+{x}+{y}")
        
        for i in range(4):
            btn = tk.Button(group_selection_window, text=f"{i+1}组", command=lambda g=i: self.modify_score(g, value, group_selection_window))
            btn.pack()
        
    def show_custom_input(self):
        custom_input_window = tk.Toplevel(self.root)
        custom_input_window.title("自定义加减分数")
        
        width = 220
        height = 200
        x = self.root.winfo_x() + (self.root.winfo_width() - width) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - height) // 2
        custom_input_window.geometry(f"{width}x{height}+{x}+{y}")
        
        label = tk.Label(custom_input_window, text="请选择操作组别:")
        label.pack()
        
        self.group_var = tk.IntVar()
        self.group_var.set(0)
        for i in range(4):
            radio_btn = tk.Radiobutton(custom_input_window, text=f"{i+1}组", variable=self.group_var, value=i)
            radio_btn.pack()
        
        label = tk.Label(custom_input_window, text="请输入要加减的分数:")
        label.pack()
        
        self.value_entry = tk.Entry(custom_input_window)
        self.value_entry.pack()
        
        submit_btn = tk.Button(custom_input_window, text="确认", command=lambda: self.modify_custom_score(custom_input_window))
        submit_btn.pack()
        
    def modify_custom_score(self, window):
        try:
            value = int(self.value_entry.get())
            group = self.group_var.get()
            self.modify_score(group, value, window)
        except ValueError:
            messagebox.showerror("错误", "请输入有效的整数")
        
    def modify_score(self, group, value, window):
        if window:
            window.destroy()
        self.scores[group] += value
        self.update_scores()
        self.save_history(f"{group+1}组得到 {value:+}", time.time())
        
    def update_scores(self):
        for i, label in enumerate(self.label_scores):
            label.config(text=f"{i+1}组: {self.scores[i]}")
        
    def view_history(self):
        history_window = tk.Toplevel(self.root)
        history_window.title("历史记录")
        
        history_listbox = tk.Listbox(history_window, width=50)
        history_listbox.pack(fill=tk.BOTH, expand=1)
        
        scrollbar = tk.Scrollbar(history_window, orient=tk.VERTICAL, command=history_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        history_listbox.config(yscrollcommand=scrollbar.set)
        
        for entry in reversed(self.history):
            history_listbox.insert(0, entry)
            
    def clear_history(self):
        self.history = []
        with open("history.pkl", "wb") as f:
            pickle.dump(self.history, f)
        
    def load_history(self):
        if os.path.exists("history.pkl"):
            with open("history.pkl", "rb") as f:
                self.history = pickle.load(f)
        else:
            self.history = []
            
    def save_history(self, entry, timestamp):
        self.history.insert(0, f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))}: {entry}")
        with open("history.pkl", "wb") as f:
            pickle.dump(self.history, f)
            
    def clear_scores(self):
        self.scores = [0, 0, 0, 0]
        self.update_scores()
        
    def check_autorun(self):
        if not os.path.exists("autorun.txt"):
            self.create_autorun()
        
    def create_autorun(self):
        with open("autorun.txt", "w") as f:
            f.write("This file ensures the program runs on startup.")
        
    def on_close(self):
        self.root.destroy()

if __name__ == "__main__":
    app = ScoreboardApp()
    app.root.mainloop()
