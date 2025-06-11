from datetime import timedelta


def get_time_str(time_diff: timedelta) -> str:
    if time_diff > timedelta(0):
        time_diff_str = "Thought for "
        seconds = time_diff.total_seconds() % 60
        minutes = time_diff.total_seconds() // 60
        if minutes:
            if minutes:
                time_diff_str += f"{minutes} minutes"
            else:
                time_diff_str += f"{minutes} minute"
            if seconds:
                time_diff_str += ", "
        if seconds:
            if seconds > 1:
                time_diff_str += f"{seconds:.0f} seconds"
            else:
                time_diff_str += f"{seconds:.0f} second"
        return time_diff_str
    else:
        return ""
