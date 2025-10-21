from game import *
import sys

# To start game, prompt for name of hero for printing
# Default: generate map containing 4 Armours, 4 Swords, and 4 Apples
# Default: generate 3 enemy bots, keeping in mind occupied item locations. Hero spawns in middle of 5x5 map
def main():
    hero = input("Enter name: ")
    items_d = generate_map(4, 4, 4)
    players_d = generate_players(3, hero, items_d)

    # First, print items and players locations
    # Game loops through hero, Enemy_1, Enemy_2, and Enemy_3 systematically
    # Prompts player for an action. If "move", prompt direction. If "attack", prompt target. If invalid, print error message and reprompt
    while True:
        items_loc = {item.name: loc for item, loc in items_d.items()}
        print(items_loc)
        players_loc = {key: value.location for key, value in players_d.items()}
        print(players_loc)
        for value in players_d.values():
            print(f"{value.name} HP: {value.health}")
            inventory = [e.name for e in value.equipment]
            print(f"{value.name} Equipment: {inventory}")
        while True:
            hero_act = input("Action: ").strip().lower()
            if hero_act not in ["move", "attack", "surrender"]:
                print("Invalid action")
                continue
            if hero_act == "surrender":
                sys.exit()
            if hero_act == "move":
                try:
                    direction = input("Direction: ").strip().lower()
                    players_d["hero"].move(direction, items_d, players_d)
                except ValueError:
                    print("Invalid direction. Back to action selection.")
                    continue
                else:
                    break
            elif hero_act == "attack":
                try:
                    target = input("Target: ")
                    players_d["hero"].attack(target, players_d)
                except ValueError:
                    print("Invalid target. Back to action selection.")
                    continue
                else:
                    break

        # After player turn, update players dict to check if only hero remains in dict. Else, run enemies' turns
        # After every enemy turn, update players dict to check who remains and if hero eliminated.
        players_d = update_players(players_d)
        if len(players_d) == 1:
            print("Victory! All enemies have been eliminated!")
            break
        enemies_left = {key: value for key, value in players_d.items() if key != "hero"}
        for enemy_name, enemy in enemies_left.items():
            if enemy.health <= 0:
                players_d = update_players(players_d)
                continue
            enemy_turn(enemy_name, players_d, items_d)
            players_d = update_players(players_d)
        if "hero" not in players_d.keys():
            print("Game over!")
            break

# Randomly generates armours, swords, and apples in random locations, in this order. Map is 5x5 by default
# Returns items_d with Item object:location list
# 2 items cannot be in the same location. Hence, occupied list
# [2, 2] occupied by hero
def generate_map(armours, swords, apples):
    items_d = {}
    occupied = [[2, 2]]
    ac_count = 0
    sw_count = 0
    ap_count = 0
    while ac_count < armours:
        loc = [random.randint(0, 4), random.randint(0, 4)]
        if loc not in occupied:
            occupied.append(loc)
            items_d[Armour(f"armour_{ac_count+1}", loc[0], loc[1])] = loc
            ac_count += 1
    while sw_count < swords:
        loc = [random.randint(0, 4), random.randint(0, 4)]
        if loc not in occupied:
            occupied.append(loc)
            items_d[Sword(f"sword_{sw_count+1}", loc[0], loc[1])] = loc
            sw_count += 1
    while ap_count < apples:
        loc = [random.randint(0, 4), random.randint(0, 4)]
        if loc not in occupied:
            occupied.append(loc)
            items_d[Apple(f"apple_{ap_count+1}", loc[0], loc[1])] = loc
            ap_count += 1
    return items_d

# Hero starts in center of map. Map is 5x5 by default
# Randomly places enemies 1, 2 and 3 in random locations, in this order
# Returns players_d with "Name":Character object
# 2 Characters cannot be in the same location. Hence, occupied list
# Cannot place bots in same location as items
def generate_players(enemies, hero, items_d):
    players_d = {}
    players_d["hero"] = Player(hero, 2, 2)
    occupied = [[2,2]]
    for loc in items_d.values():
        occupied.append(loc)
    id = 0
    while id < enemies:
        loc = [random.randint(0, 4), random.randint(0, 4)]
        if loc not in occupied:
            occupied.append(loc)
            players_d[f"enemy_{id+1}"] = Enemy(f"enemy_{id+1}", loc[0], loc[1])
            id += 1
    return players_d

# enemy_turn() is AI behavior for enemies
def enemy_turn(enemy_name, players_d, items_d):
    enemy = players_d[enemy_name]

    # pick_action() determines action of bot. Priority: Attack > Items > Randomly move
    # If any enemies_near list, return list ["attack", [targets*]]
    # If any items_near dict, return list ["move", {item object:loc*}]
    # Else, return ["move"]
    def pick_action():
        enemies_near = []
        items_near = {}
        for key, value in players_d.items():
            if key == enemy_name:
                continue
            if value.location[0] in [enemy.location[0] - 1, enemy.location[0] + 1] and value.location[1] == enemy.location[1]:
                enemies_near.append(key)
            if value.location[1] in [enemy.location[1] - 1, enemy.location[1] + 1] and value.location[0] == enemy.location[0]:
                enemies_near.append(key)
        if len(enemies_near) >= 1:
            return ["attack", enemies_near]
        for item, loc in items_d.items():
            if loc[0] in [enemy.location[0] - 1, enemy.location[0] + 1] and loc[1] == enemy.location[1]:
                if isinstance(item, Armour) and item not in enemy.equipment:
                    items_near[item] = loc
                elif isinstance(item, Sword) and item not in enemy.equipment:
                    items_near[item] = loc
                elif isinstance(item, Apple) and enemy.health < 100:
                    items_near[item] = loc
            if loc[1] in [enemy.location[1] - 1, enemy.location[1] + 1] and loc[0] == enemy.location[0]:
                if isinstance(item, Armour) and item not in enemy.equipment:
                    items_near[item] = loc
                elif isinstance(item, Sword) and item not in enemy.equipment:
                    items_near[item] = loc
                elif isinstance(item, Apple) and enemy.health < 100:
                    items_near[item] = loc
        if len(items_near) >= 1:
            return ["move", items_near]
        else:
            return ["move"]

    action = pick_action()

    # If action = ["attack", [targets*]], attack a random enemy in range
    if len(action) > 1 and action[0] == "attack":
        target = random.choice(action[1])
        return enemy.attack(target, players_d)

    # If action = ["move", {item object:loc*}], priority: healing > equipment not already equipped > move randomly
    # If health < 100 and >=1 Apple in range, move to a random Apple location and heal
    # If health = 100 or no Apple in range, filter for equipment not already equipped, then move to a random not_equipped location
    # If no equipment or already equipped, move randomly
    elif len(action) > 1 and action[0] == "move":
        heal = {item: loc for item, loc in action[1].items() if isinstance(item, Apple)}
        if len(heal) >= 1:
            target = random.choice(list(heal.values()))
            if target[0] == enemy.location[0] - 1:
                return enemy.move("n", items_d, players_d)
            elif target[0] == enemy.location[0] + 1:
                return enemy.move("s", items_d, players_d)
            elif target[1] == enemy.location[1] + 1:
                return enemy.move("e", items_d, players_d)
            elif target[1] == enemy.location[1] - 1:
                return enemy.move("w", items_d, players_d)
        elif len(heal) == 0:
            not_equipped = {}
            if enemy.armour == 0:
                not_equipped.update({item: loc for item, loc in action[1].items() if isinstance(item, Armour)})
            if enemy.weapon == "fists":
                not_equipped.update({item: loc for item, loc in action[1].items() if isinstance(item, Sword)})
            if len(not_equipped) >= 1:
                target = random.choice(list(not_equipped.values()))
                if target[0] == enemy.location[0] - 1:
                    return enemy.move("n", items_d, players_d)
                elif target[0] == enemy.location[0] + 1:
                    return enemy.move("s", items_d, players_d)
                elif target[1] == enemy.location[1] + 1:
                    return enemy.move("e", items_d, players_d)
                elif target[1] == enemy.location[1] - 1:
                    return enemy.move("w", items_d, players_d)
    while True:
        try:
            direction = random.choice(["n", "s", "e", "w"])
            enemy.move(direction, items_d, players_d)
        except ValueError:
            continue
        else:
            break

# Checks and removes any Character with <=0 hp
def update_players(players_d):
    updated_players = {key: value for key, value in players_d.items() if value.health > 0}
    return updated_players

if __name__ == "__main__":
    main()
