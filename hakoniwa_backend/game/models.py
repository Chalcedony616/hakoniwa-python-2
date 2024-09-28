from django.db import models
from django.contrib.auth.models import User
from .config import GIVEUP_ABSENT

class GlobalSettings(models.Model):
    turn_count = models.IntegerField(default=0)
    game_name = models.CharField(max_length=100, default="箱庭諸島２ for Python")
    last_updated = models.DateTimeField()
    is_updating = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.game_name} - Turn: {self.turn_count}"

class MapTile(models.Model):
    island = models.ForeignKey('Island', on_delete=models.CASCADE, related_name='map_tiles', null=True)
    x = models.IntegerField()
    y = models.IntegerField()
    terrain = models.IntegerField()
    landvalue = models.IntegerField()

    def to_dict(self):
        return {
            'id': self.id,
            'island_id': self.island.id if self.island else None,
            'x': self.x,
            'y': self.y,
            'terrain': self.terrain,
            'landvalue': self.landvalue,
        }

class Plan(models.Model):
    command = models.IntegerField()
    coordinates = models.CharField(max_length=5)
    target_island_id = models.IntegerField()
    quantity = models.IntegerField()

class Island(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    owner = models.CharField(max_length=100)
    comment = models.CharField(max_length=100, default="（未登録）")
    discovery_turn = models.IntegerField()
    population = models.IntegerField()
    area = models.IntegerField()
    funds = models.IntegerField()
    food = models.IntegerField()
    farm_size = models.IntegerField()
    factory_size = models.IntegerField()
    mine_size = models.IntegerField()
    missile_capacity = models.IntegerField()
    absent = models.IntegerField(default=GIVEUP_ABSENT - 2) # 放置ターン
    preparing = models.IntegerField(default=0) # このターンの地ならしの実行回数
    propaganda = models.BooleanField(default=False) # 誘致活動が実行中であることのフラグ
    monstersend = models.IntegerField(default=0) # 怪獣を派遣された数
    monumentfly = models.IntegerField(default=0) # 記念碑を発射された数
    boatpeople = models.IntegerField(default=0) # 難民
    turnprize = models.BooleanField(default=0) # ターン杯
    prosperity = models.BooleanField(default=False) # 繁栄賞
    superprosperity = models.BooleanField(default=False) # 超繁栄賞
    ultraprosperity = models.BooleanField(default=False) # 究極繁栄賞
    peace = models.BooleanField(default=False) # 平和賞
    superpeace = models.BooleanField(default=False) # 超平和賞
    ultrapeace = models.BooleanField(default=False) # 究極平和賞
    tragedy = models.BooleanField(default=False) # 災難賞
    supertragedy = models.BooleanField(default=False) # 超災難賞
    ultratragedy = models.BooleanField(default=False) # 究極災難賞
    ranking = models.IntegerField(default=99) #島の順位
    map_data = models.ManyToManyField(MapTile, related_name='island_maps')  # related_nameを設定
    plans = models.ManyToManyField(Plan)

    def __str__(self):
        return self.name
    
class IslandBackup(models.Model):
    original_island_id = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=100)
    owner = models.CharField(max_length=100)
    discovery_turn = models.IntegerField()
    population = models.IntegerField()
    area = models.IntegerField()
    funds = models.IntegerField()
    food = models.IntegerField()
    farm_size = models.IntegerField()
    factory_size = models.IntegerField()
    mine_size = models.IntegerField()
    missile_capacity = models.IntegerField()
    turnprize = models.BooleanField(default=0)
    prosperity = models.BooleanField(default=False)
    superprosperity = models.BooleanField(default=False)
    ultraprosperity = models.BooleanField(default=False)
    peace = models.BooleanField(default=False)
    superpeace = models.BooleanField(default=False)
    ultrapeace = models.BooleanField(default=False)
    tragedy = models.BooleanField(default=False)
    supertragedy = models.BooleanField(default=False)
    ultratragedy = models.BooleanField(default=False)
    map_data = models.JSONField()
    backup_date = models.DateTimeField(auto_now_add=True)  # バックアップの作成日を記録

    def __str__(self):
        return f"Backup of {self.name} (ID: {self.original_island_id})"

class Log(models.Model):
    island = models.ForeignKey(Island, on_delete=models.SET_NULL, null=True, related_name='logs')
    turn = models.IntegerField()
    message = models.TextField()
    is_confidential = models.BooleanField(default=False) 
    is_allLog = models.BooleanField(default=True)
    
    def __str__(self):
        log_type = "機密" if self.is_confidential else "通常"
        return f"Turn {self.turn}: {log_type} - {self.island.name if self.island else 'Deleted Island'}"
    
class History(models.Model):
    turn = models.IntegerField()
    message = models.TextField()

    def __str__(self):
        return f"Turn {self.turn}"