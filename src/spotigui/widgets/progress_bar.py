"""Progress bar widget showing track playback progress and time remaining."""

from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import NumericProperty, StringProperty
from kivy.lang import Builder

# Load the KV file
Builder.load_file("src/spotigui/widgets/progress_bar.kv")


class ProgressBarWidget(MDBoxLayout):
    """Widget showing track progress, duration, and time remaining."""

    current_position = NumericProperty(0)  # in seconds
    duration = NumericProperty(0)  # in seconds
    time_remaining_text = StringProperty("00:00")

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
        self.ids.current_time_label.text = self._format_time(current_sec)

        # Update progress bar
        if duration_sec > 0:
            progress_percent = (current_sec / duration_sec) * 100
            self.ids.progress_bar.value = progress_percent

            # Calculate and update time remaining
            remaining_sec = duration_sec - current_sec
            self.time_remaining_text = self._format_time(remaining_sec)
        else:
            self.ids.progress_bar.value = 0
            self.time_remaining_text = "00:00"

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
        self.ids.progress_bar.value = 0
        self.ids.current_time_label.text = "00:00"
        self.time_remaining_text = "00:00"
