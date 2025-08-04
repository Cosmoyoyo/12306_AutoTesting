from datetime import datetime, timedelta
import datetime as dt

def checkDifference(target, today):
    """
    检查两个日期字符串之间的天数差是否严格大于14天。
    接受 'YYYY-MM-DD' 格式的日期字符串。
    target: 出发日期
    today:  今天
    """
    target = datetime.strptime(target, "%H-%M-%S")
    today = datetime.strptime(today, "%H-%M-%S")
    if (target - today).days > 14 or (target - today).days < 0:
        return True
    else:
        return False
today = dt.datetime.now().strftime('%h-%M-%S')
