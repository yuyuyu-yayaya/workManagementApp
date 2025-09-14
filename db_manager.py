import sqlite3
from pathlib import Path
from datetime import date, datetime, timedelta
from typing import Optional, List, Tuple, Dict, Any

from utils import format_timedelta

class DatabaseManager:
    """
    工数管理アプリのデータベース操作を管理するクラス。
    """
    def __init__(self, db_path: Path):
        """
        データベースマネージャーを初期化し、データベースへの接続とテーブル作成を行う。

        Args:
            db_path (Path): データベースファイルの絶対パス。
        """
        self.conn = None
        self.cursor = None
        self.db_path = db_path

        self._connect()
        self._create_tables() # 接続後にテーブルの存在を確認・作成する

    def _connect(self):
        """データベースに接続し、カーソルを作成する。"""
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row # カラム名でアクセスできるようにする
            self.cursor = self.conn.cursor()
            # 外部キー制約を毎回有効にする
            self.cursor.execute("PRAGMA foreign_keys = ON;")
        except sqlite3.Error as e:
            print(f"データベース接続エラー: {e}")
            raise  # 接続に失敗した場合は、ここでプログラムを停止させる

    def _create_tables(self):
        """設計に基づいたテーブルがなければ作成する。"""
        if not self.conn:
            return # 接続がない場合は何もしない
        with self.conn:
            # CREATE TABLE IF NOT EXISTS を使うことで、テーブルが存在しない場合のみ作成される
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS work_days (
                    id INTEGER PRIMARY KEY,
                    work_date TEXT NOT NULL UNIQUE,
                    start_time TEXT,
                    end_time TEXT
                );
            """)
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY,
                    task_name TEXT NOT NULL UNIQUE
                );
            """)
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS time_logs (
                    id INTEGER PRIMARY KEY,
                    work_day_id INTEGER NOT NULL,
                    task_id INTEGER NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    FOREIGN KEY (work_day_id) REFERENCES work_days (id) ON DELETE CASCADE,
                    FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE CASCADE
                );
            """)

    def add_task(self, task_name: str) -> Optional[int]:
        """
        新しい工数（タスク）をtasksテーブルに追加する。
        既に存在する場合は何もしない。

        Args:
            task_name (str): 追加する工数名。

        Returns:
            Optional[int]: 追加されたタスクのID。既に存在した場合はNone。
        """
        try:
            with self.conn:
                self.cursor.execute("INSERT INTO tasks (task_name) VALUES (?)", (task_name,))
                return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            return None
        except sqlite3.Error as e:
            print(f"タスク追加エラー: {e}")
            return None

    def update_task(self, task_id: int, new_task_name: str) -> bool:
        """
        既存のタスク名を更新する。

        Args:
            task_id (int): 更新するタスクのID。
            new_task_name (str): 新しいタスク名。

        Returns:
            bool: 更新が成功した場合はTrue、失敗した場合はFalse。
        """
        try:
            with self.conn:
                self.cursor.execute("UPDATE tasks SET task_name = ? WHERE id = ?", (new_task_name, task_id))
            return self.cursor.rowcount > 0
        except sqlite3.IntegrityError:
            return False
        except sqlite3.Error as e:
            print(f"タスク更新エラー: {e}")
            return False

    def delete_task(self, task_id: int) -> bool:
        """
        タスクを削除する。
        スキーマで ON DELETE CASCADE を指定しているため、関連する時間ログも自動で削除される。
        """
        try:
            with self.conn:
                self.cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            # rowcountは削除された行数を返す
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"タスク削除エラー: {e}")
            return False

    # --- work_days テーブル操作 ---

    def get_all_tasks(self) -> List[sqlite3.Row]:
        """
        登録されているすべてのタスクを取得する。

        Returns:
            List[sqlite3.Row]: タスクのリスト。
        """
        try:
            self.cursor.execute("SELECT id, task_name FROM tasks ORDER BY id")
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"タスク取得エラー: {e}")
            return []

    def get_or_create_work_day(self, work_date: date) -> Optional[int]:
        """
        指定された日付のwork_dayレコードを取得または作成する。

        Args:
            work_date (date): 対象の日付。

        Returns:
            Optional[int]: work_daysテーブルのID。
        """
        try:
            self.cursor.execute("SELECT id FROM work_days WHERE work_date = ?", (work_date.isoformat(),))
            row = self.cursor.fetchone()
            if row:
                return row['id']
            else:
                with self.conn:
                    self.cursor.execute("INSERT INTO work_days (work_date) VALUES (?)", (work_date.isoformat(),))
                    return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Work Day取得/作成エラー: {e}")
            return None

    def update_work_day_start_time(self, work_day_id: int, start_time: datetime) -> bool:
        """
        業務日の開始時刻を更新する。
        """
        try:
            with self.conn:
                self.cursor.execute(
                    "UPDATE work_days SET start_time = ? WHERE id = ?",
                    (start_time.isoformat(), work_day_id)
                )
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"業務日開始時刻の更新エラー: {e}")
            return False

    def update_work_day_end_time(self, work_day_id: int, end_time: datetime) -> bool:
        """
        業務日の終了時刻を更新する。
        """
        try:
            with self.conn:
                self.cursor.execute(
                    "UPDATE work_days SET end_time = ? WHERE id = ?",
                    (end_time.isoformat(), work_day_id)
                )
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"業務日終了時刻の更新エラー: {e}")
            return False

    def get_work_day_details(self, work_day_id: int) -> Optional[sqlite3.Row]:
        """
        指定された業務日の詳細情報を取得する。

        Args:
            work_day_id (int): 取得対象のwork_daysテーブルのID。

        Returns:
            Optional[sqlite3.Row]: 業務日の詳細情報。見つからなければNone。
        """
        try:
            self.cursor.execute("SELECT * FROM work_days WHERE id = ?", (work_day_id,))
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            print(f"業務日詳細の取得エラー: {e}")
            return None

    def get_work_day_by_date(self, work_date: date) -> Optional[sqlite3.Row]:
        """
        指定された日付のwork_dayレコードを取得する。

        Args:
            work_date (date): 対象の日付。

        Returns:
            Optional[sqlite3.Row]: work_daysテーブルのレコード。見つからなければNone。
        """
        try:
            self.cursor.execute("SELECT * FROM work_days WHERE work_date = ?", (work_date.isoformat(),))
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            print(f"日付によるWork Day取得エラー: {e}")
            return None
    def get_summary_for_day(self, work_day_id: int, business_start_time: datetime, business_end_time: datetime) -> Dict[str, Any]:
        """
        指定された業務日の作業サマリーを計算して返す。

        Args:
            work_day_id (int): work_daysテーブルのID。
            business_start_time (datetime): 業務全体の開始時刻。
            business_end_time (datetime): 業務全体の終了時刻。

        Returns:
            Dict[str, Any]: サマリーデータ。
        """
        logs = self.get_logs_for_day(work_day_id)
        tasks = self.get_all_tasks()
        task_map = {task['id']: task['task_name'] for task in tasks}

        total_task_duration = timedelta()
        task_details = {}

        for log in logs:
            task_id = log['task_id']
            start_time = datetime.fromisoformat(log['start_time'])
            end_time = datetime.fromisoformat(log['end_time'])
            duration = end_time - start_time
            total_task_duration += duration

            if task_id not in task_details:
                task_details[task_id] = {'name': task_map.get(task_id, '不明なタスク'), 'duration': timedelta()}
            task_details[task_id]['duration'] += duration

        total_work_duration = business_end_time - business_start_time
        other_duration = total_work_duration - total_task_duration

        return {
            'total_work_time': format_timedelta(total_work_duration),
            'total_task_time': format_timedelta(total_task_duration),
            'other_time': format_timedelta(other_duration),
            'task_details': [{'name': v['name'], 'duration_str': format_timedelta(v['duration'])} for v in sorted(task_details.values(), key=lambda x: x['name'])]
        }

    # --- time_logs テーブル操作 ---

    def start_time_log(self, work_day_id: int, task_id: int, start_time: datetime) -> Optional[int]:
        """
        新しい時間ログを開始する。

        Args:
            work_day_id (int): work_daysテーブルのID。
            task_id (int): tasksテーブルのID。
            start_time (datetime): 作業開始時刻。

        Returns:
            Optional[int]: 作成されたtime_logsのID。
        """
        try:
            with self.conn:
                self.cursor.execute(
                    "INSERT INTO time_logs (work_day_id, task_id, start_time) VALUES (?, ?, ?)",
                    (work_day_id, task_id, start_time.isoformat())
                )
                return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"時間ログ開始エラー: {e}")
            return None

    def end_time_log(self, time_log_id: int, end_time: datetime):
        """
        指定された時間ログに終了時刻を記録する。

        Args:
            time_log_id (int): 更新対象のtime_logsのID。
            end_time (datetime): 作業終了時刻。
        """
        try:
            with self.conn:
                self.cursor.execute(
                    "UPDATE time_logs SET end_time = ? WHERE id = ?",
                    (end_time.isoformat(), time_log_id)
                )
        except sqlite3.Error as e:
            print(f"時間ログ終了エラー: {e}")

    def get_logs_for_day(self, work_day_id: int) -> List[sqlite3.Row]:
        """
        指定された業務日のすべての時間ログを取得する。
        終了時刻が記録されているもののみを対象とする。

        Args:
            work_day_id (int): work_daysテーブルのID。

        Returns:
            List[sqlite3.Row]: 時間ログのリスト。
        """
        try:
            self.cursor.execute("SELECT task_id, start_time, end_time FROM time_logs WHERE work_day_id = ? AND end_time IS NOT NULL", (work_day_id,))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"日次ログ取得エラー: {e}")
            return []

    def get_all_completed_logs(self) -> List[sqlite3.Row]:
        """
        完了したすべての時間ログを、日付とタスク名とともに取得する。
        日付の降順、開始時刻の昇順でソートする。

        Returns:
            List[sqlite3.Row]: 時間ログのリスト。
        """
        try:
            self.cursor.execute("""
                SELECT
                    wd.work_date,
                    t.task_name,
                    tl.start_time,
                    tl.end_time
                FROM time_logs tl
                JOIN work_days wd ON tl.work_day_id = wd.id
                JOIN tasks t ON tl.task_id = t.id
                WHERE tl.end_time IS NOT NULL
                ORDER BY wd.work_date DESC, tl.start_time ASC
            """)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"全ログ取得エラー: {e}")
            return []

    def get_logs_for_task_on_day(self, work_day_id: int, task_id: int) -> List[sqlite3.Row]:
        """
        指定された業務日とタスクに紐づく時間ログを取得する。

        Args:
            work_day_id (int): work_daysテーブルのID。
            task_id (int): tasksテーブルのID。

        Returns:
            List[sqlite3.Row]: 時間ログのリスト。
        """
        try:
            self.cursor.execute("SELECT * FROM time_logs WHERE work_day_id = ? AND task_id = ?", (work_day_id, task_id))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"タスク別ログ取得エラー: {e}")
            return []

    def delete_time_log(self, time_log_id: int) -> bool:
        """
        特定の時間ログを削除する。

        Args:
            time_log_id (int): 削除対象のtime_logsテーブルのID。

        Returns:
            bool: 削除が成功した場合はTrue、失敗した場合はFalse。
        """
        try:
            with self.conn:
                self.cursor.execute("DELETE FROM time_logs WHERE id = ?", (time_log_id,))
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"時間ログ削除エラー: {e}")
            return False

    def close(self):
        """データベース接続を閉じる。"""
        if self.conn:
            self.conn.close()

if __name__ == "__main__":
    db = DatabaseManager()
    # --- テストコード ---
    today_id = db.get_or_create_work_day(date.today())
    task_id = db.add_task("設計作業") or db.cursor.execute("SELECT id FROM tasks WHERE task_name=?", ("設計作業",)).fetchone()['id']

    if today_id and task_id:
        start = datetime.now()
        log_id = db.start_time_log(today_id, task_id, start)
        if log_id:
            # ... 何か作業 ...
            end = datetime.now()
            db.end_time_log(log_id, end)

    db.close()