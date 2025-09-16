import json
from pathlib import Path
from typing import Dict, Any

class ConfigManager:
    """
    設定をJSONファイルに保存・復元するクラス。
    """
    def __init__(self, config_file_path: Path):
        self.config_file = config_file_path
        self.defaults = {
            'break_time_minutes': 60
        }
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """
        JSONファイルから設定を読み込む。ファイルがなければデフォルト設定を返す。
        """
        if not self.config_file.exists():
            return self.defaults.copy()
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            # デフォルト値とマージして、新しい設定項目に対応
            return {**self.defaults, **config_data}
        except (IOError, json.JSONDecodeError) as e:
            print(f"設定の読み込みに失敗しました: {e}")
            return self.defaults.copy()

    def get(self, key: str, default: Any = None) -> Any:
        """設定値を取得する。"""
        return self.config.get(key, default)

    def set(self, key: str, value: Any):
        """設定値をセットする。"""
        self.config[key] = value

    def save(self):
        """
        現在の設定をJSONファイルに保存する。
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
        except IOError as e:
            print(f"設定の保存に失敗しました: {e}")