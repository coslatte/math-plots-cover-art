from typing import Callable
from brain import Brain, GraphicableEntity
from functions import get_all_functions
from utils import Constants, State


class CLI:
    def __init__(self) -> None:
        self.brain = Brain()
        self.console_input_option = None

    def start(self) -> None:
        while True:
            print("==* Art Graph Generator *==")
            self.display_menu("main")

            self.console_input_option = self.input_option("Select an option: ")

            if self.console_input_option in ("g", "generate"):
                self.cls()
                self.display_menu("generation")
                self.repeat_until_success(self.manage_generation_settings)
                self.cls()

            elif self.console_input_option in ("s", "settings"):
                self.cls()
                self.display_menu("settings")
                self.repeat_until_success(self.manage_settings)

            elif self.console_input_option in ("e", "exit"):
                print("Exiting program.")
                break

            else:
                print("Invalid option. Please try again.")

    def manage_generation_settings(self) -> State:
        """Manages generation settings."""

        available_functions: list[Callable] = get_all_functions(ret_type=Callable)
        available_functions_names: list[str] = get_all_functions(ret_type=str)
        name_map = {str(i + 1): func for i, func in enumerate(available_functions_names)}
        """
        EXAMPLE:
            name_map = {
                "1": "Fractal",
                "2": "Binary Pattern",
            }
        """

        print(name_map)

        while True:
            choice = self.input_option("Select an option: ")
            if choice not in name_map:
                continue
            self.console_input_option = choice
            break

        index: str = self.console_input_option  # Numeric sequence representation, e.g: "1", "2", "3", etc.

        g = GraphicableEntity(
            name=name_map[index],
            func=available_functions[index],
            palette=Brain.random_palette(),
            output_dir=Brain.output_path,
        )

        try:
            if self.console_input_option in name_map:
                pass
            else:
                raise Exception("The selection is not available")

            if self.console_input_option in ("10", "r", "random"):
                import random

                random_choice = random.randint(1, len(name_map))

                name = name_map[random_choice]
                func = available_functions[random_choice]

                print(f"Random option selected: {name}")

                g.name = name
                g.func = func

            # WIP
            elif self.console_input_option in ("a", "all"):
                return State.SUCCESS
            # WIP
            elif self.console_input_option in ("c", "custom"):
                return State.SUCCESS
            # WIP
            elif self.console_input_option in ("t", "template"):
                return State.SUCCESS
            # WIP
            elif self.console_input_option in ("b", "back"):
                return State.SUCCESS
            else:
                return State.FAILURE

            g.render()

            return State.SUCCESS
        except Exception as e:
            print(f"Error during generation: {e}")

            return State.FAILURE

    def manage_settings(self) -> State:
        """Manage settings based on the selected option."""

        self.console_input_option = self.input_option()

        match self.console_input_option:
            case "is" | "image settings":
                self.cls()
                return self.repeat_until_success(self.manage_image_properties_settings)
            case "dir" | "directory":
                self.cls()
                return self.repeat_until_success(self.manage_dir_settings)
            case "b" | "back":
                self.cls()
                return State.SUCCESS
            case _:
                print("Invalid settings option. Please try again.")
                return State.FAILURE

    def manage_dir_settings(self) -> State:
        print(f"Current output path (absolute): '{Brain.output_path().absolute()}'")

        option = self.input_option("Set output folder path? (Y/n): ")
        if option in State.CONFIRMATION:
            Brain.output_path(self.input_option("Enter the output path: "))
            print(f"New path assigned to: {Brain.color_palette()}")

            return State.SUCCESS
        elif option in State.NEGATION:
            print(
                f"No changes made to the output path. Assigning default path (which is ' {Constants.DEFAULT_PATH.absolute}')"
            )
            Brain.output_path.setter(Constants.DEFAULT_PATH)
            print(f"Path assigned: {Brain.output_path()}")

            return State.SUCCESS

        return State.FAILURE

    def manage_image_properties_settings(self) -> None:
        """
        Manage image size settings.
        """

        print(f"Current image size: {Brain.img_size}")

        option = self.input_option("Set image size? (Y/n): ")
        width: int
        height: int
        if option in State.CONFIRMATION:
            console_in = self.input_option("Enter width (or both, like '1000x1000'): ")

            if len(console_in.split("x")) == 2:
                width, height = console_in[0], console_in[1]
            elif console_in:
                width = int(console_in)
                height = int(self.input_option("Enter height: "))
                Brain.img_size = (width, height)

                print(f"New image size set to: {Brain.img_size}")

                return State.SUCCESS
            else:
                print("???")

                return State.FAILURE

        elif option in State.NEGATION:
            print("No changes made to the image size.")

            return State.SUCCESS

    def display_menu(self, menu: str) -> None:
        """
        Display the menu options.
        """

        main_menu = {
            "g": "Generate art.",
            "s": "Settings",
            "e": "Exit.",
        }

        generation_menu = {
            "1": "Generate fractal.",
            "2": "Generate attractor.",
            "3": "Generate binary pattern.",
            "4": "Generate tensor field.",
            "5": "Generate Voronoi art.",
            "6": "Generate Bezier art.",
            "7": "Generate Julia set.",
            "8": "Generate Hilbert curve.",
            "9": "Generate Lissajous curve.",
            "10": "Generate random art.",
            "a": "Generate all art types.",
            "c": "Customize art.",
            "t": "Select template.",
            "b": "<- Go back.",
        }

        settings_menu = {
            "is": "Image properties configuration.",
            "dir": "Output directory configuration.",
            "b": "<- Go back.",
        }

        def display(options: dict) -> None:
            for k, v in options.items():
                print(f"* {k}: {v}")

        if menu == "main":
            display(main_menu)
        elif menu == "generation":
            display(generation_menu)
        elif menu == "settings":
            display(settings_menu)
        else:
            raise Exception(f'Menu display "{menu}" does not exist')

    def input_option(self, prompt: str = "Select an option: ") -> str:
        """
        Get user input for an option with a prompt. Trims and cleans the input
        """

        self.console_input_option = input(prompt).lower().strip()
        if len(self.console_input_option) == 0:
            print("No input provided. Please try again.")

            return self.input_option(prompt)
        return self.console_input_option

    def cls(self) -> None:
        """
        Clear the console screen.
        """

        import os

        os.system("cls" if os.name == "nt" else "clear")

    def repeat_until_success(self, func: Callable[..., State]) -> State:
        while True:
            func_output = func()
            if func_output == State.SUCCESS:
                return func_output


def main():
    cli = CLI()
    cli.start()


if __name__ == "__main__":
    main()
    # save_images()
