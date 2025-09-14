from datetime import timedelta

def format_timedelta(td: timedelta) -> str:
    """timedeltaオブジェクトを HH:MM:SS 形式の文字列に変換する。"""
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"