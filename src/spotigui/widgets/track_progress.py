"""Track progress bar widget showing playback position and time remaining."""

from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import NumericProperty, StringProperty
from kivy.lang import Builder

from spotigui import resource_path

# Load the KV file
Builder.load_file(resource_path("src/spotigui/widgets/track_progress.kv"))


class TrackProgressWidget(MDBoxLayout):
    """Widget displaying track progress bar with current time and time remaining."""

    progress_value = NumericProperty(0)
    current_time_text = StringProperty("00:00")
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

        # Update current time
        self.current_time_text = self._format_time(current_sec)

        # Update progress bar
        if duration_sec > 0:
            self.progress_value = (current_sec / duration_sec) * 100

            # Calculate and update time remaining
            remaining_sec = duration_sec - current_sec
            self.time_remaining_text = self._format_time(remaining_sec)
        else:
            self.progress_value = 0
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
