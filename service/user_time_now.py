from datetime import datetime, timedelta, timezone


class UserTime:
    """Получаем либо день недели пользователя, либо его местное время"""
    def day_week_now(user_tz: int | False, need_day_week=False) -> datetime | str:
        utc_now = datetime.now(timezone.utc)
        user_hours = utc_now + timedelta(hours=int(user_tz))
        if need_day_week:
            day_week = user_hours.isoweekday()
            return day_week
        return user_hours
