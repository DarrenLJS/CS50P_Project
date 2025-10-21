import random

# Parent class Character with name for printing and 6 other attributes: location, health, offense, weapon, armour, equipment, and 2 behaviors: attack and move
class Character:
    def __init__(self, name, x, y):
        if not name or type(name) != str:
            raise ValueError("Invalid name")
        self.name = name
        self.location = [x, y]
        self.health = 100
        self.offense = 15
        self.weapon = "fists"
        self.armour = 0
        self.equipment = []

    # move() takes in ["N", "S", "E", "W"] direction and updated map. Cannot move diagonally
    def move(self, direction, items_d, players_d):

        # Checker to check if direction is invalid e.g. invalid input/out of bounds/occupied by another Character. If invalid, return False.
        def valid_direction_checker(direction):
            filtered = {k: v for k, v in players_d.items() if v != self}
            occupied = list(v.location for v in filtered.values())
            own_loc = self.location.copy()
            direct = direction.strip().lower()
            if direct not in ["n", "s", "e", "w"]:
                return False
            elif direct == "n":
                if self.location[0] == 0:
                    return False
                own_loc[0] -= 1
            elif direct == "s":
                if self.location[0] == 4:
                    return False
                own_loc[0] += 1
            elif direct == "e":
                if self.location[1] == 4:
                    return False
                own_loc[1] += 1
            elif direct == "w":
                if self.location[1] == 0:
                    return False
                own_loc[1] -= 1
            if own_loc in occupied:
                return False
            return True

        # If valid direction, move and print message with Character's name
        valid_direction = valid_direction_checker(direction)
        direct = direction.strip().lower()
        if not valid_direction:
            raise ValueError("Invalid direction")
        elif valid_direction:
            if direct == "n":
                self.location[0] -= 1
                print(f"{self.name} moved North.")
            elif direction == "s":
                self.location[0] += 1
                print(f"{self.name} moved South.")
            elif direction == "e":
                self.location[1] += 1
                print(f"{self.name} moved East.")
            elif direction == "w":
                self.location[1] -= 1
                print(f"{self.name} moved West.")

        # If item in the location, check if Apple/Armour/Sword
        # If Apple and <100 health, auto-consume Apple, heal up to 100 max health, print message with Character's name, and delete item from map. Else, item remains
        # If Armour or Sword, if not already equipped, pick up item, print message with Character's name, and delete item from map. Else, item remains
        # Updates items dict
        for item, loc in list(items_d.items()):
            if loc == self.location:
                if isinstance(item, Apple) and self.health < 100:
                    self.health = min(100, self.health + item.healing)
                    print(f"{self.name} ate {item.name}.")
                    del items_d[item]
                elif isinstance(item, Armour):
                    if self.armour == 0:
                        self.equipment.append(item)
                        self.armour = item.armour
                        print(f"{self.name} picked up {item.name}.")
                        del items_d[item]
                elif isinstance(item, Sword):
                    if self.weapon == "fists":
                        self.equipment.append(item)
                        self.offense = item.offense
                        self.weapon = item.name
                        print(f"{self.name} picked up {item.name}.")
                        del items_d[item]

    # attack() takes in Character object and updated players dict. Check if target in updated players dict
    def attack(self, player_name, players_d):
        if player_name not in players_d.keys():
            raise ValueError("Invalid player")
        player = players_d[player_name]

        # attack_roll() rolls 3 die and totals for both attacker and defender. If attacker >= defender, damage defender. Else, no damage
        # Damage = attacker.offense - defender.armour
        def attack_roll(self, player):
            offs = random.randint(3, 18)
            defs = random.randint(3, 18)
            if offs >= defs:
                damage = self.offense - player.armour
                player.health -= damage
                print(f"Success! {self.name} damaged {player.name} by {damage} using {self.weapon}.")
            elif defs > offs:
                print(f"{player.name} successfully blocked {self.name}'s attack!")

        # If target is 1 tile above/below/right/left of player, return attack_roll function. Else, raise ValueError
        if player.location[0] in [self.location[0] - 1, self.location[0] + 1] and player.location[1] == self.location[1]:
            return attack_roll(self, player)
        elif player.location[1] in [self.location[1] - 1, self.location[1] + 1] and player.location[0] == self.location[0]:
            return attack_roll(self, player)
        else:
            raise ValueError(f"{player.name} not in range")


# Parent class Item has name for printing and stores location
class Item:
    def __init__(self, name, x, y):
        self.name = name
        self.location = [x, y]

# Subclass Player refers to hero
class Player(Character):
    def __init__(self, name, x, y):
        super().__init__(name, x, y)

# Subclass Enemy refers to enemy bots
class Enemy(Character):
    def __init__(self, name, x, y):
        super().__init__(name, x, y)

# Subclass Apple heals for 25 hp
class Apple(Item):
    def __init__(self, name, x, y):
        super().__init__(name, x, y)
        self.healing = 25

# Subclass Armour grants 5 armour when equipped
class Armour(Item):
    def __init__(self, name, x, y):
        super().__init__(name, x, y)
        self.armour = 5

# Subclass Sword increases offense to 30
class Sword(Item):
    def __init__(self, name, x, y):
        super().__init__(name, x, y)
        self.offense = 30
