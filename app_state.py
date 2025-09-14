from datetime import datetime, date
from typing import Optional, Dict, Any

class AppState:
    """
    アプリケーション全体の状態を管理するシングルトンクラス。
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        # インスタンスがまだ作成されていない場合にのみ、新しいインスタンスを作成
        if not cls._instance:
            cls._instance = super(AppState, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # __new__ によって常に同じインスタンスが返されるため、
        # この初期化は一度しか実行されないようにフラグで管理する
        if not hasattr(self, '_initialized'):
            self.reset()
            self._initialized = True

    def reset(self):
        """アプリケーションの状態を初期値にリセットする。"""
        self.work_date: date = date.today()
        self.work_day_id: Optional[int] = None
        self.business_start_time: Optional[datetime] = None
        self.business_end_time: Optional[datetime] = None
        self.current_task_id: Optional[int] = None
        self.current_task_name: Optional[str] = None
        self.current_task_start_time: Optional[datetime] = None
        self.current_log_id: Optional[int] = None

    def start_business(self):
        """業務開始時刻を記録する"""
        if not self.business_start_time:
            self.business_start_time = datetime.now()

    def start_task(self, task_id: int, task_name: str, start_time: datetime, log_id: int):
        """計測するタスクの情報をセットする"""
        self.current_task_id = task_id
        self.current_task_name = task_name
        self.current_task_start_time = start_time
        self.current_log_id = log_id

    def end_task(self):
        """計測中のタスク情報をリセットする"""
        self.current_task_id = None
        self.current_task_name = None
        self.current_task_start_time = None
        self.current_log_id = None

    def to_dict(self) -> Dict[str, Any]:
        """現在の状態を辞書に変換する。"""
        return {
            'work_day_id': self.work_day_id,
            'business_start_time': self.business_start_time,
            'current_task_id': self.current_task_id,
            'current_task_name': self.current_task_name,
            'current_task_start_time': self.current_task_start_time,
            'current_log_id': self.current_log_id,
        }

    def from_dict(self, state_dict: Dict[str, Any]):
        """辞書から状態を復元する。"""
        self.work_day_id = state_dict.get('work_day_id')
        self.business_start_time = state_dict.get('business_start_time')
        self.current_task_id = state_dict.get('current_task_id')
        self.current_task_name = state_dict.get('current_task_name')
        self.current_task_start_time = state_dict.get('current_task_start_time')
        self.current_log_id = state_dict.get('current_log_id')
        # work_dateは起動時に常に今日の日付で初期化されるため、復元対象外とする
        # business_end_timeも同様