from dnd_GUI_dynamics import RollDice

def class_race():
    print("It's time to choose your race & class.")
    char_class = input('Please choose your class.\n')
    char_race = input('Please choose your race.\n')
    return {'class' : char_class, 'race' : char_race}

def roll_style():
    roll_type = input('Enter 5e to follow 5e guidelines, PB for points buy:\n')
    while roll_type != '5e' and roll_type != 'PB':
            print('Enter valid input\n')
            roll_type = input('Enter 5e to follow 5e guidelines, PB for points buy:\n')
    return roll_type

def point_buy():
    buy_count = int(input('Enter the amount of points you wish to buy, or 0:\n'))
    return buy_count

def roll_dice(roll_type):
    calc = RollDice()
    if roll_type == '5e':
        score_totals, score_dice, dice_rolled = calc.roll_5e()
        return score_totals, score_dice, dice_rolled
    else:
        score_totals = calc.roll_PB()
        return score_totals
    
def assign_points(score_totals):
    print('Here are your score points: ' + str(score_totals))
    ability = {}
    for score in score_totals:
        while True:
            assigned = input('To which ability would you like to assign ' + str(score) + '? Enter E to restart.\n')
            if assigned == 'E':
                return assign_points(score_totals)
            elif assigned in ability:
                print('Ability already assigned')
            else:
                ability[assigned] = score
                break
    while True:
        confirmed = input('You have these ability stats: ' + str(ability) + '\n Would you like to confirm or try again (Y/N)?')
        if confirmed == 'Y':
            return ability
        elif confirmed == 'N':
            return assign_points(score_totals)
        else:
            print('Invalid input.')

def execute_mod():
    roll_type = roll_style()
    buy_count = point_buy()
    inp_dict = {}
    for name, item in locals().items():
        if name == 'inp_dict':
            continue
        inp_dict[name] = item
    score_totals, score_dice, dice_rolled = roll_dice(roll_type)
    rolls = {'score_totals' : score_totals, 'score_dice' : score_dice, 'dice_rolled' : dice_rolled}
    if roll_type == '5e':
        abilities = assign_points(rolls['score_totals'])
    else:
        for ability in ['Strength', 'Dexterity', 'Constitution', 'Intelligence', 'Wisdom', 'Charisma']:
            abilities[ability] = 8
    character = class_race()
    return inp_dict, rolls, abilities, character