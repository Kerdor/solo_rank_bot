from dungeon.selector import choose_dungeon


def test_choose_strongest_dungeon_within_power():
    entries = [
        {"idx": 1, "name": "A", "rank": "B", "def": 1000},
        {"idx": 2, "name": "B", "rank": "A", "def": 2000},
        {"idx": 3, "name": "C", "rank": "S", "def": 3000},
    ]

    chosen, need_reset = choose_dungeon(entries, 2500, 3)

    assert chosen["idx"] == 2
    assert need_reset is False


def test_choose_reset_when_all_dungeons_are_too_strong():
    entries = [
        {"idx": 1, "name": "A", "rank": "B", "def": 3000},
        {"idx": 2, "name": "B", "rank": "A", "def": 4000},
    ]

    chosen, need_reset = choose_dungeon(entries, 2500, 2)

    assert chosen is None
    assert need_reset is True


def test_choose_weakest_when_no_resets_left():
    entries = [
        {"idx": 1, "name": "A", "rank": "B", "def": 3000},
        {"idx": 2, "name": "B", "rank": "A", "def": 4000},
    ]

    chosen, need_reset = choose_dungeon(entries, 2500, 0)

    assert chosen["idx"] == 1
    assert need_reset is False
