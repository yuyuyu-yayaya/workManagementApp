import json
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

class SessionManager:
    """
    作業セッションの状態をJSONファイルに保存・復元するクラス。
    """
    def __init__(self, session_file_path: Path):
        self.session_file = session_file_path

    def save_session(self, state: Dict[str, Any]):
        """
        現在のアプリケーション状態をJSONファイルに保存する。
        datetimeオブジェクトはISO 8601形式の文字列に変換する。
        """
        try:
            # datetimeオブジェクトを文字列に変換
            serializable_state = state.copy()
            for key, value in serializable_state.items():
                if isinstance(value, datetime):
                    serializable_state[key] = value.isoformat()

            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump(serializable_state, f, indent=4)
        except (IOError, TypeError) as e:
            print(f"セッションの保存に失敗しました: {e}")

    def load_session(self) -> Optional[Dict[str, Any]]:
        """
        JSONファイルからセッションを復元する。
        ISO 8601形式の文字列はdatetimeオブジェクトに変換する。
        """
        if not self.session_file.exists():
            return None
        
        try:
            with open(self.session_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            # 文字列をdatetimeオブジェクトに変換
            for key, value in state.items():
                if isinstance(value, str) and 'T' in value: # ISO形式の日時文字列を簡易的に判定
                    try:
                        state[key] = datetime.fromisoformat(value) # 復元したdatetimeオブジェクトを辞書に再代入する
                    except (ValueError, TypeError):
                        pass # 変換できない場合はそのまま
            
            return state
        except (IOError, json.JSONDecodeError) as e:
            print(f"セッションの復元に失敗しました: {e}")
            return None