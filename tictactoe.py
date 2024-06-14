import random

game_is_on = True

desc = []


def reset_desc():
    base_list1 = [0, 0, 0]
    base_list2 = [0, 0, 0]
    base_list3 = [0, 0, 0]
    global desc
    desc = [base_list1, base_list2, base_list3]


pos_list = []


def reset_pos():
    pos_list.clear()
    x = [0, 1, 2]
    for y in x:
        for z in x:
            temp_list = [y, z]
            pos_list.append(temp_list)


reset_pos()
reset_desc()


current_move = ""

IMAGE_BASE = {
    0: ["0_B.png", "0_J.png", "0_P.png"],
    1: ["1_B.png", "1_J.png", "1_P.png"],
    2: ["2_B.png", "2_J.png", "2_P.png"],
    3: ["3_B.png", "3_J.png", "3_P.png"],
    4: ["4_B.png", "4_J.png", "4_P.png"],
    5: ["5_B.png", "5_J.png", "5_P.png"],
    6: ["6_B.png", "6_J.png", "6_P.png"],
    7: ["7_B.png", "7_J.png", "7_P.png"],
    8: ["8_B.png", "8_J.png", "8_P.png"],
}

POS_DICT = {0: [0, 0], 1: [0, 1], 2: [0, 2], 3: [1, 0], 4: [1, 1], 5: [1, 2], 6: [2, 0], 7: [2, 1], 8: [2, 2]}

blank_image = "assets/img/tictactoe_images/"
images_list = []


def player_move(pos: int):
    coordinates = POS_DICT[pos]
    remove_pos(coordinates)
    return make_move(coordinates, "a")


def computer_move():
        global current_move
        current_move = "Computer"
        pos = random.choice(pos_list)
        print(pos)
        remove_pos(pos)
        game_is_over = make_move(pos, "b")
        return list(POS_DICT.keys())[list(POS_DICT.values()).index(pos)], game_is_over


def show_desc():
    for el in desc:
        print(el)


def random_coord():
    print(random.randint(0, 2))


def remove_pos(pos: list):
    pos_list.remove(pos)


def make_move(coords: list, atrib: str):
    desc[coords[0]][coords[1]] = atrib
    show_desc()
    return win_checker()


def win_checker():
    # row checker
    for row in desc:
        if row[0] != 0:
            if row[0] == row[1] and row[0] == row[2]:
                print(f"End game with row{row}")
                game_over()
                return True
            else:
                print("keep plying")

    # column checker
    checking_int = 0
    for column in desc:
        if checking_int > 2:
            checking_int = 0
        if column[checking_int] != 0:
            if desc[0][checking_int] == desc[1][checking_int] and desc[0][checking_int] == desc[2][checking_int]:
                print(f"End game with column{checking_int}")
                game_over()
                return True
            else:
                print("keep plying")
        checking_int += 1
    # diagonal checker
    if desc[0][0] != 0:
        if desc[0][0] == desc[1][1] == desc[2][2]:
            print(f"End game with decreasing diagonal")
            game_over()
            return True
        elif desc[0][2] != 0:
            if desc[0][2] == desc[1][1] == desc[2][0]:
                print(f"End game with increasing diagona")
                game_over()
                return True


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


def restart_game():
    reset_pos()
    reset_desc()
    images_list.clear()
    image_ind = 0
    while image_ind < 9:
        images_list.append("" + blank_image + IMAGE_BASE[image_ind][0] + "")
        image_ind += 1
    return images_list


def change_image(pos: int, player: int, images: list):
    print(images_list)
    print(pos)
    print(player)
    images[pos] = "" + blank_image + IMAGE_BASE[pos][player] + ""
    print(images_list)
    return images

# game_engine()
