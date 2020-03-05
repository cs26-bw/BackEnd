from django.contrib.auth.models import User
from adventure.models import Player, Room
import random
import string


class WorldGenerator:
    def __init__(self):
        self.grid = None
        self.width = 0
        self.height = 0
        self.starting_room = None

    def generate_rooms(self, size_x, size_y, num_rooms):
        Room.objects.all().delete()
        reverse_dirs = {"n": "s", "s": "n", "e": "w", "w": "e"}
        
        # Initialize the grid
        self.grid = [None] * size_y
        self.width = size_x
        self.height = size_y
        for i in range( len(self.grid) ):
            self.grid[i] = [None] * size_x

        # Start from the center of the grid
        x = size_x//2
        y = size_y//2
        room_count = 0

        # Initialize valid directions
        directions = []
        if y < size_y -1:
            directions.append(0)
        if y > 0:
            directions.append(2)
        if x < size_x -1:
            directions.append(1)
        if x > 0:
            directions.append(3)

        # Choose a random direction
        direction = random.choice(directions)


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
            direction = random.choice(directions)
        rooms = Room.objects.all()
        self.generate_room_data(rooms)
        self.generate_room_text(rooms)

    def generate_room_data(self, rooms):
        buildings = self.get_file_contents('./util/seed/buildings.txt', lambda x: (x[0], x[1]))
        for room in rooms:
            entrances = set()
            if room.n_to:
                entrances.add("north")
            if room.e_to:
                entrances.add("east")
            if room.s_to:
                entrances.add("south")
            if room.w_to:
                entrances.add("west")
            num_entrances = len(entrances)
            if num_entrances >= 3:
                room.room_type = "building"
                building = random.choice(buildings)
                room.name = building[0]
                room.building_type = building[1]
            elif num_entrances == 2:
                room.room_type = "path"
                room.name = "sidewalk"
            else:
                room.room_type = "dead_end"
                room.name = "dead end"
            room.save()

    def generate_room_text(self, rooms):
        building_types = {"restaurant": "That restaurant always seems busy.", "school": "It seems that there's a lot of students in there.", "store": "They sell a large variety of goods.", "residence": "It's a huge building.", "business": "A lot of people work here.", "medical": "This is a new hospital.", "entertainment": "The price of admission is listed on the front.", "manufacturing": "You can't go inside due to safety regulations.", "empty": "A lot of empty space is available.", "transport": "People are patiently waiting around.", "other": "This was newly built.", "outdoors": "This park is pretty popular."}
        path_types = {"pristine", "regular", "old", "crumbling"}
        adjectives = self.get_file_contents('./util/seed/adjectives.txt')
        adverbs = self.get_file_contents('./util/seed/adverbs.txt')
        nouns = self.get_file_contents('./util/seed/nouns.txt')
        names = self.get_file_contents('./util/seed/names.txt')
        surnames = self.get_file_contents('./util/seed/surnames.txt')
        for room in rooms:
            room_type = room.room_type
            title = room.name
            desc = ""
            if room_type == "path" or room_type == "dead_end":
                title = string.capwords(room.name)
            elif room_type == "building":
                title = self.generate_room_title(room, adjectives, adverbs, nouns, names, surnames)
            desc = self.generate_room_description(room, building_types, path_types)
            room.title = title
            room.description = desc
            room.save()

    def generate_room_title(self, room, adjectives, adverbs, nouns, names, surnames):
        chance = random.random()
        title = []
        if chance < 0.25:
            title.append((random.choice(adverbs)).title())
            title.append((random.choice(adjectives)).title())
        else:
            if chance < 0.5:
                title.append(random.choice(surnames))
            else:
                if chance < 0.75:
                    title.append((random.choice(adjectives)).title())
                name = random.choice(names)
                if chance > 0.85:
                    name += "'s"
                title.append(name)
        title.append(string.capwords(room.name))
        return " ".join(title)

    def generate_room_description(self, room, building_types, path_types):
        room_type = room.room_type
        building_type = room.building_type
        desc = []
        if room_type == "dead_end":
            desc.append(f"You come across a dead end.")
        elif room_type == "path":
            path_type = random.choice(tuple(path_types))
            desc.append("You're walking along a sidewalk.")
            if path_type == "pristine":
                desc.append("The concrete in this section seems new.")
            elif path_type == "old":
                desc.append("Specks of dirt and litter cover your path.")
            elif path_type == "crumbling":
                desc.append("You can't help but notice all of the cracks and holes.")
        elif room_type == "building":
            desc.append(f"You find yourself next to {self.get_noun_with_prep(room.name)}.")
            desc.append(building_types[building_type])

        desc.append("\n\n")
        entrances = [None, None, None, None]
        if room.n_to:
            entrances[0] = self.get_noun_with_prep(Room.objects.get(id=room.n_to).name)
            entrances[0] += " to the north"
        if room.e_to:
            entrances[1] = self.get_noun_with_prep(Room.objects.get(id=room.e_to).name)
            entrances[1] += " to the east"
        if room.s_to:
            entrances[2] = self.get_noun_with_prep(Room.objects.get(id=room.s_to).name)
            entrances[2] += " to the south"
        if room.w_to:
            entrances[3] = self.get_noun_with_prep(Room.objects.get(id=room.w_to).name)
            entrances[3] += " to the west"
        routes = [x for x in entrances if x]
        formatted_routes = ", ".join(routes[:-2] + [" and ".join(routes[-2:])])
        desc.append(f"There's {formatted_routes}.")
        return " ".join(desc)

    def get_noun_with_prep(self, noun):
        ch = noun[0]
        prep = "a"
        if ch == "a" or ch == "e" or ch == "i" or ch == "o" or ch == "u":
            prep = "an"
        return f"{prep} {noun}"

    def get_file_contents(self, url, app=lambda x:x[0]):
        file_contents = open(url, 'r')
        contents = []
        for line in file_contents.readlines():
            data = line.rstrip().split(';')
            contents.append(app(data))
        return contents

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


w = WorldGenerator()
num_rooms = 100
width = 20
height = 20
w.generate_rooms(width, height, num_rooms)
w.print_rooms()

rooms = Room.objects.all()
for room in rooms:
    print(room.id, room.title, room.description, room.n_to, room.w_to, room.s_to, room.e_to, room.x, room.y)

print(f"\n\nWorld\n  height: {height}\n  width: {width},\n  num_rooms: {num_rooms}\n")

players=Player.objects.all()
for p in players:
    p.currentRoom= w.starting_room.id
    p.save()

