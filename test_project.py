import pytest
from project import generate_map, generate_players, enemy_turn, update_players
from game import *


def test_generate_map():
    items_d = generate_map(4, 4, 4)
    armours = [item for item in items_d.keys() if isinstance(item, Armour)]
    swords = [item for item in items_d.keys() if isinstance(item, Sword)]
    apples = [item for item in items_d.keys() if isinstance(item, Apple)]

    # Check counts
    assert len(armours) == 4
    assert len(swords) == 4
    assert len(apples) == 4

    # Check no duplicates in locations
    locs = list(items_d.values())
    dupli = []
    for i in locs:
        if i not in dupli:
            dupli.append(i)
    assert len(locs) == len(dupli)


def test_generate_players():
    items_d = generate_map(4, 4, 4)
    players_d = generate_players(3, "hero", items_d)
    enemies = {k: v for k, v in players_d.items() if k != "hero"}

    # Check hero is in center
    assert players_d["hero"].location == [2, 2]

    # Check number of enemies
    assert len(enemies) == 3

    # Check no player occupies same space as item
    item_locs = list(items_d.values())
    player_locs = [p.location for p in players_d.values()]
    for loc in player_locs:
        assert loc not in item_locs

    # Check no duplicate player locations
    dupli = []
    for i in player_locs:
        if i not in dupli:
            dupli.append(i)
    assert len(player_locs) == len(dupli)


def test_update_players():
    players_d = {
        "hero": Player("hero", 2, 2),
        "enemy_1": Enemy("enemy_1", 0, 0),
        "enemy_2": Enemy("enemy_2", 1, 1),
        "enemy_3": Enemy("enemy_3", 3, 3)
    }

    # Simulate 2 defeated enemies
    players_d["enemy_1"].health = 0
    players_d["enemy_3"].health = 0
    updated = update_players(players_d)

    assert "enemy_1" not in updated
    assert "enemy_3" not in updated
    assert "hero" in updated
    assert "enemy_2" in updated


def test_enemy_turn():
    items_d = {
        Apple("apple_1", 1, 0): [1, 0],
        Armour("armour_1", 2, 0): [2, 0],
        Sword("sword_1", 1, 1): [1, 1],
        Armour("armour_3", 3, 3): [3, 3],
        Sword("sword_3", 3, 0): [3, 0]
    }
    players_d = {
        "hero": Player("hero", 2, 2),
        "enemy_1": Enemy("enemy_1", 0, 0),
        "enemy_2": Enemy("enemy_2", 1, 2),
        "enemy_3": Enemy("enemy_3", 4, 4),
        "enemy_4": Enemy("enemy_4", 4, 0)
    }

    # Give enemy_1 low hp to heal, and armour to test unequpped priority
    players_d["enemy_1"].health = 80
    players_d["enemy_1"].armour = 5
    players_d["enemy_1"].equipment = [Armour("armour_2", 0, 4)]

    # Give enemy_4 sword to test random move
    players_d["enemy_4"].offense = 30
    players_d["enemy_4"].equipment = [Sword("sword_2", 4, 0)]
    players_d["enemy_4"].weapon = "sword_2"

    # Simulation 1
    enemy_turn("enemy_1", players_d, items_d) # Should move to apple_1 loc and heal
    enemy_turn("enemy_2", players_d, items_d) # Should attack hero and stay put, and not move to sword_1 loc as priority attack
    enemy_turn("enemy_3", players_d, items_d) # Should randomly move, but not out of bounds
    enemy_turn("enemy_4", players_d, items_d) # Should randomly move as sword already equipped, but not out of bounds

    assert players_d["enemy_1"].location == [1, 0]
    assert players_d["enemy_1"].health == 100
    assert players_d["enemy_2"].location == [1, 2]
    assert players_d["enemy_3"].location in [[3, 4], [4, 3]]
    assert players_d["enemy_4"].location in [[3, 0], [4, 1]]

    # Simulation 2
    enemy_turn("enemy_1", players_d, items_d) # Should move to sword_1 loc and equip, and not armour_1 loc as already equipped armour
    enemy_turn("enemy_2", players_d, items_d) # Should randomly attack either enemy_1 or hero and stay put
    enemy_turn("enemy_3", players_d, items_d) # Should move to armour_3 loc and equip

    assert players_d["enemy_1"].location == [1, 1]
    assert players_d["enemy_1"].offense == 30
    assert isinstance(players_d["enemy_1"].equipment[1], Sword)
    assert players_d["enemy_2"].location == [1, 2]
    assert players_d["enemy_3"].location == [3, 3]
    assert players_d["enemy_3"].armour == 5
    assert isinstance(players_d["enemy_3"].equipment[0], Armour)

    assert len(items_d) == 2 # items_d should only have armour_1 and sword_3
