from django.contrib.auth.models import User
from adventure.models import Player, Room
import random
from util.landmarks import Landmark

class World:
    def __init__(self):
        self.grid = None
        self.width = 0
        self.height = 0
        self.starting_room = None

    def generate_rooms(self, size_x, size_y, num_rooms):
        Room.objects.all().delete()
        reverse_dirs = {"n": "s", "s": "n", "e": "w", "w": "e"}
        '''
        Fill up the grid, bottom to top, in a zig-zag pattern
        '''

        # Initialize the grid
        self.grid = [None] * size_y
        self.width = size_x
        self.height = size_y
        for i in range( len(self.grid) ):
            self.grid[i] = [None] * size_x

        # Start from lower-left corner (0,0)
        x = size_x//2 # (this will become 0 on the first step)
        y = size_y//2
        room_count = 0


        directions = []
        if y < size_y -1:
            directions.append(0)
        if y > 0:
            directions.append(2)
        if x < size_x -1:
            directions.append(1)
        if x > 0:
            directions.append(3)

        # Start generating rooms to the east
        direction = random.choice(directions)  # 1: east, -1: west


        # While there are rooms to be created...
        previous_room = None
        while room_count < num_rooms:
            if direction == 0:
                room_direction = "n"
                y += 1
            elif direction == 1:
                room_direction = "e"
                x += 1
            elif direction == 2:
                room_direction = "s"
                y -= 1
            else:
                room_direction = "w"
                x -= 1
            existing = self.grid[y][x]
            if not existing:
                room = Room(title="A Generic Room", description="This is a generic room.", x = x, y = y)
                room.save()
                # Note that in Django, you'll need to save the room after you create i
                # Save the room in the World grid
                self.grid[y][x] = room
                if not self.starting_room:
                    self.starting_room = room
                room_count += 1
            else:
                room = existing

            # Connect the new room to the previous room
            if previous_room is not None:
                if room_direction not in reverse_dirs:
                    print("Invalid direction")
                    continue
                reverse_dir = reverse_dirs[room_direction]
                previous_room.connectRooms(room, room_direction)
                room.connectRooms(previous_room, reverse_dir)

            # Update iteration variables
            previous_room = room


            directions = []
            if y < size_y - 1:
                directions.append(0)
            if y > 0:
                directions.append(2)
            if x < size_x - 1:
                directions.append(1)
            if x > 0:
                directions.append(3)

            # Start generating rooms to the east
            direction = random.choice(directions)  # 1: east, -1: west


    def generate_room_data(self):

        possible_names = [
            Landmark("Starbucks", "this is a starbucks"),
            Landmark("Post office", "this is where u get ur mail"),
            Landmark("walmart", "here at walmart we got the best prices"),
            Landmark("Park", "this is a dog park"),
            Landmark("Police Station", "this is a police station")
        ]

        rooms = Room.objects.all()
        for room in rooms:
            landmark = random.choice(possible_names)
            room.title = landmark.title
            room.description = landmark.description
            room.save()



    def print_rooms(self):
        '''
        Print the rooms in room_grid in ascii characters.
        '''

        # Add top border
        str = "# " * ((3 + self.width * 5) // 2) + "\n"

        # The console prints top to bottom but our array is arranged
        # bottom to top.
        #
        # We reverse it so it draws in the right direction.
        reverse_grid = list(self.grid) # make a copy of the list
        reverse_grid.reverse()
        for row in reverse_grid:
            # PRINT NORTH CONNECTION ROW
            str += "#"
            for room in row:
                if room is not None and room.n_to:
                    str += "  |  "
                else:
                    str += "     "
            str += "#\n"
            # PRINT ROOM ROW
            str += "#"
            for room in row:
                if room is not None and room.w_to:
                    str += "-"
                else:
                    str += " "
                if room is not None:
                    str += f"{room.id}".zfill(3)
                else:
                    str += "   "
                if room is not None and room.e_to:
                    str += "-"
                else:
                    str += " "
            str += "#\n"
            # PRINT SOUTH CONNECTION ROW
            str += "#"
            for room in row:
                if room is not None and room.s_to:
                    str += "  |  "
                else:
                    str += "     "
            str += "#\n"

        # Add bottom border
        str += "# " * ((3 + self.width * 5) // 2) + "\n"

        # Print string
        print(str)


w = World()
num_rooms = 100
width = 20
height = 20
w.generate_rooms(width, height, num_rooms)
w.generate_room_data()
w.print_rooms()

print(f"\n\nWorld\n  height: {height}\n  width: {width},\n  num_rooms: {num_rooms}\n")

players=Player.objects.all()
for p in players:
    p.currentRoom= w.starting_room.id
    p.save()

