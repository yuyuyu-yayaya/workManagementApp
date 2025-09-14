import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

class StartTimeDialog(tk.Toplevel):
    """
    開始時刻を確認・編集するためのダイアログ（画面4）。
    """
    def __init__(self, parent, task_name: str):
        super().__init__(parent)
        self.transient(parent) # 親ウィンドウの上に表示
        self.grab_set() # モーダルにする

        self.title("作業開始")
        self.geometry("350x150")

        self.start_time: Optional[datetime] = None
        self.task_name = task_name

        self._create_widgets()
        self._center_window()

        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.wait_window(self) # ダイアログが閉じるまで待つ

    def _center_window(self):
        """ダイアログを親ウィンドウの中央に表示する。"""
        self.update_idletasks() # ウィンドウのサイズが確定するのを待つ
        parent_x = self.master.winfo_x()
        parent_y = self.master.winfo_y()
        parent_width = self.master.winfo_width()
        parent_height = self.master.winfo_height()
        self.geometry(f"+{parent_x + (parent_width // 2) - (self.winfo_width() // 2)}+{parent_y + (parent_height // 2) - (self.winfo_height() // 2)}")

    def _create_widgets(self):
        main_frame = ttk.Frame(self, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # ラベル
        task_label = ttk.Label(main_frame, text=f"工数: {self.task_name}", font=("", 12, "bold"))
        task_label.pack(pady=(0, 10))

        time_label = ttk.Label(main_frame, text="開始時刻:")
        time_label.pack(side=tk.LEFT, padx=(0, 5))

        # 時刻入力フィールド
        now = datetime.now()
        self.hour_var = tk.StringVar(value=f"{now.hour:02}")
        self.minute_var = tk.StringVar(value=f"{now.minute:02}")

        hour_spinbox = ttk.Spinbox(main_frame, from_=0, to=23, textvariable=self.hour_var, width=4, format="%02.0f")
        hour_spinbox.pack(side=tk.LEFT)
        separator = ttk.Label(main_frame, text=":")
        separator.pack(side=tk.LEFT, padx=2)
        minute_spinbox = ttk.Spinbox(main_frame, from_=0, to=59, textvariable=self.minute_var, width=4, format="%02.0f")
        minute_spinbox.pack(side=tk.LEFT)

        # ボタン
        button_frame = ttk.Frame(self, padding=(0, 10, 0, 10))
        button_frame.pack(fill=tk.X)
        
        ok_button = ttk.Button(button_frame, text="Start", command=self._on_ok)
        ok_button.pack(side=tk.RIGHT)
        cancel_button = ttk.Button(button_frame, text="キャンセル", command=self._on_cancel)
        cancel_button.pack(side=tk.RIGHT, padx=(0, 10))

    def _on_ok(self):
        now = datetime.now()
        self.start_time = now.replace(hour=int(self.hour_var.get()), minute=int(self.minute_var.get()), second=0, microsecond=0)
        self.destroy()

    def _on_cancel(self):
        self.start_time = None
        self.destroy()

class EndTimeDialog(tk.Toplevel):
    """
    終了時刻を確認・編集するためのダイアログ（画面5）。
    """
    def __init__(self, parent, task_name: str):
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()

        self.title("作業終了")
        self.geometry("350x150")

        self.end_time: Optional[datetime] = None
        self.task_name = task_name

        self._create_widgets()
        self._center_window()

        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.wait_window(self)

    def _center_window(self):
        """ダイアログを親ウィンドウの中央に表示する。"""
        self.update_idletasks() # ウィンドウのサイズが確定するのを待つ
        parent_x = self.master.winfo_x()
        parent_y = self.master.winfo_y()
        parent_width = self.master.winfo_width()
        parent_height = self.master.winfo_height()
        self.geometry(f"+{parent_x + (parent_width // 2) - (self.winfo_width() // 2)}+{parent_y + (parent_height // 2) - (self.winfo_height() // 2)}")

    def _create_widgets(self):
        main_frame = ttk.Frame(self, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        task_label = ttk.Label(main_frame, text=f"工数: {self.task_name}", font=("", 12, "bold"))
        task_label.pack(pady=(0, 10))

        time_label = ttk.Label(main_frame, text="終了時刻:")
        time_label.pack(side=tk.LEFT, padx=(0, 5))

        now = datetime.now()
        self.hour_var = tk.StringVar(value=f"{now.hour:02}")
        self.minute_var = tk.StringVar(value=f"{now.minute:02}")

        hour_spinbox = ttk.Spinbox(main_frame, from_=0, to=23, textvariable=self.hour_var, width=4, format="%02.0f")
        hour_spinbox.pack(side=tk.LEFT)
        separator = ttk.Label(main_frame, text=":")
        separator.pack(side=tk.LEFT, padx=2)
        minute_spinbox = ttk.Spinbox(main_frame, from_=0, to=59, textvariable=self.minute_var, width=4, format="%02.0f")
        minute_spinbox.pack(side=tk.LEFT)

        button_frame = ttk.Frame(self, padding=(0, 10, 0, 10))
        button_frame.pack(fill=tk.X)
        
        ok_button = ttk.Button(button_frame, text="確定", command=self._on_ok)
        ok_button.pack(side=tk.RIGHT)
        cancel_button = ttk.Button(button_frame, text="キャンセル", command=self._on_cancel)
        cancel_button.pack(side=tk.RIGHT, padx=(0, 10))

    def _on_ok(self):
        now = datetime.now()
        self.end_time = now.replace(hour=int(self.hour_var.get()), minute=int(self.minute_var.get()), second=0, microsecond=0)
        self.destroy()

    def _on_cancel(self):
        self.end_time = None
        self.destroy()

class ResultDialog(tk.Toplevel):
    """
    一日の作業サマリーを表示するリザルト画面（画面7）。
    """
    def __init__(self, parent, summary_data: Dict[str, Any]):
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()

        self.title("本日の作業サマリー")
        self.geometry("450x400")

        self.summary_data = summary_data
        self._create_widgets()
        self._center_window()

        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.wait_window(self)

    def _center_window(self):
        """ダイアログを親ウィンドウの中央に表示する。"""
        self.update_idletasks() # ウィンドウのサイズが確定するのを待つ
        parent_x = self.master.winfo_x()
        parent_y = self.master.winfo_y()
        parent_width = self.master.winfo_width()
        parent_height = self.master.winfo_height()
        self.geometry(f"+{parent_x + (parent_width // 2) - (self.winfo_width() // 2)}+{parent_y + (parent_height // 2) - (self.winfo_height() // 2)}")

    def _create_widgets(self):
        main_frame = ttk.Frame(self, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- サマリー情報 ---
        total_work_time_str = self.summary_data.get('total_work_time', 'N/A')
        total_task_time_str = self.summary_data.get('total_task_time', 'N/A')
        other_time_str = self.summary_data.get('other_time', 'N/A')

        ttk.Label(main_frame, text=f"総労働時間: {total_work_time_str}", font=("", 11, "bold")).pack(anchor="w", pady=2)
        ttk.Label(main_frame, text=f"タスク合計時間: {total_task_time_str}", font=("", 11, "bold")).pack(anchor="w", pady=2)
        ttk.Label(main_frame, text=f"その他時間: {other_time_str}", font=("", 11, "bold")).pack(anchor="w", pady=2)

        ttk.Separator(main_frame, orient='horizontal').pack(fill='x', pady=10)

        # --- タスクごとの内訳 ---
        ttk.Label(main_frame, text="タスクごとの作業時間:", font=("", 10, "bold")).pack(anchor="w", pady=(5, 5))

        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        tree = ttk.Treeview(tree_frame, columns=("task_name", "duration"), show="headings")
        tree.heading("task_name", text="工数名")
        tree.heading("duration", text="作業時間")
        tree.column("duration", width=100, anchor=tk.E)
        tree.pack(fill=tk.BOTH, expand=True)

        for task in self.summary_data.get('task_details', []):
            tree.insert("", tk.END, values=(task['name'], task['duration_str']))

        # --- 閉じるボタン ---
        button_frame = ttk.Frame(self, padding=(0, 10, 0, 10))
        button_frame.pack(fill=tk.X)
        close_button = ttk.Button(button_frame, text="閉じる", command=self.destroy)
        close_button.pack(side=tk.RIGHT)