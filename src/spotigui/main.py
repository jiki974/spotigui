"""
Main entry point for spotigui application.
Initializes the Kivy/KivyMD application with 720x720 window size.
"""

from kivy.core.window import Window
from kivy.logger import Logger
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel

from spotigui.config import WINDOW_WIDTH, WINDOW_HEIGHT, APP_NAME


# Configure window size before importing any other Kivy widgets
Window.size = (WINDOW_WIDTH, WINDOW_HEIGHT)


class SpotiGuiApp(MDApp):
    """Main application class for spotigui."""

    def build(self):
        """Build the application UI."""
        self.title = APP_NAME

        # Create main layout
        main_layout = MDBoxLayout(orientation="vertical", padding="10dp", spacing="10dp")

        # Placeholder for future UI components
        welcome_label = MDLabel(
            text="Welcome to spotigui",
            halign="center",
            size_hint_y=None,
            height="48dp",
        )
        main_layout.add_widget(welcome_label)

        return main_layout


def main():
    """Entry point for the application."""
    app = SpotiGuiApp()
    app.run()


if __name__ == "__main__":
    main()
