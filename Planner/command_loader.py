import json


class CommandLoader:

    def __init__(self, file_name='commands.json'):
        """
        Constructor which opens file wth commands and parses it.
        :param file_name: str, optional(default='commands.json').
            Name of the json file with commands.
        """
        self._file_name = file_name
        with open(file_name, 'r', encoding='utf-8') as infile:
            self._parsed_json_commands = json.loads(infile.read())

    def __getitem__(self, item):
        """
        Add dict-like interface: loader[item]
        :param item: str.
            Command name in file.
        :return: int, float, str, dict, list, bool, None.
            Command with all parameters from file.
        """
        return self._parsed_json_commands[item]

    def load_command(self, command_name):
        return self[command_name]

    def save_command(self, command):
        # TODO: need to avoid rewriting all file but append at the end.
        self._parsed_json_commands[command['name']] = command
        with open(self._file_name, 'w', encoding='utf-8') as outfile:
            json.dump(self._parsed_json_commands, outfile)
