from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from django.db.models import Subquery, OuterRef, Max
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
from .models import GlobalSettings, Island, MapTile, Plan, Log, History
from .serializers import IslandSerializer, LogSerializer, HistorySerializer
from .config import TURN_TIME, JST
from game.log_messages import log_discover, log_change_name, log_change_owner

from .utils import get_adjacent_hexes, calculate_island_status
import random

@api_view(['POST'])
def register(request):
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email')

    if not username or not password or not email:
        return Response({"error": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        validate_password(password)
    except ValidationError as e:
        return Response({"error": e.messages}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.create_user(username=username, password=password, email=email)
        return Response({"message": "User created successfully."}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def create_island(request):
    username = request.data.get('username')
    password = request.data.get('password')
    owner_name = request.data.get('owner_name')
    island_name = request.data.get('island_name')
    
    settings = GlobalSettings.objects.first()
    if settings is None:
        raise ValueError("GlobalSettings object does not exist. Please create one.")
    current_turn = settings.turn_count

    if not username or not password or not owner_name or not island_name:
        return Response({"error": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=username, password=password)
    if user is None:
        return Response({"error": "Invalid username or password."}, status=status.HTTP_401_UNAUTHORIZED)

    if Island.objects.filter(user=user).exists():
        return Response({"error": "User already has an island."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # 1. 島を作成
        island = Island.objects.create(
            user=user,
            name=island_name,
            owner=owner_name,
            discovery_turn=current_turn,
            population=0,
            area=0,
            funds=100,  # 初期資金100億円
            food=100,  # 初期食料10000トン
            farm_size=0,
            factory_size=0,
            mine_size=0,
            missile_capacity=0,
        )

        # 2. すべてのHEXを海で初期化し、MapTileオブジェクトを作成
        map_tiles = [
            MapTile(island=island, x=i, y=j, terrain=0, landvalue=0)
            for i in range(12) for j in range(12)
        ]
        
        # MapTileオブジェクトを一括で保存
        MapTile.objects.bulk_create(map_tiles)

        # island.map_dataにMapTileオブジェクトを追加
        island.map_data.set(map_tiles)

        # 3. マップ中央の4x4を荒地に変更
        MapTile.objects.filter(island=island, x__gte=4, x__lt=8, y__gte=4, y__lt=8).update(terrain=2)

        # 4. 陸地増殖処理を120回繰り返す
        for _ in range(120):
            x = random.randint(2, 10)
            y = random.randint(2, 10)
            tile = MapTile.objects.get(island=island, x=x, y=y)
            if tile.terrain == 2:  # 荒地なら平地にする
                tile.terrain = 3
            elif tile.terrain == 1:  # 浅瀬なら荒地にする
                tile.terrain = 2
            elif tile.terrain == 0:  # 海なら条件次第で浅瀬にする
                adjacent_hexes = get_adjacent_hexes(x, y)
                for adj_x, adj_y in adjacent_hexes:
                    if 0 <= adj_x < 12 and 0 <= adj_y < 12:
                        adjacent_tile = MapTile.objects.get(island=island, x=adj_x, y=adj_y)
                        if adjacent_tile.terrain in [2, 3]:  # 隣接HEXに荒地か平地があれば
                            tile.terrain = 1  # 浅瀬にする
                            break
            tile.save()

        # 5. 森が4個作成されるまで森作成処理を行う
        forests_created = 0
        while forests_created < 4:
            x = random.randint(4, 8)
            y = random.randint(4, 8)
            tile = MapTile.objects.get(island=island, x=x, y=y)
            if tile.terrain != 4:  # 既に森でなければ
                tile.terrain = 4
                tile.landvalue = 5
                tile.save()
                forests_created += 1

        # 6. 村が2個作成されるまで村作成処理を行う
        villages_created = 0
        while villages_created < 2:
            x = random.randint(4, 8)
            y = random.randint(4, 8)
            tile = MapTile.objects.get(island=island, x=x, y=y)
            if tile.terrain not in [4, 10]:  # 既に森または村でなければ
                tile.terrain = 10
                tile.landvalue = 5
                tile.save()
                island.population += 5  # 村ができるごとに人口を5増加させる
                villages_created += 1

        # 7. 山を1個作成する
        mountain_created = False
        while not mountain_created:
            x = random.randint(4, 8)
            y = random.randint(4, 8)
            tile = MapTile.objects.get(island=island, x=x, y=y)
            if tile.terrain not in [4, 10]:  # 既に森または村でなければ
                tile.terrain = 5
                tile.save()
                mountain_created = True

        # 8. ミサイル基地を1個作成する
        mbase_created = False
        while not mbase_created:
            x = random.randint(4, 8)
            y = random.randint(4, 8)
            tile = MapTile.objects.get(island=island, x=x, y=y)
            if tile.terrain not in [4, 5, 10]:  # 既に森、山または村でなければ
                tile.terrain = 30
                tile.save()
                mbase_created = True

        # 9. 初期計画データを作成
        plans = [Plan.objects.create(command=0, coordinates='0,0', target_island_id=island.id, quantity=0) for _ in range(30)]
        island.plans.set(plans)

        # 10. ステータスを計算し、島に反映
        calculated_status = calculate_island_status(island.id)
        island.area = calculated_status['area']
        island.population = calculated_status['population']
        island.farm_size = calculated_status['farm_size']
        island.factory_size = calculated_status['factory_size']
        island.mine_size = calculated_status['mine_size']
        island.missile_capacity = calculated_status['missile_capacity']

        # 11. ランキングを初期化（最下位に設定）
        island.ranking = Island.objects.count()  # 現在の島の総数 + 1
        log_discover(current_turn, island.id, island.name)

        island.save()

        return Response({"message": "Island created successfully.", "id": island.id}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def list_islands(request):
    islands = Island.objects.order_by('ranking')  # ranking 順にソート
    serializer = IslandSerializer(islands, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def island_detail(request, pk):
    try:
        island = Island.objects.get(pk=pk)
    except Island.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    serializer = IslandSerializer(island)
    return Response(serializer.data)

@api_view(['POST'])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    island_id = request.data.get('island_id')

    if not username or not password or not island_id:
        return Response({"error": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=username, password=password)
    if user is None:
        return Response({"error": "Invalid username or password."}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        island = Island.objects.get(id=island_id, user=user)
    except Island.DoesNotExist:
        return Response({"error": "Island not found or you do not have permission."}, status=status.HTTP_403_FORBIDDEN)

    return Response({"message": "Login successful.", "island_id": island.id}, status=status.HTTP_200_OK)

@api_view(['PUT'])
def update_plans(request, pk):
    try:
        island = Island.objects.get(pk=pk)
    except Island.DoesNotExist:
        return Response({"error": "Island not found."}, status=status.HTTP_404_NOT_FOUND)

    plans_data = request.data.get('plans')
    
    if not isinstance(plans_data, list) or len(plans_data) != 30:
        return Response({"error": "Invalid plans data."}, status=status.HTTP_400_BAD_REQUEST)

    # 更新前に既存のplansを削除
    island.plans.all().delete()

    # 新しいplansを追加
    for plan_data in plans_data:
        plan = Plan(
            command=plan_data['command'],
            coordinates=plan_data['coordinates'],
            target_island_id=plan_data['target_island_id'],
            quantity=plan_data['quantity'],
        )
        plan.save()
        island.plans.add(plan)

    island.save()

    return Response({"message": "Plans updated successfully."}, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_island_logs(request, island_id):
    # Get the most recent 42 turns with logs for the specified island
    recent_turns = Log.objects.filter(island__id=island_id).values('turn').distinct().order_by('-turn')[:42]

    # Get logs for those recent turns, ordered by turn descending and id ascending (oldest logs first within the turn)
    logs = Log.objects.filter(island__id=island_id, turn__in=Subquery(recent_turns)).order_by('-turn', 'id')

    serializer = LogSerializer(logs, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def global_recent_logs(request):
    # 直近12ターンのターン番号を取得
    recent_turns = Log.objects.filter(is_allLog=True).values('turn').distinct().order_by('-turn')[:12]
    recent_turn_numbers = [turn['turn'] for turn in recent_turns]

    # 直近12ターン分のログを取得
    logs = Log.objects.filter(is_allLog=True, turn__in=recent_turn_numbers).order_by('-turn', 'id')

    serializer = LogSerializer(logs, many=True)
    return JsonResponse(serializer.data, safe=False)

@api_view(['GET'])
def get_histories(request):
    # 直近10個のHistoryオブジェクトを取得し、ターン内で逆順にソート
    histories = History.objects.all().order_by('-turn', '-id')[:10]  # idが大きいほど後に作られたもの
    serializer = HistorySerializer(histories, many=True)
    return Response(serializer.data)

def get_turn_info(request):
    # グローバルセッティングから現在のターン数を読み込み
    settings = GlobalSettings.objects.first()
    current_turn = settings.turn_count

    # 現在時刻を日本時間で読み込み
    now = timezone.now().astimezone(JST)

    # 最終更新時刻と次回の更新時刻を判定
    today_str = now.strftime('%Y-%m-%d')
    last_update_time = None
    next_update_time = None

    for time_str in TURN_TIME:
        update_time = datetime.strptime(f"{today_str} {time_str}", '%Y-%m-%d %H:%M:%S')
        update_time = JST.localize(update_time)  # 日本時間としてオフセットを付与
        if update_time <= now:
            last_update_time = update_time
        elif update_time > now:
            next_update_time = update_time
            break
    
    # 次回の更新時刻が特定できなければ、次回の更新は翌日の最初の更新時刻
    if not next_update_time:
        next_update_time = datetime.strptime(f"{today_str} {TURN_TIME[0]}", '%Y-%m-%d %H:%M:%S')
        next_update_time = JST.localize(next_update_time) + timedelta(days=1)
    
    # 更新までの残り時刻を決定
    time_remaining = next_update_time - now

    return JsonResponse({
        'current_turn': current_turn,
        'last_update_time': last_update_time.strftime('%Y-%m-%d %H:%M:%S'),
        'next_update_time': next_update_time.strftime('%Y-%m-%d %H:%M:%S'),
        'time_remaining': str(time_remaining)
    })

@api_view(['GET', 'PUT'])
def island_detail(request, pk):
    try:
        island = Island.objects.get(pk=pk)
    except Island.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    settings = GlobalSettings.objects.first()
    if settings is None:
        raise ValueError("GlobalSettings object does not exist. Please create one.")
    current_turn = settings.turn_count

    if request.method == 'GET':
        serializer = IslandSerializer(island)
        return Response(serializer.data)

    elif request.method == 'PUT':
        data = request.data
        funds_deducted = False

        if 'name' in data and data['name'] != island.name:
            log_change_name(current_turn, island.id, island.name, data['name'])
            island.name = data['name']
            funds_deducted = True  # コストを引くフラグを立てる
        if 'owner' in data and data['owner'] != island.owner:
            log_change_owner(current_turn, island.id, island.name, data['owner'])
            island.owner = data['owner']
            funds_deducted = True  # コストを引くフラグを立てる
        if 'comment' in data:
            island.comment = data['comment']

        # フラグが立っている場合に一度だけコストを引く
        if funds_deducted:
            island.funds -= 500
        
        serializer = IslandSerializer(island, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)