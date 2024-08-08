import wx
import wx.adv
from dnd_GUI_dynamics import *
from dnd_init_class import initRaceClass as raceClass

class MyWizard(wx.adv.Wizard):
    def __init__(self):
        """Initialises instance variables and calls creation of static ordered pages"""
        super().__init__(parent=None, title="Character Creation Wizard")
        self.SetPageSize(wx.Size(500,400))
        self.CONSTANTS = Constants()
        self.GUI = GUIElements()
        self.create_base_pages()
        self.extra_pages = []
        self.page_2 = ''
        self.score_dict = {}
    
    def create_base_pages(self):
        """Creates statically ordered pages and binds events to page changes where data required to pull through"""
        self.l_page = LandingPage(self, self.GUI)
        self.c_page = ClassPage(self, self.GUI, self.CONSTANTS)
        self.f_page = FinalisePage(self, self.GUI, self.CONSTANTS)
        self.l_page.Chain(self.c_page)
        self.c_page.Chain(self.f_page)
        self.l_page.Bind(wx.adv.EVT_WIZARD_BEFORE_PAGE_CHANGED, self.on_next_page)
        self.c_page.Bind(wx.adv.EVT_WIZARD_PAGE_CHANGING, lambda event, parent=self.c_page, next_page=self.f_page, grid=self.f_page.f_grid: self.next_page_dict(event, parent, next_page, grid))
        self.c_page.Bind(wx.adv.EVT_WIZARD_BEFORE_PAGE_CHANGED, self.c_page.update_score_dict)
        self.f_page.Bind(wx.adv.EVT_WIZARD_PAGE_CHANGED, self.update_char_details)

    def on_next_page(self, event):
        """Used by l_page to decide either five e or pb page to chain and calls methods to handle that"""
        chosen = self.l_page.type_choose.GetSelection()
        if chosen == 0:
            event.Veto()
        elif chosen == 2:
            self.run_pb_page()
        else:
            self.run_eeeee_page()
    
    def run_pb_page(self):
        """Called to handle user moving to the pb page, creates pb page or sets it in order and binds page change for data pull through"""
        if 'pb_page' not in self.extra_pages:
            self.pb_page = PointsBuyPage(self, self.CONSTANTS, self.GUI)
            self.extra_pages.append('pb_page')
        if self.page_2 != 'pb_page':
            self.l_page.Chain(self.pb_page)
            self.pb_page.Chain(self.c_page)
            self.page_2 = 'pb_page'
            self.pb_page.Bind(wx.adv.EVT_WIZARD_BEFORE_PAGE_CHANGED, self.pb_page.on_page_change)
            self.pb_page.Bind(wx.adv.EVT_WIZARD_PAGE_CHANGING, lambda event, parent=self.pb_page, next_page=self.c_page, grid=self.c_page.c_grid: self.next_page_dict(event, parent, next_page, grid))

    def run_eeeee_page(self):
        """Called to handle user moving to five e page, creates eeeee page or sets it in order and binds page change for data pull through"""
        if 'eeeee_page' not in self.extra_pages:
            self.eeeee_page = Roll5ePage(self, self.CONSTANTS, self.GUI)
            self.extra_pages.append('eeeee_page')
        if self.page_2 != 'eeeee_page':
            self.l_page.Chain(self.eeeee_page)
            self.eeeee_page.Chain(self.c_page)
            self.page_2 = 'eeeee_page'
            self.eeeee_page.Bind(wx.adv.EVT_WIZARD_BEFORE_PAGE_CHANGED, self.on_move_from_eeeee)

    def on_move_from_eeeee(self, event):
        """Creates a_page and chains it after eeeee page, then to c_page, binds page change events for data pull through"""
        if hasattr(self.eeeee_page, 'score_totals'):
            self.score_totals = self.eeeee_page.score_totals
            self.a_page = AssignRollsPage(self, self.score_totals, self.CONSTANTS, self.GUI)
            self.eeeee_page.Chain(self.a_page)    
            self.a_page.Chain(self.c_page)
            self.a_page.Bind(wx.adv.EVT_WIZARD_BEFORE_PAGE_CHANGED, self.a_page.on_page_change)
            self.a_page.Bind(wx.adv.EVT_WIZARD_PAGE_CHANGING, lambda event, parent=self.a_page, next_page=self.c_page, grid=self.c_page.c_grid: self.next_page_dict(event, parent, next_page, grid))

        else:
            event.Veto()

    def next_page_dict(self, event, parent, next_page, grid):
        """Called on event when changing to c_page, pulls data for score_dict from previous page to next page and calls update_grid_data to update next page"""
        self.score_dict = parent.score_dict
        self.GUI.update_grid_data(self.score_dict, grid)
        next_page.score_dict = self.score_dict

    def update_char_details(self, event):
        """Updates the character details chosen on c_page and pulls through to f_page, calls update_char_details to update f_page"""
        self.f_page.character_dict = self.c_page.character_dict
        self.f_page.update_char_details()


class LandingPage(wx.adv.WizardPageSimple):
    def __init__(self, parent, GUI):
        """Initialises instance of GUI class and calls creation of page elements"""
        super().__init__(parent)
        self.GUI = GUI
        self.GUI.parent = self
        self.create_landing_page()

    def create_landing_page(self):
        """Creates the main sizer, calls creation of a title and subtitle and calls creation of choice button"""
        self.l_page_sizer = wx.BoxSizer(wx.VERTICAL)
        self.GUI.create_title_subtitle(self.l_page_sizer, "Welcome to the Character Creation Wizard!", 'Please select the ability score assignment method')
        self.choose_method_choice()
        self.SetSizer(self.l_page_sizer)

    def choose_method_choice(self):
        """Creates a choice widget to choose which method of stat rolling is desired"""
        self.type_choose = wx.Choice(self, choices=['Choose from dropdown', '5e: Roll 4d6 & remove lowest', 'Points Buy: Start at 8, buy points'])
        self.type_choose.Fit()
        self.l_page_sizer.Add(self.type_choose, 0, wx.ALIGN_CENTRE, 5)
        self.l_page_sizer.AddSpacer(30)


class Roll5ePage(wx.adv.WizardPageSimple):
    def __init__(self, parent, CONSTANTS, GUI):
        """Initialises instances of classes, and instance variables, calls creation of page elements"""
        super().__init__(parent)
        self.rollDice = RollDice()
        self.GUI = GUI
        self.GUI.parent = self
        self.CONSTANTS = CONSTANTS
        self.rolls = 0
        self.roll_flag = False
        self.create_5e_page()
    
    def create_5e_page(self):
        """Creates main page sizer, calls a title, subtitle, calls the creation of all page elements and sets the page sizer"""
        self.e_page_sizer = wx.BoxSizer(wx.VERTICAL)
        self.GUI.create_title_subtitle(self.e_page_sizer, "Lets roll your stats!", 'Your rolls so far')
        self.create_score_holder()
        self.create_dice_roller()
        self.roll_button()
        self.SetSizer(self.e_page_sizer)

    def create_score_holder(self):
        """Creates a grid sizer and adds blank placeholders"""
        self.score_grid = wx.GridSizer(1, 6, 50, 80)
        for i in range(6):
            point = wx.StaticText(self, label="")
            point.Font = self.CONSTANTS.FEATURE_FONT
            self.score_grid.Add(point)
        self.e_page_sizer.Add(self.score_grid, 0, wx.ALIGN_CENTRE, 5)
        self.e_page_sizer.AddSpacer(70)

    def create_dice_roller(self):
        """Creates a grid sizer with a subtitle above, populates grid with placeholders (6)"""
        subtitle = wx.StaticText(self, label='Your dice')
        subtitle.Font = self.CONSTANTS.SUB_FONT
        self.e_page_sizer.Add(subtitle, 0, wx.ALIGN_CENTRE, 5)
        self.e_page_sizer.AddSpacer(20)
        self.dice_grid = wx.GridSizer(1, 4, 60, 80)
        for _ in range(4):
            placeholder = wx.StaticText(self, label="6", style=wx.ALIGN_CENTRE)
            placeholder.SetMinSize(wx.Size(30, 30))
            placeholder.Font = self.CONSTANTS.FEATURE_FONT
            self.dice_grid.Add(placeholder, 0, wx.ALIGN_CENTRE, 10)
        self.e_page_sizer.Add(self.dice_grid, 0, wx.ALIGN_CENTRE, 5)
        self.e_page_sizer.AddSpacer(40)
    
    def roll_button(self):
        """Creates the roll button and binds it to the event handler roll_dice"""
        self.action_button = wx.Button(self, label='ROLL!', size=(wx.Size(100,70)))
        self.action_button.SetFont(self.CONSTANTS.FEATURE_FONT)
        self.action_button.Bind(wx.EVT_BUTTON, self.roll_dice)
        self.e_page_sizer.Add(self.action_button, 0, wx.ALIGN_CENTRE, 5)
        self.e_page_sizer.AddSpacer(10)
    
    def roll_dice(self, event):
        """Calls initialise_dice if no dice scores have been rolled yet, updates dice_grid with roll values, sets background colour and calls update_scores up to 6 times"""
        if not self.roll_flag:
            self.initialise_dice()
        if self.rolls < 6: # likely made redundant due to button being disabled after 6
            select = 0
            for i, item in enumerate(self.dice_grid.GetChildren()):
                mini = min(self.dice_rolled[self.rolls])
                roll = self.dice_rolled[self.rolls][i]
                widget = item.GetWindow()
                widget.SetLabel(str(roll))
                if roll == mini and not select:
                    select += 1
                    widget.SetBackgroundColour(wx.Colour(wx.NullColour))
                else:
                    widget.SetBackgroundColour(wx.Colour(wx.GREEN))
            self.update_scores()

    def update_scores(self):
        """Updates the score_grid with values from the roll_dice initialisation, updates roll counter and disables button after 6 rolls"""
        score_wid = self.score_grid.GetChildren()[self.rolls].GetWindow()
        score_wid.SetLabel(self.score_totals[self.rolls])
        self.rolls += 1
        if self.rolls == 6:
            self.action_button.Disable()
    
    def initialise_dice(self):
        """Calls roll_5e and sets instance variables to the return values to hold dice scores, flags itself as having run"""
        self.score_totals, self.score_dice, self.dice_rolled = self.rollDice.roll_5e()
        self.roll_flag = True


class AssignRollsPage(wx.adv.WizardPageSimple):
    def __init__(self, parent, score_totals, CONSTANTS, GUI):
        """Initialises instance classes and instance variables, calls creation of page elements"""
        super().__init__(parent)
        self.CONSTANTS = CONSTANTS
        self.GUI = GUI
        self.GUI.parent = self
        self.score_totals = score_totals
        self.score_dict = {}
        self.choice_list = []
        self.values_list = []
        self.remaining_list = []
        self.create_assign_page()

    def create_assign_page(self):
        """Creates main page sizer, title, subtitle, calls creation of ability grid and remaining scores, sets page sizer"""
        self.a_page_sizer = wx.BoxSizer(wx.VERTICAL)
        self.GUI.create_title_subtitle(self.a_page_sizer, 'Time to assign you rolls to abilities', 'Your abilities')
        self.create_ability_grid()
        self.create_remaining_scores()
        self.SetSizer(self.a_page_sizer)

    def create_ability_grid(self):
        """Creates grid sizer with ability names inserted in the top row, calls the ability choice widgets creation in each loop"""
        self.a_ability_grid = wx.GridSizer(2, 6, 30, 30)
        for i, ability in enumerate(reversed(self.CONSTANTS.ABILITY_NAMES)):
            text = wx.StaticText(self, label=ability)
            text.Font = self.CONSTANTS.SUB_FONT
            self.a_ability_grid.Insert(0, text, 0, wx.ALIGN_CENTRE)
            self.create_ability_choice(i)
        self.a_page_sizer.Add(self.a_ability_grid, 0, wx.ALIGN_CENTRE)
        self.a_page_sizer.AddSpacer(80)

    def create_ability_choice(self, index):
        """Creates a choice widget with the score_totals as the choices and label as the index of the column, inserts into ability_grid after ability names, populates choice and values list and binds each choice to on_choice_made"""
        choice = wx.Choice(self, choices=[roll for roll in self.score_totals])
        choice.Label = self.score_totals[5-index]
        choice.Bind(wx.EVT_CHOICE, self.on_choice_made)
        self.choice_list.insert(0, choice)
        self.values_list.append(self.score_totals[index])
        self.a_ability_grid.Insert(index+1, choice, 0, wx.ALIGN_CENTRE)

    def create_remaining_scores(self):
        """Creates a grid sizer populated with values from score_totals, calls them to be formatted, adds each one to a list"""
        self.a_remaining_grid = wx.GridSizer(6, 10, 40)
        for roll in self.score_totals:
            text = wx.StaticText(self, label=roll, style=wx.ALIGN_CENTRE)
            self.format_remaining_scores(text)
            self.remaining_list.append(text)
            self.a_remaining_grid.Add(text, 0, wx.ALIGN_CENTRE, 10)
        self.a_page_sizer.Add(self.a_remaining_grid, 0, wx.ALIGN_CENTRE)

    def format_remaining_scores(self, text):
        """Formats the text in the remaining grid, initialising their backgrounds at green"""
        text.Font = self.CONSTANTS.FEATURE_FONT
        text.SetMinSize(wx.Size(30,30)) 
        text.SetBackgroundColour(wx.Colour(wx.GREEN))

    def on_choice_made(self, event):
        """Calls the on_choice_made logic to update the values and colours from GUI module"""
        choice_obj = event.GetEventObject()
        self.GUI.on_choice_made(choice_obj, self.values_list, self.choice_list, self.remaining_list, self.score_totals)

    def on_page_change(self, event):
        """Prevents change if not all values selected, populates score_dict with the ability names and scores"""
        if sorted(self.values_list) != sorted(self.score_totals):
            event.Veto()
        else:
            for i, score in enumerate(self.values_list):
                ability = self.CONSTANTS.ABILITY_NAMES[i]
                self.score_dict[ability] = score
            event.Skip()


class PointsBuyPage(wx.adv.WizardPageSimple):
    def __init__(self, parent, CONSTANTS, GUI):
        """Initialises classes and variables, calls creation of page elements"""
        super().__init__(parent)
        self.GUI = GUI
        self.GUI.parent = self
        self.CONSTANTS = CONSTANTS
        self.score_dict = {}
        self.spin_buttons = []
        self.ability_windows = []
        self.cost_windows = []
        self.points_available = self.CONSTANTS.POINTS_AVAILABLE_MAX
        self.create_PB_page()   

    def create_PB_page(self):
        """Creates main page sizer, title, subtitle, calls creation of page elements, binds the page change to on_page_change and sets the main page sizer"""
        self.pb_page_sizer = wx.BoxSizer(wx.VERTICAL)
        self.GUI.create_title_subtitle(self.pb_page_sizer, 'Time to assign your scores!', 'Your abilities')
        self.create_ability_grid()
        self.create_available_point()
        self.create_reset_button()
        self.Bind(wx.adv.EVT_WIZARD_BEFORE_PAGE_CHANGED, self.on_page_change)
        self.SetSizer(self.pb_page_sizer)

    def create_ability_grid(self):
        """Creates a grid sizer and populates with ability names inserted at 0, calls creation of ability scores windows and cost spin windows, populates the cost_windows list"""
        self.ability_grid = wx.GridSizer(3, 6, 15, 30)
        for i, ability in enumerate(reversed(self.CONSTANTS.ABILITY_NAMES)):
            text = wx.StaticText(self, label=ability)
            text.Font = self.CONSTANTS.SUB_FONT
            self.ability_grid.Insert(0, text, 0, wx.ALIGN_CENTRE)
            self.ability_windows.insert(0, self.GUI.populate_ability_scores(self.ability_grid, i, str(self.CONSTANTS.MIN_POINTS)))
            self.cost_windows.append(self.GUI.populate_cost_spin(self.ability_grid, self.create_spin_button()))
        self.pb_page_sizer.Add(self.ability_grid, 0, wx.ALIGN_CENTRE)
        self.pb_page_sizer.AddSpacer(30)

    def create_spin_button(self): 
        """Creates a spin widget and binds to on_spin, appends the widget to spin_buttons list, returns the spin button"""
        ctrl_spin = wx.SpinButton(self)
        ctrl_spin.Bind(wx.EVT_SPIN, self.on_spin)
        ctrl_spin.SetRange(self.CONSTANTS.MIN_POINTS, self.CONSTANTS.MAX_POINTS)
        self.spin_buttons.append(ctrl_spin)
        return ctrl_spin
    
    def on_spin(self, event):
        """Calls on_spin in GUI module to alter the points_available variable"""
        self.points_available = self.GUI.on_spin(event, self.spin_buttons, self.ability_windows, self.cost_windows, self.points_available, self.remaining_text)
        
    def create_available_point(self):
        """Creates the remaining available points counter and initialises to POINTS_AVAILABLE_MAX"""
        text = wx.StaticText(self, label='Remaining points')
        text.Font = self.CONSTANTS.SUB_FONT
        self.pb_page_sizer.Add(text, 0, wx.ALIGN_CENTRE)
        self.pb_page_sizer.AddSpacer(10)
        self.remaining_text = wx.StaticText(self, label=str(self.CONSTANTS.POINTS_AVAILABLE_MAX))
        self.remaining_text.Font = self.CONSTANTS.FEATURE_FONT
        self.pb_page_sizer.Add(self.remaining_text, 0, wx.ALIGN_CENTRE)
        self.pb_page_sizer.AddSpacer(10)
    
    def create_reset_button(self):
        """Creates reset button and binds event handler on_reset"""
        button = wx.Button(self, label='Reset')
        button.Font = self.CONSTANTS.SUB_FONT
        button.Fit()
        button.Bind(wx.EVT_BUTTON, self.on_reset)
        self.pb_page_sizer.Add(button, 0, wx.ALIGN_CENTRE)

    def on_reset(self, event):
        """Iterates through ability windows list and sets value to minimum, through cost spin windows for the same, and calls update_points_available to do so"""
        for i in range(6):
            ability_window  = self.ability_windows[i]
            ability_window.SetLabel(str(self.CONSTANTS.MIN_POINTS))
            spinner = self.spin_buttons[i]
            spinner.SetValue(self.CONSTANTS.MIN_POINTS)
            cost = self.cost_windows[i]
            if cost.GetLabel() == str(self.CONSTANTS.HIGH_COST):
                cost.SetLabel(str(self.CONSTANTS.LOW_COST))
        self.points_available = self.CONSTANTS.POINTS_AVAILABLE_MAX
        self.GUI.update_points_available(self.remaining_text, self.points_available)
        self.Layout()
    
    def on_page_change(self, event):
        """Cancels page change if points_available isn't 0, or iterates through values of spin_buttons to set score_dict with the chosen scores"""
        if self.points_available != 0:
            event.Veto()
        else:
            for i, spinner in enumerate(self.spin_buttons):
                score = spinner.GetValue()
                self.score_dict[self.CONSTANTS.ABILITY_NAMES[i]] = str(score)
            event.Skip()
    

class ClassPage(wx.adv.WizardPageSimple):
    def __init__(self, parent, GUI, CONSTANTS):
        """Initialises classes and instance variables, calls creation of page elements"""
        super().__init__(parent)
        self.GUI = GUI
        self.GUI.parent = self
        self.grid_window_list = []
        self.ability_modified = []
        self.class_abilities = []
        self.score_dict = {}
        self.character_dict = {}
        self.CONSTANTS = CONSTANTS
        self.RaceClass = raceClass('/Users/homefolder/VSCode/DnD/Data/Class_Race.txt', 1, 'Race\n')
        self.create_c_page()   

    def create_c_page(self):
        """Creates main page sizer, title, subtitle, page elements, and initialises HalfElfElements, sets main page sizer"""
        self.c_page_sizer = wx.BoxSizer(wx.VERTICAL)
        self.GUI.create_title_subtitle(self.c_page_sizer, 'Now we can set your class and race', 'Your ability stats so far')
        self.create_ability_grid()
        self.create_choice_layout()
        self.HalfElf = HalfElfElements(self, self.grid_window_list, self.c_page_sizer, self.CONSTANTS)
        self.SetSizer(self.c_page_sizer)

    def create_ability_grid(self):
        """Creates grid sizer an populates with placeholders, populates grid_window_list with windows"""
        self.c_grid = wx.GridSizer(3, 6, 30, 30)
        for _ in range(18):
            text = wx.StaticText(self, label='+0')
            text.Font = self.CONSTANTS.SUB_FONT
            self.c_grid.Add(text, 0, wx.ALIGN_CENTRE, 0)
            self.grid_window_list.append(text)
        self.c_page_sizer.Add(self.c_grid, 0, wx.ALIGN_CENTRE)
        self.c_page_sizer.AddSpacer(50)

    def create_choice_layout(self):
        """Creates box sizer, calls creation of class and race choice"""
        self.c_choice_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.create_class_choice()
        self.c_choice_sizer.AddSpacer(20)
        self.create_race_choice()
        self.c_page_sizer.Add(self.c_choice_sizer, 0, wx.ALIGN_CENTRE)
        self.c_page_sizer.AddSpacer(30)

    def create_class_choice(self):
        """Creates the class choice widget and binds on_class_choice from GUI module"""
        self.class_choice = wx.Choice(self, choices = list(self.RaceClass.class_dict.keys()))
        self.c_choice_sizer.Add(self.class_choice, 0, wx.ALIGN_CENTRE)
        self.class_choice.Bind(wx.EVT_CHOICE, lambda event, grid_list=self.grid_window_list[:6], class_dict=self.RaceClass.class_dict: self.GUI.on_class_choice(event, grid_list, class_dict))

    def create_race_choice(self):
        """Creates the race choice widget and binds on_race_choice"""
        self.race_choice = wx.Choice(self, choices = list(self.RaceClass.race_dict.keys()))
        self.c_choice_sizer.Add(self.race_choice, 0, wx.ALIGN_CENTRE)
        self.race_choice.Bind(wx.EVT_CHOICE, self.on_race_choice)

    def on_race_choice(self, event):
        """Calls race_value_logic from GUI and checks for Half-Elf to run haelf module functionality"""
        selection = event.GetString()
        score_modifier = self.RaceClass.race_dict[selection]
        self.ability_modified = list(score_modifier.keys())
        self.GUI.race_value_logic(self.ability_modified, score_modifier, self.grid_window_list)
        if selection == 'Half-Elf':
            self.HalfElf.haelf_selection_on()
        elif self.HalfElf.haelf_show:
            self.HalfElf.haelf_show_hide(False)

    def update_score_dict(self, event):
        """Called from page change, vetoes if no modifier is altered (no race chosen), otherwise populates score_dict and character_dict"""
        proceed = False
        for mod in self.grid_window_list[self.CONSTANTS.MODIFIER_INDEX:]:
            if mod.GetLabel() != '+0':
                proceed = True
                break
        if proceed:
            for i in range(6):
                self.score_dict[self.grid_window_list[i].GetLabel()] = self.grid_window_list[i+self.CONSTANTS.SCORE_INDEX].GetLabel()
            char_details = ['Class', 'Race']
            for i, window in enumerate([self.class_choice, self.race_choice]):
                self.character_dict[char_details[i]] = window.GetString(window.GetSelection())
        else:
            event.Veto()


class FinalisePage(wx.adv.WizardPageSimple):
    def __init__(self, parent, GUI, CONSTANTS):
        """Initialises class instance and instance variables, calls page elements' creation"""
        super().__init__(parent)
        self.GUI = GUI
        self.GUI.parent = self
        self.CONSTANTS = CONSTANTS
        self.char_detail_list = []
        self.score_dict = {}
        self.character_dict = {}
        self.modifier_dict = {}
        self.create_f_page()   

    def create_f_page(self):
        """Creates main sizer, title, subtitle, calls page elements' creation and sets page sizer"""
        self.f_page_sizer = wx.BoxSizer(wx.VERTICAL)
        self.GUI.create_title_subtitle(self.f_page_sizer, 'Congratulations! Time to save your character', 'Here are your ability stats')
        self.create_f_grid()
        self.create_char_details()
        self.create_confirm_button()
        self.SetSizer(self.f_page_sizer)

    def create_f_grid(self):
        """Creates grid sizer and populates with placeholders (1)"""
        self.f_grid = wx.GridSizer(2, 6, 30, 30)
        for _ in range(12):
            text = wx.StaticText(self, label='1')
            text.Font = self.CONSTANTS.SUB_FONT
            self.f_grid.Add(text, 0, wx.ALIGN_CENTRE)
        self.f_page_sizer.AddSpacer(20)
        self.f_page_sizer.Add(self.f_grid, 0, wx.ALIGN_CENTRE)
        self.f_page_sizer.AddSpacer(40)

    def create_char_details(self):
        """Creates sizer and populates with place holders (1), populates char_detail_list"""
        self.char_sizer = wx.BoxSizer(wx.VERTICAL)
        for i in range(2):
            text = wx.StaticText(self, label='1')
            text.Font = self.CONSTANTS.SUB_FONT
            if i == 0:
                self.char_sizer.AddSpacer(20)
            self.char_detail_list.append(text)
            self.char_sizer.Add(text, 1, wx.ALIGN_CENTRE)
        self.f_page_sizer.Add(self.char_sizer, 0, wx.ALIGN_CENTRE)
        self.f_page_sizer.AddSpacer(50)

    def update_char_details(self):
        """Called from MyWizard to update the char_sizer with variables from previous page"""
        for i, detail in enumerate(self.character_dict.keys()):
            self.char_detail_list[i].SetLabel(detail + ': ' + self.character_dict[detail])
        self.Layout()

    def create_confirm_button(self):
        """Creates a button and binds to on_confirm_button"""
        button = wx.Button(self, label='Confirm', size=(wx.Size(100,70)))
        button.Font = self.CONSTANTS.SUB_FONT
        button.Bind(wx.EVT_BUTTON, self.on_confirm_button)
        self.f_page_sizer.Add(button, 0, wx.ALIGN_CENTRE)

    def on_confirm_button(self, event):
        """Opens dialog to request (file) name, calls validate_name, sets modifier_dict values, sets file path, calls write_file to update the txt file with details, relays save complete and disables confirm button. If dialog cancelled, event is vetoed"""
        dialog = wx.TextEntryDialog(self, 'Enter character name here:', 'Character Name')
        if dialog.ShowModal() == wx.ID_OK:
            character_name = dialog.GetValue()
            character_name = self.validate_name(character_name)
            self.modifier_dict = {key : ((int(value)-10) // 2) for key, value in self.score_dict.items()}
            file_path = f'/Users/homefolder/VSCode/DnD/Data/{character_name}.txt' # Could edit to allow choosing file path
            self.write_file(file_path)
            wx.MessageBox(f'Character data saved successfully to {file_path}', 'Data Saved', wx.OK)
            button = event.GetEventObject()
            button.Disable()
        else:
            wx.MessageBox('Character data not saved', 'Data Not Saved', wx.OK | wx.ICON_INFORMATION)

    def write_file(self, file_path):
        """Creates a txt file in the path and updates with values from character_dict, score_dict and modifier_dict, one dict key/value per line"""
        with open(file_path, 'w') as file:
            file.write('Character Details\n')
            for key, value in self.character_dict.items():
                file.write(f'{key}: {value}\n')
            file.write('\n Ability Scores\n')
            for key, value in self.score_dict.items():
                file.write(f'{key}: {value}\n')
            file.write('\n Score Modifiers\n')
            for key, value in self.modifier_dict.items():
                file.write(f'{key}: {value}\n')
        
    def validate_name(self, character_name):
        """Validates characters in given name to be a letter, ', or space, replaces spaces with underscores"""
        for letter in character_name:
            if not (letter.isalpha() or letter == "'" or letter == ' '):
                character_name = 'please_rename_file'
        return character_name.replace(' ', '_')