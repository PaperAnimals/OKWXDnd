from random import randint
import wx
import wx.adv


class GUIElements():
    """A class that contains methods for dynamic elements on the main GUI"""
    def __init__(self, parent:wx.adv.WizardPageSimple=None):
        self.parent = parent
        self.CONSTANTS = Constants()
        self.is_point_shown = 0

    def create_title_subtitle(self, sizer: wx.BoxSizer, title_label: str, sub_label: str) -> None:
        """
        Creates a title and subtitle as wx.StaticText and adds them to a wx.BoxSizer
        
        Args:
        sizer (wx.BoxSizer): sizer on the parent page that elements are added to
        title_label (str): text to be displayed as the title
        sub_label (str): text to be displayed below the title as the subtitle

        Returns:
        None
        """
        title = wx.StaticText(self.parent, label=title_label)
        title_font = wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        title.Font = title_font
        subtitle = wx.StaticText(self.parent, label=sub_label)
        sub_font = wx.Font(15, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        subtitle.Font = sub_font
        sizer.Add(title, 0, wx.ALIGN_TOP| wx.ALIGN_CENTRE, 10)
        sizer.AddSpacer(60)
        sizer.Add(subtitle, 0, wx.ALIGN_CENTRE | wx.BOTTOM, 5)
        sizer.AddSpacer(20)

    def populate_ability_scores(self, grid: wx.GridSizer, index: int, score_init: str) -> wx.StaticText: # PointsBuyPage
        """
        Populates the 2nd row of a wx.GridSizer with 8s.
        
        Args:
        grid (wx.GridSizer): sizer for the window to be entered into
        index (int): iterated index to find correct grid location.

        Returns:
        text (wx.StaticText): window to be appended to list of ability score windows
        """
        text = wx.StaticText(self.parent, label=score_init)
        text.Font = self.CONSTANTS.FEATURE_FONT
        grid.Insert(index + 1, text, 0, wx.ALIGN_CENTRE)
        return text

    def populate_cost_spin(self, grid: wx.GridSizer, spin_button: wx.SpinButton) -> wx.StaticText:
        """
        Populates the 3rd row of a wx.GridSizer with 1s and a wx.SpinButton
        
        Args:
        grid (wx.GridSizer): sizer for the window to be entered into
        spin_button (wx.SpinButton): button created in PointsBuyPage.create_spin_button() to be added to the window
        
        Returns:
        text (wx.StaticText): window containing cost display to be appended to list of cost number windows
        """
        ctrl_sizer = wx.BoxSizer(wx.HORIZONTAL)
        text = wx.StaticText(self.parent, label=str(self.CONSTANTS.LOW_COST))
        text.Font = self.CONSTANTS.SUB_FONT
        ctrl_sizer.Add(text, 0, wx.ALIGN_CENTRE)
        ctrl_sizer.AddSpacer(5)
        ctrl_sizer.Add(spin_button, 0, wx.ALIGN_CENTRE)
        grid.Add(ctrl_sizer, 0, wx.ALIGN_CENTRE)
        return text
    
    def on_spin(self, event, spin_buttons: list, ability_windows: list, cost_list: list, points_available: int, remaining_text: wx.StaticText) -> int:
        """
        An event handler for a spin button being pressed for the PointsBuyPage
        
        Args:
        event (wx.Event): sent as default by wxpython, holds the event information
        spin_buttons (list): containing spin_buttons, used for indexing other elements
        ability_windows (list): containing ability score windows, used to reach the window to be changed
        cost_list (list): containing cost number windows, used to reach cost number to be changed
        points_available (int): holds up-to-date count for updating remaining_text
        remaining_text (wx.StaticText): window that displays the points_available counter
        
        Returns:
        points_available (int): counter updated with increment to be stored in main module, or counter left as is 
        """
        spin_window = event.GetEventObject()
        col_index = spin_buttons.index(spin_window)
        ability_window = ability_windows[col_index]
        current_score = int(ability_window.GetLabel())
        new_score = spin_window.GetValue()
        if new_score == current_score or new_score > current_score and (points_available == 0 or (points_available == 1 and current_score >= self.CONSTANTS.COST_THRESHOLD)):
            spin_window.SetValue(current_score)
            return points_available
        else:
            increment = self.update_values_logic(current_score, new_score)
            points_available += increment 
            self.update_values(new_score, ability_window)
            self.update_points_available(remaining_text, points_available)
            self.update_cost(cost_list, col_index, new_score)
            self.parent.Layout()
            return points_available

    def update_values_logic(self, current_score: int, new_score: int) -> int:
        """
        Logic method to assign a value to increment variable to be used to update points_available for the PointsBuyPage
        
        Args:
        current_score (int): ability_window score before any changes made used for conditions, used for conditionals against new_score and COST_THRESHOLD
        new_score (int): value held by spin_button after button clicked, used for conditionals against current_score and COST_THRESHOLD
        
        Returns:
        increment (int): used to update the points_available variable, also to check if a change should be made to the display values
        """
        increment = 0
        if new_score > current_score:
            if current_score >= self.CONSTANTS.COST_THRESHOLD:
                increment = - self.CONSTANTS.HIGH_COST
            elif current_score < self.CONSTANTS.COST_THRESHOLD:
                increment = - self.CONSTANTS.LOW_COST
        else:
            if current_score > self.CONSTANTS.COST_THRESHOLD:
                increment = self.CONSTANTS.HIGH_COST
            else:
                increment = self.CONSTANTS.LOW_COST
        return increment

    def update_points_available(self, remaining_text: wx.StaticText, points_available: int) -> None:
        """
        Updates the display of the remaining_text window with the points_available variable
        
        Args:
        remaining_text (wx.StaticText): window displaying the previous points_available count, to be updated
        points_available (int): new points_available count to update the remaining_text window

        Returns:
        None
        """
        remaining_text.SetLabel(str(points_available))
    
    def update_values(self, new_score: int, ability_window: wx.StaticText) -> None:
        """
        Updates the score count displayed in ability_window with the new_score variable
        
        Args:
        new_score (int): value from spin_button that holds the updated score to be displayed
        ability_window (wx.StaticText): window displaying the current score, to be updated with the new_score

        Returns:
        None
        """
        ability_window.SetLabel(str(new_score))
    
    def update_cost(self, cost_list: list, col_index: int, new_score: int) -> None:
        """
        Updates the cost number in the indexed window from cost_list with high or low cost when passing the threshold
        
        Args:
        cost_list (list): contains the windows displaying cost numbers, to be indexed to reach required window
        col_index (int): index variable to find the correct window in the list, calculated by indexing the spin_button in on_spin
        new_score (int): score used for conditional to select high or low cost number to display based on the COST_THRESHOLD constant

        Returns:
        None
        """
        cost_text = cost_list[col_index]
        if new_score == self.CONSTANTS.COST_THRESHOLD: 
            cost_text.SetLabel(str(self.CONSTANTS.HIGH_COST))
        elif new_score == self.CONSTANTS.COST_THRESHOLD - 1:
            cost_text.SetLabel(str(self.CONSTANTS.LOW_COST))
    
    def on_choice_made(self, choice_obj: wx.Choice, values_list: list, choice_list: list, remaining_list: list, score_totals: list) ->  None: # AssignRollsPage
        """
        A method that activates on a bind for a wx.Choice element, changing other elements of the page for the AssignRollsPage
        
        Args:
        choice_obj (wx.Choice): taken from the triggered event object and used to index other variables
        values_list (list): previous values that had been selected across all wx.Choice objects, updated with the new_selection here
        choice_list (list): wx.Choice objects on the page, used to index along with choice_obj to alter other variables
        remaining_list (list): wx.StaticText objects, initialised as an instance variable for helper functions
        score_totals (list): values from the remaining_list windows, initialised here for helper function

        Returns:
        None
        """
        self.score_totals = score_totals
        self.values_list = values_list
        self.remaining_list = remaining_list
        new_selection = choice_obj.GetString(choice_obj.GetSelection())
        old_list = values_list.copy()
        self.values_list[choice_list.index(choice_obj)] = new_selection
        self.alter_colour_logic_loop(old_list)

    def alter_colour_logic_loop(self, old_list: list) -> None:
        """
        A for loop iterating over remaining_list that initialises the required variables for the conditionals that follow in the next helper and breaks when the conditionals are finished
        
        Args:
        old_list (list): previous values selected across wx.Choice elements, used to get a count of the item label in the previous selection
        
        Returns:
        None
        """
        self.count_to_green = 0
        self.count_to_red = 0
        for item in self.remaining_list:
            label = item.GetLabel()
            colour = item.GetBackgroundColour()
            old_count = old_list.count(label)
            new_count = self.values_list.count(label)
            self.alter_colour_logic_condition(old_count, new_count, label, item, colour)
            if self.count_to_green == 1 and self.count_to_red == 1:
                break
        
    def alter_colour_logic_condition(self, old_count: int, new_count: int, label: str, item: wx.StaticText, colour: wx.Colour) -> None:
        """
        The conditional section of the for loop in the previous method, using if statements, it checks whether the count of the iterated item is lower or higher than before and that none have been changed based on the same conditions

        Args:
        old_count (int): count of the current item's label within the previous selection of wx.Choice objects, used for conditional comparison
        new_count (int): count of the current item's label within the new selection of wx.Choice objects, used for conditional comparison
        label (str): value shown by the iterated item, used for counting in self.score_totals in order to create comparison 
        item (wx.StaticText): current iterated object, updated in background colour when conditionals met
        colour (wx.Colour): current background colour of item, used for conditional to prevent changing a colour to the same colour as before

        Returns:
        None
        """
        if self.count_to_green == 0 and colour != wx.GREEN and old_count < new_count:
            item.SetBackgroundColour(wx.GREEN)
            self.count_to_green = 1
        elif self.count_to_red == 0 and colour != wx.RED and old_count > new_count and new_count < self.score_totals.count(label):
            item.SetBackgroundColour(wx.RED)
            self.count_to_red = 1

    def update_grid_data(self, score_dict: dict, sizer: wx.GridSizer) -> None: # ClassPage
        """
        When the page is changed to the ClassPage, this method updates the page's grid sizer with data from the score_dict taken from the previous page
        
        Args:
        score_dict (dict): keys are the ability name and values are their score determined in the last page, used to create a list to be iterated over for the labels
        sizer (wx.GridSizer): the sizer which is to be updated, each child's window has a new label set related to ability names and scores
        
        Returns:
        None
        """
        abilities = self.CONSTANTS.ABILITY_NAMES
        scores = list(score_dict.values())
        combined = abilities + scores
        children = sizer.GetChildren()
        for i in range(12):
            children[i].GetWindow().SetLabel(combined[i])
        self.score_dict = score_dict

    def on_class_choice(self, event: wx.Event, grid_list: list, class_dict: dict) -> None:
        """
        Called when the class spinner event is activated, changes the background colour to null if not relevant and green if relevant to the class
        
        Args:
        event (wx.Event): automatically called by the choice object bind, used to retrieve selected value by matching value to key in class dict
        grid_list (list): wx.StaticText windows that are to be updated in background colour
        class_dict (dict): contains the ability information for each class, used to identify relevant abilities

        Returns:
        None
        """
        selection = event.GetString()
        class_abilities = class_dict[selection]
        for ability in grid_list:
            abi_label = ability.GetLabel()
            if abi_label in class_abilities and ability.GetBackgroundColour() != wx.GREEN:
                ability.SetBackgroundColour(wx.GREEN)
            elif abi_label not in class_abilities and ability.GetBackgroundColour() == wx.GREEN:
                ability.SetBackgroundColour(wx.NullColour)
    
    def race_value_logic(self, ability_modified: list, score_modifier: dict, grid_list: list) -> None:
        """
        Called after the race choice event is called, handles logic for updating the windows in grid_list with new information based on the choice value selected
        
        Args:
        ability_modified (list): list of keys from score_modifier used to compare the str to the ability in ABILITY_NAMES to check if an action is required or not
        score_modifier (dict): generated by extracting the value using the race choice event object's data as the key in race_dict, the keys match abilities in ability_modified to obtain the value information to update the windows
        grid_list (list): contains windows in a grid to be updated by the update_window_label method

        Returns:
        None
        """
        for i, ability in enumerate(self.CONSTANTS.ABILITY_NAMES):
            if ability in ability_modified:
                new_score = str(int(self.score_dict[ability]) + score_modifier[ability])
                modifier = '+' + str(score_modifier[ability])
                self.update_window_label(grid_list, i, new_score, modifier)
            elif grid_list[i + self.CONSTANTS.SCORE_INDEX].GetLabel() != self.score_dict[ability]:
                self.update_window_label(grid_list, i, self.score_dict[ability], '+0')

    def update_window_label(self, grid_list: list, i: int, score: str, modifier: str) -> None:
        """
        Updates the labels of the windows in grid_list to be in line with the new values provided by the race_value_logic method
        
        Args:
        grid_list (list): windows in a grid that are to have their labels updated based on indexing and updated to values from race_value_logic
        i (int): iterable index from the enumerate call in the loop in race_value_logic, used to index which column the window is in
        score (str): value to update the label for the selected score window indexed by SCORE_INDEX, created by race_value_logic
        modifier (str): value to update the label for the selected score window indexed by MODIFIER_INDEX, created by race_value_logic

        Returns:
        None
        """
        grid_list[i + self.CONSTANTS.SCORE_INDEX].SetLabel(score)
        grid_list[i + self.CONSTANTS.MODIFIER_INDEX].SetLabel(modifier)


class RollDice(): #Roll5ePage
    """A class that simulates rolling dice and selecting scores based on 5e rules"""
    def __init__(self):
        self.dice_rolled = []
        self.score_dice = []
        self.score_totals = []

    def roll_5e(self) -> tuple:
        """
        Simulates rolling 4d6 6 times and removing the lowest, populates the Roll5ePage in the main GUI
        
        Returns:
        self.score_totals (list): holds the sum of each list in self.score_dice, used to populate a grid sizer with the scores
        self.score_dice (list): 6 lists holding 3 ints each, generated by removing the lowest from self.dice_rolled, used to identify which rolls are kept from each iteration and to generate self.score_totals
        self.dice_rolled (list): 6 lists of 4 ints each, random numbers populate each list in order, used to populate dice rolled display and to generate self.score_dice by removing the min
        """
        for roll in range(6):
            rolls = [randint(1, 6) for _ in range(4)]
            min_dice = min(rolls)
            self.dice_rolled.append(rolls.copy())
            rolls.remove(min_dice)
            self.score_dice.append(rolls.copy())
        self.total_dice()
        return self.score_totals, self.score_dice, self.dice_rolled
    
    def total_dice(self) -> None: # Can probably move into roll_5e
        """Sums the dice from each list within self.score_dice, appends each total to self.score_totals used in the roll_5e method"""
        for rolls in self.score_dice:
            self.score_totals.append(str(sum(rolls)))


class HalfElfElements():
    """Handles the elements required when the Half-Elf race is selected on ClassPage's race choice widget"""
    def __init__(self, parent: wx.adv.WizardPageSimple, grid_window_list: list, c_page_sizer: wx.BoxSizer, constants_class: 'Constants') -> None:
        self.haelf_flag = 1
        self.haelf_show = 0
        self.parent = parent
        self.grid_window_list = grid_window_list
        self.c_page_sizer = c_page_sizer
        self.CONSTANTS = constants_class

    def haelf_selection_on(self) -> None:
        """
        When Half-Elf is selected on the race choice widget on ClassPage, checks if the Half-Elf choice widgets have been created or not and either calls their creation or calls them to be shown
        
        Args:
        None
        
        Returns:
        None
        """
        if self.haelf_flag:
            self.create_halfelf_choice()
        else:
            self.haelf_show_hide(True)
    
    def haelf_show_hide(self, show: bool) -> None:
        """
        Shows or hides the Half-Elf choice widgets based on the show bool, also resets the haelf_select to its default value to match the values in the GUI

        Args:
        show (bool): True when they are to be shown, False to hide them, decided in logic based on wheether Half-Elf has been selected or not

        Returns:
        None
        """
        for child in self.halfelf_sizer:
            if child.IsWindow():
                child.GetWindow().Show(show)
                if show:
                    child.GetWindow().SetSelection(0)
        if self.haelf_select != ['Strength'] * 2:
            self.haelf_select = ['Strength'] * 2
        self.haelf_show = show

    def create_halfelf_choice(self) -> None:
        """
        Creates the choice widgets that deal with the extra functionality required when Half-Elf is the selected race. Updates haelf_select to 2 * strength and haelf_choice to include the choice widgets
        
        Args:
        None
        
        Returns:
        None
        """
        self.haelf_flag = 0
        self.haelf_select = []
        self.haelf_choice = []
        self.halfelf_sizer = wx.BoxSizer(wx.HORIZONTAL)
        for i in range(2):
            choice = wx.Choice(self.parent, choices=self.CONSTANTS.ABILITY_NAMES)
            if i:
                self.halfelf_sizer.AddSpacer(10)
            self.halfelf_sizer.Add(choice, 0, wx.ALIGN_CENTRE, 20)
            choice.Bind(wx.EVT_CHOICE, self.on_halfelf_choice)
            self.haelf_choice.append(choice)
            self.haelf_select.append('Strength')
        self.c_page_sizer.Add(self.halfelf_sizer, 0, wx.ALIGN_CENTRE, 0)
        self.parent.Layout()
        self.haelf_show = 1
        
    def on_halfelf_choice(self, event: wx.Event) -> None:
        """
        Event handler for the created choice widgets that contains logic to decide which values to update by indexing ABILITY_NAMES and the index of the event object in haelf_choice using the event object
        
        Args:
        event (wx.Event): event object automatically generated by the Half-Elf choice widgets, used to get the current selection for indexing updates
        
        Returns:
        None"""
        selection = event.GetString()
        choice_index = self.haelf_choice.index(event.GetEventObject())
        if self.haelf_select[choice_index] != selection:
            index = self.CONSTANTS.ABILITY_NAMES.index(self.haelf_select[choice_index])
            self.haelf_update_values(index, - 1)
            self.haelf_select[choice_index] = selection 
            index = self.CONSTANTS.ABILITY_NAMES.index(selection)
            self.haelf_update_values(index, 1)
            self.ability_modified = ['Charisma'] + self.haelf_select 

    def haelf_update_values(self, index: int, value_mod: int) -> None:
        """
        Update the values of windows in grid_window_list based on indices from on_halfelf_choice and values calculated in method
        
        Args:
        index (int): index taken from on_halfelf_choice, used to determine the column to update
        value_mod (int): +/- 1 based on whether the window's value is to be lowered when deselected or increased when selected in the choice widget
        
        Returns:
        None
        """
        mod_window = self.grid_window_list[index + self.CONSTANTS.MODIFIER_INDEX]
        score_window = self.grid_window_list[index + self.CONSTANTS.SCORE_INDEX]
        for i, window in enumerate([mod_window, score_window]):
            current = int(window.GetLabel())
            new = str(current + value_mod)
            if i == 0:
                mod_update = '+' + new
                mod_window.SetLabel(mod_update)
            else:
                score_update = new
                score_window.SetLabel(score_update)

class Constants():
    """List of constants used in the main GUI"""
    def __init__(self):
        self.POINTS_AVAILABLE_MAX = 27
        self.COST_THRESHOLD = 13
        self.MAX_POINTS = 15
        self.MIN_POINTS = 8
        self.HIGH_COST = 2
        self.LOW_COST = 1
        self.SCORE_INDEX = 6
        self.MODIFIER_INDEX = 12
        self.ABILITY_NAMES = ['Strength', 'Dexterity', 'Constitution', 'Intelligence', 'Wisdom', 'Charisma']
        self.FEATURE_FONT = wx.Font(20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_MAX, wx.FONTWEIGHT_BOLD)
        self.SUB_FONT = wx.Font(15, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)


