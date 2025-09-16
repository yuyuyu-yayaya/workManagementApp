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

class EditTimeDialog(tk.Toplevel):
    """
    汎用的な時刻編集ダイアログ。
    """
    def __init__(self, parent, title: str, initial_time: datetime):
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()

        self.title(title)
        self.geometry("300x120")

        self.selected_time: Optional[datetime] = None
        self.initial_time = initial_time

        self._create_widgets()
        self._center_window()

        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.wait_window(self)

    def _center_window(self):
        """ダイアログを親ウィンドウの中央に表示する。"""
        self.update_idletasks()
        parent_x = self.master.winfo_x()
        parent_y = self.master.winfo_y()
        parent_width = self.master.winfo_width()
        parent_height = self.master.winfo_height()
        self.geometry(f"+{parent_x + (parent_width // 2) - (self.winfo_width() // 2)}+{parent_y + (parent_height // 2) - (self.winfo_height() // 2)}")

    def _create_widgets(self):
        main_frame = ttk.Frame(self, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        time_label = ttk.Label(main_frame, text="時刻:")
        time_label.pack(side=tk.LEFT, padx=(0, 5))

        self.hour_var = tk.StringVar(value=f"{self.initial_time.hour:02}")
        self.minute_var = tk.StringVar(value=f"{self.initial_time.minute:02}")

        hour_spinbox = ttk.Spinbox(main_frame, from_=0, to=23, textvariable=self.hour_var, width=4, format="%02.0f")
        hour_spinbox.pack(side=tk.LEFT)
        separator = ttk.Label(main_frame, text=":")
        separator.pack(side=tk.LEFT, padx=2)
        minute_spinbox = ttk.Spinbox(main_frame, from_=0, to=59, textvariable=self.minute_var, width=4, format="%02.0f")
        minute_spinbox.pack(side=tk.LEFT)

        button_frame = ttk.Frame(self, padding=(0, 10, 0, 10))
        button_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        ok_button = ttk.Button(button_frame, text="確定", command=self._on_ok)
        ok_button.pack(side=tk.RIGHT)
        cancel_button = ttk.Button(button_frame, text="キャンセル", command=self._on_cancel)
        cancel_button.pack(side=tk.RIGHT, padx=(0, 10))

    def _on_ok(self):
        self.selected_time = self.initial_time.replace(hour=int(self.hour_var.get()), minute=int(self.minute_var.get()), second=0, microsecond=0)
        self.destroy()

    def _on_cancel(self):
        self.selected_time = None
        self.destroy()

class SettingsDialog(tk.Toplevel):
    """
    設定を変更するためのダイアログ。
    """
    def __init__(self, parent, config_manager):
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()

        self.title("設定")
        self.geometry("300x150")

        self.config_manager = config_manager

        self._create_widgets()
        self._center_window()

        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.wait_window(self)

    def _center_window(self):
        """ダイアログを親ウィンドウの中央に表示する。"""
        self.update_idletasks()
        parent_x = self.master.winfo_x()
        parent_y = self.master.winfo_y()
        parent_width = self.master.winfo_width()
        parent_height = self.master.winfo_height()
        self.geometry(f"+{parent_x + (parent_width // 2) - (self.winfo_width() // 2)}+{parent_y + (parent_height // 2) - (self.winfo_height() // 2)}")

    def _create_widgets(self):
        main_frame = ttk.Frame(self, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 休憩時間設定
        break_time_frame = ttk.Frame(main_frame)
        break_time_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(break_time_frame, text="休憩時間:").pack(side=tk.LEFT)
        
        initial_minutes = self.config_manager.get('break_time_minutes', 60)
        self.break_time_var = tk.StringVar(value=str(initial_minutes))
        
        ttk.Spinbox(break_time_frame, from_=0, to=180, increment=15, textvariable=self.break_time_var, width=5).pack(side=tk.LEFT, padx=5)
        ttk.Label(break_time_frame, text="分").pack(side=tk.LEFT)

        # ボタン
        button_frame = ttk.Frame(self, padding=(0, 10, 0, 10))
        button_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        ttk.Button(button_frame, text="保存", command=self._on_save).pack(side=tk.RIGHT)

    def _on_save(self):
        self.config_manager.set('break_time_minutes', int(self.break_time_var.get()))
        self.config_manager.save()
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

        # --- 総労働時間 ---
        net_work_time_str = self.summary_data.get('net_work_time', 'N/A')
        start_str = self.summary_data.get('business_start_time_str', '')
        end_str = self.summary_data.get('business_end_time_str', '')
        
        display_text = f"総労働時間: {net_work_time_str} ({start_str}~{end_str})"
        ttk.Label(main_frame, text=display_text, font=("", 11, "bold")).pack(anchor="w", pady=2)
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

        # 「その他」の時間を追加
        other_time_str = self.summary_data.get('other_time', 'N/A')
        tree.insert("", tk.END, values=("その他", other_time_str))

        # --- 閉じるボタン ---
        button_frame = ttk.Frame(self, padding=(0, 10, 0, 10))
        button_frame.pack(fill=tk.X)
        close_button = ttk.Button(button_frame, text="閉じる", command=self.destroy)
        close_button.pack(side=tk.RIGHT)

class AllLogsViewerDialog(tk.Toplevel):
    """
    過去すべての作業ログを閲覧するためのダイアログ。
    """
    def __init__(self, parent, all_logs: list):
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()

        self.title("全作業ログ一覧")
        self.geometry("600x500")

        self.all_logs = all_logs

        self._create_widgets()
        self._center_window()

        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.wait_window(self)

    def _center_window(self):
        """ダイアログを親ウィンドウの中央に表示する。"""
        self.update_idletasks()
        parent_x = self.master.winfo_x()
        parent_y = self.master.winfo_y()
        parent_width = self.master.winfo_width()
        parent_height = self.master.winfo_height()
        self.geometry(f"+{parent_x + (parent_width // 2) - (self.winfo_width() // 2)}+{parent_y + (parent_height // 2) - (self.winfo_height() // 2)}")

    def _create_widgets(self):
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # show="tree headings" に変更し、#0列（ツリー構造）とヘッダーの両方を表示
        tree = ttk.Treeview(main_frame, columns=("task", "duration", "start", "end"), show="tree headings")
        tree.heading("#0", text="日付")
        tree.heading("task", text="工数名")
        tree.heading("duration", text="作業時間")
        tree.heading("start", text="開始時刻")
        tree.heading("end", text="終了時刻")

        tree.column("#0", width=100, anchor=tk.W) # 日付カラムの幅を設定
        tree.column("task", width=150)
        tree.column("duration", width=100, anchor=tk.E)
        tree.column("start", width=100, anchor=tk.CENTER)
        tree.column("end", width=100, anchor=tk.CENTER)
        # 日付ごとにログをグループ化
        logs_by_date = {}
        for log in self.all_logs:
            work_date = log['work_date']
            if work_date not in logs_by_date:
                logs_by_date[work_date] = []
            logs_by_date[work_date].append(log)

        # Treeviewにデータを挿入
        for work_date, logs in logs_by_date.items():
            # その日の最初のログから業務開始・終了時刻を取得
            first_log = logs[0]
            business_start_str = ""
            business_end_str = ""
            total_work_time_str = ""

            if first_log['business_start_time']:
                business_start_dt = datetime.fromisoformat(first_log['business_start_time'])
                business_start_str = business_start_dt.strftime('%H:%M')
            
            if first_log['business_end_time']:
                business_end_dt = datetime.fromisoformat(first_log['business_end_time'])
                business_end_str = business_end_dt.strftime('%H:%M')
                # 総作業時間を計算
                if first_log['business_start_time']:
                    total_work_duration = business_end_dt - datetime.fromisoformat(first_log['business_start_time'])
                    break_time_minutes = self.master.config_manager.get('break_time_minutes', 60)
                    net_work_duration = total_work_duration - timedelta(minutes=break_time_minutes)
                    total_work_time_str = f"{int(net_work_duration.total_seconds() // 3600)}h {int((net_work_duration.total_seconds() % 3600) // 60)}m"

            # 親ノード（日付）を挿入。
            date_node = tree.insert("", tk.END, text=work_date, values=("", total_work_time_str, business_start_str, business_end_str), open=False)
            
            # --- 子ノード（工数ごとの集計と個別ログ）の処理 ---
            tasks_for_day: Dict[str, Dict[str, Any]] = {}
            for log in logs:
                task_name = log['task_name']
                if task_name not in tasks_for_day:
                    tasks_for_day[task_name] = {'total_duration': timedelta(), 'logs': []}
                
                start_dt = datetime.fromisoformat(log['start_time'])
                end_dt = datetime.fromisoformat(log['end_time'])
                duration = end_dt - start_dt

                tasks_for_day[task_name]['total_duration'] += duration
                tasks_for_day[task_name]['logs'].append({'start': start_dt, 'end': end_dt, 'duration': duration})

            # 工数ごとの合計時間を表示
            all_tasks_duration = timedelta()
            for task_name, data in sorted(tasks_for_day.items()):
                total_duration = data['total_duration']
                all_tasks_duration += total_duration
                duration_str = f"{int(total_duration.total_seconds() // 3600):02}:{int((total_duration.total_seconds() % 3600) // 60):02}:{int(total_duration.total_seconds() % 60):02}"
                
                # 工数名のノードを挿入
                task_node = tree.insert(date_node, tk.END, text="", values=(task_name, duration_str, "", ""), open=False)

                # 個別ログのノードを挿入
                for log_detail in data['logs']:
                    log_duration_str = f"{int(log_detail['duration'].total_seconds() // 3600):02}:{int((log_detail['duration'].total_seconds() % 3600) // 60):02}:{int(log_detail['duration'].total_seconds() % 60):02}"
                    log_values = ("", log_duration_str, log_detail['start'].strftime('%H:%M:%S'), log_detail['end'].strftime('%H:%M:%S'))
                    tree.insert(task_node, tk.END, text="", values=log_values)
            
            # 「その他」時間を計算して表示
            if first_log['business_start_time'] and first_log['business_end_time']:
                business_start_dt = datetime.fromisoformat(first_log['business_start_time'])
                business_end_dt = datetime.fromisoformat(first_log['business_end_time'])
                total_work_duration = business_end_dt - business_start_dt
                break_time_minutes = self.master.config_manager.get('break_time_minutes', 60)
                break_time = timedelta(minutes=break_time_minutes)
                other_duration = total_work_duration - all_tasks_duration - break_time
                other_duration_str = f"{int(other_duration.total_seconds() // 3600):02}:{int((other_duration.total_seconds() % 3600) // 60):02}:{int(other_duration.total_seconds() % 60):02}"
                tree.insert(date_node, tk.END, values=("その他", other_duration_str, "", ""), text="")

        tree.pack(fill=tk.BOTH, expand=True)

        close_button = ttk.Button(main_frame, text="閉じる", command=self.destroy, padding=(10, 5))
        close_button.pack(pady=(10, 0))

class LogViewerDialog(tk.Toplevel):
    """
    特定のタスクのログ一覧を表示するダイアログ。
    """
    def __init__(self, parent, task_name: str, logs: list):
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()

        self.title(f"ログ詳細: {task_name}")
        self.geometry("400x300")

        self.task_name = task_name
        self.logs = logs

        self._create_widgets()
        self._center_window()

        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.wait_window(self)

    def _center_window(self):
        """ダイアログを親ウィンドウの中央に表示する。"""
        self.update_idletasks()
        parent_x = self.master.winfo_x()
        parent_y = self.master.winfo_y()
        parent_width = self.master.winfo_width()
        parent_height = self.master.winfo_height()
        self.geometry(f"+{parent_x + (parent_width // 2) - (self.winfo_width() // 2)}+{parent_y + (parent_height // 2) - (self.winfo_height() // 2)}")

    def _create_widgets(self):
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        tree = ttk.Treeview(main_frame, columns=("start", "end", "duration"), show="headings")
        tree.heading("start", text="開始時刻")
        tree.heading("end", text="終了時刻")
        tree.heading("duration", text="作業時間")
        tree.column("start", width=100, anchor=tk.CENTER)
        tree.column("end", width=100, anchor=tk.CENTER)
        tree.column("duration", width=100, anchor=tk.E)
        tree.pack(fill=tk.BOTH, expand=True)

        for log in self.logs:
            tree.insert("", tk.END, values=(log['start'], log['end'], log['duration']))

        close_button = ttk.Button(main_frame, text="閉じる", command=self.destroy, padding=(10, 5))
        close_button.pack(pady=(10, 0))