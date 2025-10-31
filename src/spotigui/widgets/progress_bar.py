"""Progress bar widget showing track playback progress and time remaining."""

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivy.properties import NumericProperty, StringProperty
from kivy.uix.progressbar import ProgressBar


class ProgressBarWidget(MDBoxLayout):
    """Widget showing track progress, duration, and time remaining."""

    current_position = NumericProperty(0)  # in seconds
    duration = NumericProperty(0)  # in seconds
    time_remaining_text = StringProperty("00:00")

    def __init__(self, **kwargs):
        """Initialize progress bar widget."""
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing = "5dp"
        self.padding = "5dp"
        self.size_hint_y = None
        self.height = "50dp"

        # Progress bar
        self.progress_bar = ProgressBar(
            value=0,
            max=100,
            size_hint_y=0.4,
        )
        self.add_widget(self.progress_bar)

        # Time info layout
        time_layout = MDBoxLayout(spacing="10dp", size_hint_y=0.6)

        # Current time label
        self.current_time_label = MDLabel(
            text="00:00",
            size_hint_x=0.2,
            halign="left",
            font_size="10sp",
        )
        time_layout.add_widget(self.current_time_label)

        # Time remaining label
        self.time_remaining_label = MDLabel(
            text=self.time_remaining_text,
            size_hint_x=0.8,
            halign="right",
            font_size="10sp",
        )
        time_layout.add_widget(self.time_remaining_label)

        self.add_widget(time_layout)

    def update_progress(self, current_pos_ms: int, duration_ms: int):
        """
        Update progress bar and time display.

        Args:
            current_pos_ms: Current playback position in milliseconds
            duration_ms: Total track duration in milliseconds
        """
        current_sec = current_pos_ms // 1000
        duration_sec = duration_ms // 1000

        # Update current position
        self.current_position = current_sec
        self.current_time_label.text = self._format_time(current_sec)

        # Update progress bar
        if duration_sec > 0:
            progress_percent = (current_sec / duration_sec) * 100
            self.progress_bar.value = progress_percent

            # Calculate and update time remaining
            remaining_sec = duration_sec - current_sec
            self.time_remaining_text = self._format_time(remaining_sec)
            self.time_remaining_label.text = self.time_remaining_text
        else:
            self.progress_bar.value = 0
            self.time_remaining_label.text = "00:00"

    @staticmethod
    def _format_time(seconds: int) -> str:
        """
        Format seconds to MM:SS format.

        Args:
            seconds: Number of seconds

        Returns:
            Formatted time string (MM:SS)
        """
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:02d}:{secs:02d}"

    def reset(self):
        """Reset progress bar to initial state."""
        self.current_position = 0
        self.progress_bar.value = 0
        self.current_time_label.text = "00:00"
        self.time_remaining_label.text = "00:00"
