"""
Global hotkey management system
"""

import pynput
from pynput import keyboard
from typing import Dict, Callable, Set
from .converter import ConversionType
from ..utils.feedback_system import get_feedback_system

class HotkeyManager:
    """Manages global keyboard shortcuts"""

    def __init__(self, callback_map: Dict[str, Callable]):
        self.callback_map = callback_map
        self.listener = None
        self.current_keys: Set = set()
        self.feedback_system = get_feedback_system()

    def setup_hotkeys(self):
        """Initialize global hotkey listener"""
        if self.listener:
            self.listener.stop()

        def on_press(key):
            try:
                if hasattr(key, 'char'):
                    self.current_keys.add(key.char)
                else:
                    self.current_keys.add(key)
            except AttributeError:
                self.current_keys.add(key)

            self._check_combinations()

        def on_release(key):
            try:
                if hasattr(key, 'char'):
                    self.current_keys.discard(key.char)
                else:
                    self.current_keys.discard(key)
            except (AttributeError, KeyError):
                pass

        self.listener = keyboard.Listener(
            on_press=on_press,
            on_release=on_release
        )
        self.listener.start()

    def _check_combinations(self):
        """Check for hotkey combinations and trigger callbacks"""
        if not (pynput.keyboard.Key.cmd in self.current_keys and
                pynput.keyboard.Key.shift in self.current_keys):
            return

        # Define hotkey mappings
        hotkey_map = {
            'u': ConversionType.UPPERCASE,
            'l': ConversionType.LOWERCASE,
            'c': ConversionType.CAPITALIZE
        }

        for key, conversion_type in hotkey_map.items():
            if key in self.current_keys:
                # Record hotkey activation
                self.feedback_system.record_hotkey_activation(
                    "⌘⇧" + key.upper(),
                    conversion_type.value
                )

                callback_key = f"convert_{conversion_type.value}"
                if callback_key in self.callback_map:
                    self.callback_map[callback_key](conversion_type)
                self.current_keys.clear()
                break

    def stop(self):
        """Stop the hotkey listener"""
        if self.listener:
            self.listener.stop()
            self.listener = None

    def restart(self):
        """Restart the hotkey system"""
        self.stop()
        self.setup_hotkeys()