# -*- coding: utf-8 -*-
"""Top bar widget with back button, title, and device selector."""

from typing import Optional, Callable, List, Dict, Any
from kivymd.uix.appbar import MDTopAppBar
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.menu.menu import MDDropdownTextItem  # Explicitly import to register
from kivy.lang import Builder
from kivy.properties import StringProperty

from spotigui import resource_path

# Load the KV file
Builder.load_file(resource_path("src/spotigui/widgets/topbar.kv"))


class TopBarWidget(MDTopAppBar):
    """Top bar widget containing navigation, title, and device controls."""

    back_button_icon = StringProperty("arrow-left")
    font_color = StringProperty("Custom")

    def __init__(
        self,
        back_button_icon: str = "arrow-left",
        font_color: str =  "Custom",
        on_back: Optional[Callable] = None,
        on_device_select: Optional[Callable] = None,
        on_device_refresh: Optional[Callable] = None,
        **kwargs
    ):
        """
        Initialize top bar widget.

        Args:
            font_color: Color to be used for text and icons
            back_button_icon: Icon to show on the back button (default: "arrow-left")
            on_back: Callback when back button is pressed
            on_device_select: Callback when device is selected (device_id)
            on_device_refresh: Callback to refresh available devices
        """
        super().__init__(**kwargs)

        self.back_button_icon = back_button_icon
        self.font_color = font_color
        self.on_back_callback = on_back
        self.on_device_select_callback = on_device_select
        self.on_device_refresh_callback = on_device_refresh# RGBA format (values 0-1)
        # Menu for device selection
        self.device_menu = None
        self.current_devices = []

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
                    self.device_menu.caller = self.ids.device_btn
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

            # Format device name with type
            text = device_name
            if device_type:
                text += f" ({device_type})"

            # Add [Active] prefix for active device
            if is_active:
                text = f"[Active] {text}"

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
