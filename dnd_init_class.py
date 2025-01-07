import json

class initRaceClass():
    def __init__(self, file_path: str):
        self.data = self.process_json(file_path)
        self.class_dict = self.data.get("Classes", {})
        self.race_dict = self.data.get("Races", {})

    def process_json(self, file_path):
        """Processes a JSON file and returns the data.

        Args:
            file_path (str): JSON file to be processed.

        Returns:
            dict: Dictionary containing the parsed JSON data.
        """
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
