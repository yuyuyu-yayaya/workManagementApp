import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from typing import Dict, Any
from datetime import datetime, date, timedelta

from db_manager import DatabaseManager
from app_state import AppState
from dialogs import StartTimeDialog, EndTimeDialog, ResultDialog, LogViewerDialog, AllLogsViewerDialog, EditTimeDialog, SettingsDialog
from session_manager import SessionManager
from config_manager import ConfigManager
from utils import format_timedelta

class WorkManagementApp(tk.Tk):
    # Treeviewのカラム識別子を定数として定義
    COL_ACTION = "action"
    COL_TASK_NAME = "task_name"
    COL_LOG = "log"

    def __init__(self, db_manager: DatabaseManager, app_state: AppState, session_manager: SessionManager, config_manager: ConfigManager):
        super().__init__()
        self.db = db_manager
        self.state = app_state
        self.session_manager = session_manager
        self.config_manager = config_manager

        self.title("工数管理アプリ")
        self.geometry("900x500")

        # Treeviewの各行ウィジェットを管理するための辞書
        self.task_items: Dict[int, Any] = {}

        self.create_widgets()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        # --- メインフレーム ---
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- 上部フレーム (ボタン類) ---
        top_frame = ttk.Frame(self, padding=(10, 10, 10, 0))
        top_frame.grid(row=0, column=0, sticky="ew")

        add_task_button = ttk.Button(top_frame, text="＋ 工数を追加", command=self.add_new_task)
        add_task_button.pack(side=tk.LEFT)

        show_logs_button = ttk.Button(top_frame, text="ログ一覧", command=self.show_all_logs)
        show_logs_button.pack(side=tk.LEFT, padx=5)

        settings_button = ttk.Button(top_frame, text="設定", command=self.open_settings)
        settings_button.pack(side=tk.LEFT, padx=5)

        # 業務開始時刻を表示するラベル
        start_time_str = "N/A" # 初期値はN/A。後で更新する。
        self.start_time_label = ttk.Label(top_frame, text=f"業務開始: {start_time_str}", font=("", 10))
        # 中央に配置するために左右に expand する
        self.start_time_label.pack(side=tk.LEFT, padx=(20, 0)) # 右側のpaddingを削除

        edit_start_time_button = ttk.Button(top_frame, text="編集", command=self.edit_business_start_time, width=5)
        edit_start_time_button.pack(side=tk.LEFT, padx=(5, 20)) # ラベルとの間に少しスペースを空ける

        end_business_button = ttk.Button(top_frame, text="業務終了", command=self.end_business)
        end_business_button.pack(side=tk.RIGHT) # 業務終了ボタンは右端のまま

        # --- Treeview用フレーム ---
        tree_frame = ttk.Frame(self, padding=(10, 10, 10, 10))
        tree_frame.grid(row=1, column=0, sticky="nsew")

        # --- Treeview (タスク一覧) ---
        columns = (self.COL_TASK_NAME, self.COL_ACTION, "total_time", self.COL_LOG)
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")

        # ヘッダー設定
        self.tree.heading(self.COL_TASK_NAME, text="工数名")
        self.tree.heading(self.COL_ACTION, text="アクション")
        self.tree.heading("total_time", text="合計時間")
        self.tree.heading(self.COL_LOG, text="ログ")
        # カラム幅設定
        self.tree.column(self.COL_TASK_NAME, width=250, anchor=tk.CENTER)
        self.tree.column(self.COL_ACTION, width=100, anchor=tk.CENTER)
        self.tree.column("total_time", width=100, anchor=tk.CENTER)
        self.tree.column(self.COL_LOG, width=350, anchor=tk.CENTER)

        # 計測中の行のスタイルを設定
        self.tree.tag_configure("measuring", background="#e0f0ff") # 明るい青色
        self.tree.pack(side="left", fill=tk.BOTH, expand=True)

        self.tree.bind("<Double-1>", self.on_task_double_click)
        self.load_tasks()

    def load_tasks(self):
        """データベースからタスクとログを読み込み、集計してTreeviewに表示する"""
        # 既存の表示をクリア
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.task_items.clear()

        # その日の完了したログを取得
        logs = self.db.get_logs_for_day(self.state.work_day_id)

        # タスクごとにログを集計
        task_summary: Dict[int, Dict[str, Any]] = {}
        for log in logs:
            task_id = log['task_id']
            if task_id not in task_summary:
                task_summary[task_id] = {'total_duration': timedelta(), 'log_texts': []}

            start_time = datetime.fromisoformat(log['start_time'])
            end_time = datetime.fromisoformat(log['end_time'])
            duration = end_time - start_time
            task_summary[task_id]['total_duration'] += duration

            log_text = f"{start_time.strftime('%H:%M')}~{end_time.strftime('%H:%M')}"
            task_summary[task_id]['log_texts'].append(log_text)

        # 全てのタスクをTreeviewに表示
        tasks = self.db.get_all_tasks()
        for task in tasks:
            task_id = task['id']
            summary = task_summary.get(task_id)

            total_hours = (summary['total_duration'].total_seconds() / 3600) if summary else 0.0
            log_str = ", ".join(summary['log_texts']) if summary else ""

            # Treeviewにアイテムを追加
            values = (task[self.COL_TASK_NAME], "Start", f"{total_hours:.1f}h", log_str)
            item_id = self.tree.insert("", tk.END, values=values, tags=(str(task_id),))
            self.task_items[task_id] = item_id
        
        # 復元されたセッションがあればUIに反映
        if self.state.current_task_id:
            self.update_task_ui_for_start(self.state.current_task_id)

    def on_task_double_click(self, event):
        """Treeviewの行がダブルクリックされたときの処理"""
        item_id = self.tree.focus() # 選択されている行のIDを取得
        if not item_id:
            return

        # クリックされた列を特定
        column = self.tree.identify_column(event.x)
        
        # 'task_name' カラムがダブルクリックされた場合、編集モードに入る
        if column == f"#{self.tree['columns'].index(self.COL_TASK_NAME) + 1}":
            self.edit_task_name(item_id)
        # 'log' カラムがダブルクリックされた場合、ログ詳細を表示
        elif column == f"#{self.tree['columns'].index(self.COL_LOG) + 1}":
            task_id = int(self.tree.item(item_id, "tags")[0])
            task_name = self.tree.item(item_id, "values")[0] # task_nameはvaluesの1番目
            self.show_log_details(task_id, task_name)
        else:
            # それ以外のカラム（アクション列など）がクリックされた場合、タスクの開始/終了処理
            values = self.tree.item(item_id, "values")
            tags = self.tree.item(item_id, "tags")
            clicked_task_id = int(tags[0])

            # ダブルクリックされたタスクが現在実行中のタスクか確認
            if self.state.current_task_id == clicked_task_id:
                # 実行中のタスクなので、終了処理を呼び出す
                self.end_task(clicked_task_id)
            else:
                # 新しいタスクなので、開始処理を呼び出す
                self.start_task(clicked_task_id, values[0]) # task_nameはvaluesの0番目

    def show_log_details(self, task_id: int, task_name: str):
        """指定されたタスクのログ詳細をポップアップで表示する"""
        logs_from_db = self.db.get_logs_for_task_on_day(self.state.work_day_id, task_id)
        
        formatted_logs = []
        for log in logs_from_db:
            if log['end_time']: # 完了したログのみ表示
                start_time = datetime.fromisoformat(log['start_time'])
                end_time = datetime.fromisoformat(log['end_time'])
                duration = end_time - start_time
                formatted_logs.append({
                    'start': start_time.strftime('%H:%M:%S'),
                    'end': end_time.strftime('%H:%M:%S'),
                    'duration': format_timedelta(duration)
                })
        
        LogViewerDialog(self, task_name, formatted_logs)

    def edit_task_name(self, item_id: str):
        """Treeviewのタスク名をインプレースで編集する。"""
        # 編集中のタスクは開始/終了できないようにする
        if self.state.current_task_id is not None:
            messagebox.showinfo("情報", "タスク計測中は工数名を編集できません。")
            return

        # セルの位置とサイズを取得
        bbox = self.tree.bbox(item_id, column=self.COL_TASK_NAME)
        if not bbox:
            return

        x, y, width, height = bbox
        
        # Entryウィジェットを作成
        current_name = self.tree.set(item_id, self.COL_TASK_NAME)
        entry_var = tk.StringVar(value=current_name)
        entry = ttk.Entry(self.tree, textvariable=entry_var)
        entry.place(x=x, y=y, width=width, height=height)
        entry.focus_set()
        entry.selection_range(0, tk.END)

        def on_commit(event=None):
            new_name = entry_var.get().strip()
            entry.destroy()
            
            if new_name and new_name != current_name:
                task_id = int(self.tree.item(item_id, "tags")[0])
                if self.db.update_task(task_id, new_name):
                    self.tree.set(item_id, self.COL_TASK_NAME, new_name)
                else:
                    messagebox.showerror("更新失敗", f"工数名 '{new_name}' は既に存在するか、更新できませんでした。")
            # もし名前が変わっていなくても、UIを元に戻すために何もしない

        def on_cancel(event=None):
            entry.destroy()

        # イベントをバインド
        entry.bind("<Return>", on_commit)      # Enterキーで確定
        entry.bind("<KP_Enter>", on_commit)    # テンキーのEnterでも確定
        entry.bind("<FocusOut>", on_commit)    # フォーカスが外れたら確定
        entry.bind("<Escape>", on_cancel)      # Escapeキーでキャンセル

    def show_all_logs(self):
        """すべての作業ログを閲覧するダイアログを表示する"""
        all_logs = self.db.get_all_completed_logs()
        AllLogsViewerDialog(self, all_logs)
        
    def open_settings(self):
        """設定ダイアログを開く"""
        SettingsDialog(self, self.config_manager)

    def edit_business_start_time(self):
        """業務開始時刻を編集するダイアログを表示する"""
        if not self.state.business_start_time:
            messagebox.showinfo("情報", "まだ業務が開始されていません。")
            return

        dialog = EditTimeDialog(self, "業務開始時刻の編集", self.state.business_start_time)
        new_time = dialog.selected_time

        if new_time:
            # 状態を更新
            self.state.business_start_time = new_time
            # DBを更新
            self.db.update_work_day_start_time(self.state.work_day_id, new_time)
            # UIラベルを更新
            self.start_time_label.config(text=f"業務開始: {new_time.strftime('%H:%M:%S')}")
            # セッションを保存
            self.session_manager.save_session(self.state.to_dict())

    def add_new_task(self):
        """新しい工数を追加するポップアップを表示"""
        task_name = simpledialog.askstring("工数追加", "新しい工数名を入力してください:", parent=self)
        if task_name:
            new_id = self.db.add_task(task_name)
            if new_id:
                self.load_tasks() # Treeviewを再読み込み
            else:
                messagebox.showwarning("追加失敗", f"工数 '{task_name}' は既に存在します。")

    def start_task(self, task_id: int, task_name: str):
        """タスク開始処理"""
        # 他のタスクが実行中か確認
        if self.state.current_task_id is not None:
            messagebox.showwarning("確認", "他のタスクが実行中です。先に終了してください。")
            return

        # 画面4（開始時刻確認ポップアップ）を表示
        dialog = StartTimeDialog(self, task_name)
        start_time = dialog.start_time

        if start_time:
            # --- 業務開始時刻の更新ロジック ---
            # もし、まだ業務開始時刻が記録されていない（＝その日最初のタスク）なら、
            # このタスクの開始時刻を業務開始時刻としてDBに記録する
            if not self.state.business_start_time:
                self.state.business_start_time = start_time
                self.db.update_work_day_start_time(self.state.work_day_id, start_time)
                # UIラベルも更新
                self.start_time_label.config(text=f"業務開始: {start_time.strftime('%H:%M:%S')}")

            # 1. データベースに時間ログを開始したことを記録
            log_id = self.db.start_time_log(self.state.work_day_id, task_id, start_time)

            if log_id:
                # 2. アプリケーションの状態を更新
                self.state.start_task(task_id, task_name, start_time, log_id)

                # 3. UIを更新
                self.update_task_ui_for_start(task_id)

                # 4. セッションを保存
                self.session_manager.save_session(self.state.to_dict())
            else:
                messagebox.showerror("エラー", "データベースへのログ記録に失敗しました。")

    def update_task_ui_for_start(self, task_id: int):
        """タスク開始時のUI更新"""
        item_id = self.task_items.get(task_id)
        if not item_id:
            return

        # アクション列のテキストを更新
        self.tree.set(item_id, self.COL_ACTION, "Stop")

        # 背景色を変更するためのタグを追加
        self.tree.item(item_id, tags=self.tree.item(item_id, "tags") + ("measuring",))

    def end_business(self):
        """業務終了処理"""
        # 画面6（業務終了確認）
        if messagebox.askyesno("業務終了", "本日の業務を終了しますか？"):
            business_end_time = datetime.now()
            self.db.update_work_day_end_time(self.state.work_day_id, business_end_time)

            # 設定から休憩時間を取得
            break_minutes = self.config_manager.get('break_time_minutes', 60)
            # サマリーデータをDBManagerから取得
            summary_data = self.db.get_summary_for_day(
                self.state.work_day_id,
                self.state.business_start_time,
                business_end_time,
                break_minutes
            )

            # 表示用に開始・終了時刻をサマリーデータに追加
            summary_data['business_start_time_str'] = self.state.business_start_time.strftime('%H:%M')
            summary_data['business_end_time_str'] = business_end_time.strftime('%H:%M')

            # 画面7（リザルト画面）を表示
            ResultDialog(self, summary_data)
            self.on_closing()

    def end_task(self, task_id: int):
        """タスク終了処理"""
        # 画面5（終了時刻確認ポップアップ）を表示
        dialog = EndTimeDialog(self, self.state.current_task_name)
        end_time = dialog.end_time

        if end_time:
            # 1. データベースのログを更新
            self.db.end_time_log(self.state.current_log_id, end_time)

            # 2. UIを更新
            self.update_task_ui_for_end(task_id)

            # 3. アプリケーションの状態をリセット
            self.state.end_task()
            
            # 4. セッションファイルをクリア
            self.session_manager.save_session(self.state.to_dict())

            # 4. Treeviewを再読み込みして合計時間とログを更新
            self.load_tasks()

    def update_task_ui_for_end(self, task_id: int):
        """タスク終了時のUI更新"""
        item_id = self.task_items.get(task_id)
        if not item_id:
            return

        # アクションを元に戻す
        self.tree.set(item_id, self.COL_ACTION, "Start")
        
        # 背景色を元に戻すためにタグを削除
        current_tags = list(self.tree.item(item_id, "tags"))
        if "measuring" in current_tags:
            current_tags.remove("measuring")
            self.tree.item(item_id, tags=tuple(current_tags))


    def on_closing(self):
        # タスクが実行中でない場合（＝正常な中断）はセッションを残す
        if self.state.current_task_id is None:
            # 正常終了時はセッションをクリアする
            self.session_manager.save_session(self.state.to_dict())

        self.db.close()
        self.destroy()

if __name__ == "__main__":
    from pathlib import Path
    import os

    # データベースの保存先を AppData/Roaming に設定します。
    # これはアプリケーションがデータを保存するための標準的な場所です。
    # os.getenv('APPDATA') は 'C:\Users\ユーザー名\AppData\Roaming' を指します。
    app_data_dir = Path(os.getenv('APPDATA', Path.home() / 'Documents')) / "WorkManagementApp"
    
    # データ保存用フォルダがなければ作成します。
    app_data_dir.mkdir(exist_ok=True)
    
    db_path = app_data_dir / "work_management.db"
    session_path = app_data_dir / "session.json"
    config_path = app_data_dir / "config.json"

    # --- アプリケーション起動シーケンス ---

    # 1. 各マネージャと状態クラスをインスタンス化
    db_manager = DatabaseManager(db_path)
    config_manager = ConfigManager(config_path)
    app_state = AppState()
    session_manager = SessionManager(session_path)

    # 2. 今日の日付に対応する work_day_id をDBから取得/作成し、状態にセット
    today_work_day_id = db_manager.get_or_create_work_day(app_state.work_date)
    app_state.work_day_id = today_work_day_id

    # 3. セッションファイルを読み込み、今日の日付のデータであれば状態を復元
    session_data = session_manager.load_session()
    if session_data and session_data.get('work_day_id') == today_work_day_id:
        app_state.from_dict(session_data)

    # --- 前日のサマリー表示（その日最初の起動時のみ） ---
    today_str = date.today().isoformat()
    last_summary_shown_date = session_data.get('last_summary_shown_date') if session_data else None

    if last_summary_shown_date != today_str:
        yesterday = date.today() - timedelta(days=1)
        yesterday_work_day = db_manager.get_work_day_by_date(yesterday)

        if yesterday_work_day and yesterday_work_day['end_time']:
            try:
                start_time_val = yesterday_work_day['start_time']
                end_time_val = yesterday_work_day['end_time']

                if start_time_val and end_time_val:
                    start_time = datetime.fromisoformat(start_time_val)
                    end_time = datetime.fromisoformat(end_time_val)
                    
                    break_minutes = config_manager.get('break_time_minutes', 60)
                    summary_data = db_manager.get_summary_for_day(yesterday_work_day['id'], start_time, end_time, break_minutes)
                    
                    # 表示用に開始・終了時刻をサマリーデータに追加
                    summary_data['business_start_time_str'] = start_time.strftime('%H:%M')
                    summary_data['business_end_time_str'] = end_time.strftime('%H:%M')

                    # リザルトダイアログを表示 (親ウィンドウなしで表示)
                    ResultDialog(None, summary_data)

            except (TypeError, ValueError) as e:
                print(f"前日のサマリー表示中にエラーが発生しました: {e}")

        # サマリー表示日を記録してセッションを保存
        current_session = app_state.to_dict()
        current_session['last_summary_shown_date'] = today_str
        session_manager.save_session(current_session)

    # 4. 業務開始時刻がまだ設定されていなければ、記録してセッションに保存
    if not app_state.business_start_time:
        pass # 最初のタスク開始時に記録するため、ここでは何もしない

    # 5. アプリケーションのUIを初期化
    app = WorkManagementApp(db_manager, app_state, session_manager, config_manager)

    # 6. UIのラベルに業務開始時刻を反映させ、タスクリストを読み込む
    if app.state.business_start_time:
        start_time_str = app.state.business_start_time.strftime('%H:%M:%S')
        app.start_time_label.config(text=f"業務開始: {start_time_str}")
    app.load_tasks()

    app.mainloop()