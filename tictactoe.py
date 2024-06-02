import random

game_is_on = True

base_list1 = [0, 0, 0]
base_list2 = [0, 0, 0]
base_list3 = [0, 0, 0]
desc = [base_list1, base_list2, base_list3]

x = [0, 1, 2]
pos_list = []
for y in x:
    for z in x:
        temp_list = [y, z]
        pos_list.append(temp_list)
print(pos_list)

current_move = ""


# print(x)
# temp_list = []
# for y in x:
#     print(y)
#
#     temp_list.append(y)
# for z in temp_list:
#     print(z)
#     print(z, y)


def player_move():
    if game_is_on:

        global current_move
        current_move = "Player"
        player_input = input("Where to put your X (a1, b3 example): ")
        coordinates = list(player_input)

        if coordinates[0] == "a":
            coordinates[0] = 0
        elif coordinates[0] == "b":
            coordinates[0] = 1
        elif coordinates[0] == "c":
            coordinates[0] = 2

        coordinates[1] = int(coordinates[1])
        print("Player put item to:")
        print(coordinates)
        remove_pos(coordinates)

        make_move(coordinates, "a")


def show_desc():
    print("Current deck:")
    for el in desc:
        print(el)


def random_coord():
    print(random.randint(0, 2))


def remove_pos(pos: list):
    pos_list.remove(pos)
    print(f"Positions left: {len(pos_list)}")
    print(pos_list)


def computer_move():
    if game_is_on:
        global current_move
        current_move = "Computer"
        pos = random.choice(pos_list)
        print("Computer  put item to:")
        print(pos)
        remove_pos(pos)

        make_move(pos, "b")


def make_move(coords: list, atrib: str):
    desc[coords[0]][coords[1]] = atrib
    show_desc()
    win_checker()


def win_checker():
    # row checker
    for row in desc:
        if row[0] != 0:
            if row[0] == row[1] and row[0] == row[2]:
                print(f"End game with row{row}")
                game_over()
                return 0
            else:
                print("keep plying")

    # column checker
    col_int = 0
    for column in desc:
        if column[0] != 0:
            if column[0] == desc[1][col_int] and column[0] == desc[2][col_int]:
                print(f"End game with column{col_int}")
                game_over()

                return 0
            else:
                print("keep plying")
        col_int += 1
    # diagonal checker
    if desc[0][0] != 0:
        if desc[0][0] == desc[1][1] == desc[2][2]:
            print(f"End game with decreasing diagonal")
            game_over()

            return 0
        elif desc[0][2] != 0:
            if desc[0][2] == desc[1][1] == desc[2][0]:
                print(f"End game with increasing diagona")
                game_over()

                return 0


def game_round():
    player_move()
    computer_move()


def game_engine():
    while game_is_on:
        game_round()
    print("Game Over")


def game_over():
    global game_is_on
    game_is_on = False
    print(f"{current_move} wins!")


game_engine()
