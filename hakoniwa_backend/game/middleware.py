from datetime import datetime, timedelta
from django.db import transaction
from django.utils import timezone
from .models import GlobalSettings
from .management.commands.hako_turn import update_turn
from .config import TURN_TIME

class UpdateTurnMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # GlobalSettings オブジェクトを取得
        global_settings = GlobalSettings.objects.first()

        # is_updating が False の場合のみ run_turn_updates_if_needed を実行
        if not global_settings.is_updating:
            self.run_turn_updates_if_needed()

        # 次のミドルウェアやビューを呼び出す
        response = self.get_response(request)
        
        return response

    def run_turn_updates_if_needed(self):
        # トランザクションを使ってロックをかける
        with transaction.atomic():
            settings = GlobalSettings.objects.select_for_update().first()
            now = timezone.now()

            # last_updatedの日付を取得
            last_update_date = settings.last_updated.date()

            # 現在の日付と時刻を取得
            now_date = now.date()
            now_time = now.time()

            # ターン更新の基準となる時間を生成する関数
            def get_turn_time(date, time_str):
                return timezone.make_aware(datetime.combine(date, datetime.strptime(time_str, "%H:%M:%S").time()))

            # 最後の更新から何回TURN_TIMEが経過したかをカウントする
            updates_needed = 0
            last_update_time = None

            for day in (last_update_date + timedelta(days=i) for i in range((now_date - last_update_date).days + 1)):
                for time_str in TURN_TIME:
                    turn_time = get_turn_time(day, time_str)

                    if turn_time > settings.last_updated and turn_time <= now:
                        updates_needed += 1
                        last_update_time = turn_time  # 最後の更新時刻を記録

            # 必要なターン更新がある場合に処理を実行
            if updates_needed > 0:
                settings.is_updating = True
                settings.save()

                try:
                    # 必要な回数だけ update_turn を実行
                    for _ in range(updates_needed):
                        update_turn()

                    # update_turn後に再度GlobalSettingsを取得し直す
                    settings = GlobalSettings.objects.select_for_update().first()

                finally:
                    # 更新終了後に設定を元に戻す
                    settings.is_updating = False
                    settings.last_updated = last_update_time  # 最後の更新時刻を記録
                    settings.save()

