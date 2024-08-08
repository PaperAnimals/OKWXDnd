class initRaceClass():
    def __init__(self, file_path: str, lines_to_skip: int, split_point: str):
        self.txt_data = self.process_txt(file_path, lines_to_skip)
        self.class_section, self.race_section = self.create_sections(self.txt_data, split_point)
        self.class_dict, self.race_dict = self.create_dictionaries(self.class_section, self.race_section)

    def process_txt(self, file_path, lines_to_skip):
        """Processes a .txt file into a list, skipping a chosen amount of lines.
        
        Args:
            file_path (str): txt file to be processed.
            lines_to_skip (int): Amount of lines removed at output.
        
        Returns:
            list: List of lines in the txt file, not including the first x lines.
        """
        with open(file_path, 'r') as file:
            txt_data = file.readlines()
        return txt_data[lines_to_skip:]
    
    def create_sections(self, data, split_point):
        """Splits a string into two parts based on the split_point.

        Args:
            data: The list to split.
            split_point: Where to split it.

        Returns:
            tuple: Two lists created by splitting the input data.
        """
        divider = data.index(split_point)
        first_section, second_section = data[:divider], data[divider+1:]
        return first_section, second_section

    def create_dictionaries(self, class_data, race_data):
        """Runs functions to populate class and race dictionaries.
        
        Args:
            class_data (str): Data to be used in process_classes.
            race_data (str): Data to be used in process_races.
            
        Returns:
            tuple: Two dictionaries, one containing class and race data.
        """
        class_dict = self.process_classes(class_data)
        race_dict = self.process_races(race_data)
        return class_dict, race_dict
    
    def process_classes(self, class_data):
        """Processes the class data and returns the class dictionary.
        
        Args:
            class_data (str): Data holding information on classes.
        
        Returns:
            dict: Holding the class data where keys are classes and values are lists of ablities.
        """
        class_dict = {}
        for line in class_data:  
            if line.strip():      
                class_name, *abilities = map(str.strip, line.split('|'))      
                class_dict[class_name] = abilities
        return class_dict
    
    def process_races(self, race_data):
        """Processes the race data and returns the race dictionary.
        
        Args:
            race_data (str): Data holding information on races.
            
        Returns:
            dict: Holding the race data where keys are races and values are dicts of race traits and assiciiated points buff.
        """
        race_dict = {}
        for line in race_data:
            if line.strip():
                parts = line.split('|')
                race_name = parts[0].strip()
                ability_pairs = {}
                for i in range(1, len(parts), 2):
                    ability = parts[i].strip()
                    point_buff = int(parts[i+1].strip())
                    ability_pairs[ability] = point_buff
                race_dict[race_name] = ability_pairs
        return race_dict