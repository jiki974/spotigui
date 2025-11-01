"""Top bar widget with back button, title, and device selector."""

from typing import Optional, Callable, List, Dict, Any
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.menu.menu import MDDropdownTextItem  # Explicitly import to register
from kivy.lang import Builder

# Load the KV file
Builder.load_file("src/spotigui/widgets/topbar.kv")


class TopBarWidget(MDBoxLayout):
    """Top bar widget containing navigation, title, and device controls."""

    def __init__(
        self,
        show_back_button: bool = True,
        show_device_button: bool = True,
        on_back: Optional[Callable] = None,
        on_device_select: Optional[Callable] = None,
        on_device_refresh: Optional[Callable] = None,
        **kwargs
    ):
        """
        Initialize top bar widget.

        Args:
            show_back_button: Whether to show the back button
            show_device_button: Whether to show the device button
            on_back: Callback when back button is pressed
            on_device_select: Callback when device is selected (device_id)
            on_device_refresh: Callback to refresh available devices
        """
        super().__init__(**kwargs)

        self.on_back_callback = on_back
        self.on_device_select_callback = on_device_select
        self.on_device_refresh_callback = on_device_refresh

        # Store initialization flags
        self.show_back_button = show_back_button
        self.show_device_button = show_device_button

        # Menu for device selection
        self.device_menu = None
        self.current_devices = []
        self.device_btn = None

    def on_kv_post(self, base_widget):
        """Called after the KV file has been applied."""
        super().on_kv_post(base_widget)

        # Add back button if needed
        if self.show_back_button:
            back_btn = MDIconButton(
                icon="arrow-left",
                font_size="24sp",
                pos_hint={"center_y": 0.5}
            )
            back_btn.bind(on_press=self._on_back)
            self.ids.left_container.add_widget(back_btn)

        # Add device button if needed
        if self.show_device_button:
            self.device_btn = MDIconButton(
                icon="cast",
                font_size="24sp",
                pos_hint={"center_y": 0.5}
            )
            self.device_btn.bind(on_press=self._on_device_button_press)
            self.ids.right_container.add_widget(self.device_btn)

    def set_track_name(self, track_name: str):
        """Update the track name text."""
        self.ids.track_name_label.text = track_name

    def _on_back(self, _instance):
        """Handle back button press."""
        if self.on_back_callback:
            self.on_back_callback()

    def _on_device_button_press(self, _instance):
        """Handle device button press to show device menu."""
        # Request fresh device list
        if self.on_device_refresh_callback:
            devices = self.on_device_refresh_callback()
            if devices:
                self.update_device_menu(devices)
                # Set caller and open menu
                if self.device_menu:
                    self.device_menu.caller = self.device_btn
                    self.device_menu.open()

    def update_device_menu(self, devices: List[Dict[str, Any]]):
        """Update the device selection menu with available devices."""
        self.current_devices = devices

        # Create menu items
        menu_items = []
        for device in devices:
            device_name = device.get("name", "Unknown Device")
            device_type = device.get("type", "")
            is_active = device.get("is_active", False)

            # Add checkmark for active device
            text = f"{'✓ ' if is_active else ''}{device_name}"
            if device_type:
                text += f" ({device_type})"

            menu_items.append({
                "text": text,
                "on_release": lambda x=device: self._select_device(x),
                "viewclass": "MDDropdownTextItem",
            })

        # Create or update menu (without caller initially)
        if not self.device_menu:
            self.device_menu = MDDropdownMenu(
                items=menu_items,
                max_height="200dp",
            )
        else:
            self.device_menu.items = menu_items

    def _select_device(self, device: Dict[str, Any]):
        """Handle device selection."""
        # Close the menu first
        if self.device_menu:
            self.device_menu.dismiss()

        # Then handle the selection
        device_id = device.get("id")
        if device_id and self.on_device_select_callback:
            self.on_device_select_callback(device_id)
