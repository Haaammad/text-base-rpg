import os
import random
import time
import json
from rich.text import Text
from rich.console import Console
from rich.panel import Panel

# Character class
class Character:
    def __init__(self, name, strength, agility, intelligence, charisma, hp, defense):
        self.name = name
        self.strength = strength
        self.agility = agility
        self.intelligence = intelligence
        self.charisma = charisma
        self.hp = hp
        self.max_hp = hp
        self.defense = defense

    def attack(self, target):
        damage = max(0, self.strength - target.defense)
        target.hp -= damage
        return damage

# NPC class
class NPC(Character):
    def __init__(self, name, strength, agility, intelligence, charisma, hp, defense, description):
        super().__init__(name, strength, agility, intelligence, charisma, hp, defense)
        self.description = description

# Item class
class Item:
    def __init__(self, name, description):
        self.name = name
        self.description = description

# Room class
class Room:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.items = []
        self.npcs = []

    def add_item(self, item):
        self.items.append(item)

    def remove_item(self, item):
        if item in self.items:
            self.items.remove(item)

    def add_npc(self, npc):
        self.npcs.append(npc)

    def remove_npc(self, npc):
        if npc in self.npcs:
            self.npcs.remove(npc)

# Menu class
class Menu:
    def __init__(self, text, options, console):
        self.text = text
        self.options = options
        self.console = console

    def print_menu(self):
        self.console.print(Panel(self.text, expand=False), justify="center")

    def print_options(self):
        options_text = "\n".join([f"{key}. {value}" for key, value in self.options.items()])
        self.console.print(Panel(options_text, expand=True, style="white on blue"), justify="center")

    def choice(self):
        choice = input("Enter your choice: ")
        return int(choice) if choice.isdigit() else -1

# Encounter class
class Encounter:
    def __init__(self, name, description, options, results, console):
        self.name = name
        self.description = description
        self.options = options
        self.results = results
        self.console = console

    def play_encounter(self):
        self.console.print(Panel(f"{self.name}\n\n{self.description}", expand=True, style="white on blue"), justify="center")
        self.console.print(Panel("Choose an option:", expand=False, style="white on green"), justify="center")
        for key, option in self.options.items():
            self.console.print(f"{key}. {option}")

        choice = self.get_valid_choice()
        if choice != -1:
            results_text = "\n".join(self.results[choice])
            self.console.print(Panel(results_text, expand=True, style="white on red"), justify="center")
        else:
            self.console.print("Invalid choice.")

    def get_valid_choice(self):
        while True:
            choice = input("Enter your choice: ")
            if choice.isdigit() and int(choice) in self.options:
                return int(choice)
            else:
                self.console.print("Invalid choice. Please enter a valid option.")

# Function to create character
def create_character(rolls=3, save_folder="Characters/"):
    print("Welcome to the character creator! First things first, what's your hero's name?")
    name = input()
    attributes_accepted = False
    roll = 1

    while not attributes_accepted and roll <= rolls:
        attributes = {"strength": 0, "agility": 0, "intelligence": 0, "charisma": 0}
        index = 0
        for attribute in attributes:
            index += 1
            print(f"Let's roll some dice and find out {name}'s attributes {'.' * index}", end="\r")
            attributes[attribute] = random.randint(3, 10)
            time.sleep(0.5)

        attributes["hp"] = attributes["strength"] * 10
        attributes["defense"] = max(attributes["strength"], attributes["agility"]) + 5

        print("\nYour adventurer is ready! Their attributes are (from 3 to 10):")
        print(f"- Strength: {attributes['strength']}")
        print(f"- Agility: {attributes['agility']}")
        print(f"- Intelligence: {attributes['intelligence']}")
        print(f"- Charisma: {attributes['charisma']}\n")
        print(f"- HP (Strength * 10): {attributes['hp']}")
        print(f"- Defense (max(str/agi) + 5): {attributes['defense']}\n")

        if roll < rolls:
            choice = input(f"Would you like to roll again? You have {rolls - roll} more chance(s) (yes/no) \n").lower()
        elif roll == rolls:
            print("You're out of chances")
            choice = "no"

        if choice == "no":
            print("Very well, your character was created!")
            print("Returning to the starting menu...")

            attributes["name"] = name
            with open((save_folder + name + ".json"), mode="w") as f:
                json.dump(attributes, f, indent=4, ensure_ascii=False)

            time.sleep(3.0)
            attributes_accepted = True
        elif choice == "yes":
            roll += 1
        else:
            print("That's not a valid choice, try again...")
            time.sleep(2)

# Function to read character from file
def read_character(name):
    try:
        with open(("Characters/" + name + ".json"), mode="r") as f:
            attributes = json.load(f)

        character = Character(
            attributes["name"],
            attributes["strength"],
            attributes["agility"],
            attributes["intelligence"],
            attributes["charisma"],
            attributes["hp"],
            attributes["defense"],
        )
        return character
    except FileNotFoundError:
        print("Character file not found.")
        return None

# Function to read adventure from file
def read_adventure(adventure_file):
    try:
        with open(("Adventures/" + adventure_file + ".txt"), mode="r") as f:
            lines = f.readlines()
            lines = "".join(lines)
            lines = lines.split("*encounter*:")[1:]

        encounters = {}

        for encounter_index in range(len(lines)):
            encounter_raw = lines[encounter_index]

            encounter_name = encounter_raw.split("\n")[0]
            encounter_name = encounter_name.rstrip(" ").lstrip(" ")

            encounter_raw = "\n".join(encounter_raw.split("\n")[1:])

            encounter_description = encounter_raw.split("*options*")[0]
            encounter_description = encounter_description.rstrip("\n ")
            encounter_description = encounter_description.lstrip("\n ")

            encounter_options = encounter_raw.split("*options*")[1]
            encounter_options = encounter_options.rstrip("\n ")
            encounter_options = encounter_options.lstrip("\n ")
            encounter_options = encounter_options.split("*option*\n")[1:]

            options = []
            results = []

            for option_index in range(len(encounter_options)):
                option_raw = encounter_options[option_index]
                option = option_raw.split("*results*\n")[0]
                option = option.rstrip("\n ")
                option = option.lstrip("\n ")

                options.append(option)

                option_results = option_raw.split("*results*\n")[1]
                option_results = option_results.split("\n")
                try:
                    option_results.remove("")
                except ValueError:
                    option_results = option_results

                results.append(option_results)

            options = dict(enumerate(options))
            results = dict(enumerate(results))

            encounters[encounter_name] = Encounter(
                encounter_name,
                encounter_description,
                options,
                results,
                console,
            )

        return encounters
    except FileNotFoundError:
        print("Adventure file not found.")
        return None

# Function to choose character
def choose_character():
    try:
        character_list = [f.split(".")[0] for f in os.listdir("Characters") if f.endswith("json")]
        text = Text("Choose your character:", justify="center")
        options = dict(enumerate(character_list))

        character_menu = Menu(text, options, console)
        character_menu.print_menu()
        character_menu.print_options()
        choice = character_menu.choice()

        return character_list[choice] if choice != -1 else None
    except FileNotFoundError:
        print("Characters folder not found.")
        return None

# Function to choose adventure
def choose_adventure():
    try:
        adventure_list = [f.split(".")[0] for f in os.listdir("Adventures") if f.endswith("txt")]
        text = Text("Which adventure are you taking today?", justify="center")
        options = dict(enumerate(adventure_list))
        options[len(adventure_list)] = "Return"

        adventure_menu = Menu(text, options, console)
        adventure_menu.print_menu()
        adventure_menu.print_options()
        choice = adventure_menu.choice()

        if choice == (len(adventure_list)):
            initialize_game()
        else:
            character_name = choose_character()
            if character_name:
                adventure = read_adventure(adventure_list[choice])
                if adventure:
                    play_adventure(adventure, character_name)
    except FileNotFoundError:
        print("Adventures folder not found.")

# Function to play adventure
def play_adventure(adventure, character_name):
    character = read_character(character_name)
    if character:
        console.print(f"You have chosen {character.name} for the adventure.")
        for encounter_name, encounter in adventure.items():
            encounter.play_encounter()

# Initialize game
def initialize_game():
    try:
        print("Welcome to the Text-Based RPG!")
        print("What would you like to do?")
        print("1. Create Character")
        print("2. Choose Adventure")
        print("3. Quit")

        choice = input("Enter your choice: ")

        if choice == "1":
            create_character()
            initialize_game()
        elif choice == "2":
            choose_adventure()
        elif choice == "3":
            print("Goodbye!")
            quit()
        else:
            print("Invalid choice.")
            initialize_game()
    except KeyboardInterrupt:
        print("\nGame terminated.")

# Main function
def main():
    initialize_game()

# Run the game
if __name__ == "__main__":
    console = Console()
    main()
