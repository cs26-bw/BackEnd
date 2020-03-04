from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
# from pusher import Pusher
from django.http import JsonResponse
from decouple import config
from django.contrib.auth.models import User
from django.http import HttpResponseNotFound
from .models import *
from rest_framework.decorators import api_view
import json

# instantiate pusher
# pusher = Pusher(app_id=config('PUSHER_APP_ID'), key=config('PUSHER_KEY'), secret=config('PUSHER_SECRET'), cluster=config('PUSHER_CLUSTER'))

@csrf_exempt
@api_view(["GET"])
def initialize(request):
    user = request.user
    if not user.is_authenticated:
        return HttpResponseNotFound()
    player = user.player
    player_id = player.id
    uuid = player.uuid
    room = player.room()
    players = room.playerNames(player_id)
    return JsonResponse({'uuid': uuid, 'name':player.user.username, 'title':room.title, 'description':room.description, 'players':players}, safe=True)


# @csrf_exempt
@api_view(["POST"])
def move(request):
    if not request.user.is_authenticated:
        return HttpResponseNotFound()
    dirs={"n": "north", "s": "south", "e": "east", "w": "west"}
    reverse_dirs = {"n": "south", "s": "north", "e": "west", "w": "east"}
    player = request.user.player
    player_id = player.id
    player_uuid = player.uuid
    data = json.loads(request.body)
    direction = data['direction']
    room = player.room()
    nextRoomID = None
    if direction == "n":
        nextRoomID = room.n_to
    elif direction == "s":
        nextRoomID = room.s_to
    elif direction == "e":
        nextRoomID = room.e_to
    elif direction == "w":
        nextRoomID = room.w_to
    if nextRoomID is not None and nextRoomID > 0:
        nextRoom = Room.objects.get(id=nextRoomID)
        player.currentRoom=nextRoomID
        player.save()
        players = nextRoom.playerNames(player_id)
        currentPlayerUUIDs = room.playerUUIDs(player_id)
        nextPlayerUUIDs = nextRoom.playerUUIDs(player_id)
        # for p_uuid in currentPlayerUUIDs:
        #     pusher.trigger(f'p-channel-{p_uuid}', u'broadcast', {'message':f'{player.user.username} has walked {dirs[direction]}.'})
        # for p_uuid in nextPlayerUUIDs:
        #     pusher.trigger(f'p-channel-{p_uuid}', u'broadcast', {'message':f'{player.user.username} has entered from the {reverse_dirs[direction]}.'})
        return JsonResponse({'name':player.user.username, 'title':nextRoom.title, 'description':nextRoom.description, 'players':players, 'error_msg':""}, safe=True)
    else:
        players = room.playerNames(player_id)
        return JsonResponse({'name':player.user.username, 'title':room.title, 'description':room.description, 'players':players, 'error_msg':"You cannot move that way."}, safe=True)

#@csrf_exempt
@api_view(["GET"])
def rooms(request):
    if not request.user.is_authenticated:
        return HttpResponseNotFound()
    rooms = Room.objects.all()
    response = []
    cache = [None for x in range(0, len(rooms))]
    def get_room_info(id_in):
        result = {}
        if id_in == 0:
            return result
        found = cache[id_in - 1]
        if not found:
            found = Room.objects.get(id=id_in)
            cache[id_in - 1] = found
        result = {'id': found.id, 'title': found.title, 'description': found.description, 'x': found.x, 'y': found.y}
        return result
    for room in rooms:
        response.append({'id': room.id, 
                    'title': room.title,
                    'description': room.description,
                    'north': get_room_info(room.n_to),
                    'south': get_room_info(room.s_to),
                    'west': get_room_info(room.w_to),
                    'east': get_room_info(room.e_to),
                    'x': room.x,
                    'y': room.y})
    return JsonResponse(response, safe=False)

@csrf_exempt
@api_view(["POST"])
def say(request):
    if not request.user.is_authenticated:
        return HttpResponseNotFound()
    # IMPLEMENT
    return JsonResponse({'error':"Not yet implemented"}, safe=True, status=500)
