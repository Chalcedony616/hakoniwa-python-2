from rest_framework import serializers
from .models import Island, MapTile, Plan, Log, History

class MapTileSerializer(serializers.ModelSerializer):
    class Meta:
        model = MapTile
        fields = ['terrain', 'landvalue']

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ['command', 'coordinates', 'quantity', 'target_island_id']

class IslandSerializer(serializers.ModelSerializer):
    map_data = serializers.SerializerMethodField()
    plans = PlanSerializer(many=True)

    class Meta:
        model = Island
        fields = '__all__'

    def get_map_data(self, obj):
        # Retrieve the map data and format it as a 2D list
        map_data = [[None for _ in range(12)] for _ in range(12)]
        map_tiles = obj.map_data.all()

        # MapTileを座標に基づいて配置
        for tile in map_tiles:
            map_data[tile.y][tile.x] = MapTileSerializer(tile).data
        
        return map_data
    
class LogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log
        fields = ['id', 'island', 'turn', 'message', 'is_confidential', 'is_allLog']

class HistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = History
        fields = ['turn', 'message']