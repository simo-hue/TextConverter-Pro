"""
Automatic paste functionality
"""

import time
import threading
import pynput
from pynput import keyboard

class AutoPaster:
    """Handles automatic pasting of converted text"""

    def __init__(self):
        self.is_pasting = False

    def paste_converted_text(self):
        """Paste converted text with proper timing and focus management"""
        if self.is_pasting:
            return

        def paste():
            self.is_pasting = True
            try:
                time.sleep(0.05)
                keyboard_controller = pynput.keyboard.Controller()

                # Release any held keys to prevent interference
                self._release_hotkey_modifiers(keyboard_controller)
                time.sleep(0.02)

                # Paste the converted text
                self._execute_paste(keyboard_controller)

            finally:
                self.is_pasting = False

        threading.Thread(target=paste, daemon=False).start()

    def _release_hotkey_modifiers(self, controller):
        """Release modifier keys that might interfere with pasting"""
        keys_to_release = [
            pynput.keyboard.Key.cmd,
            pynput.keyboard.Key.shift,
            'u', 'l', 'c'
        ]

        for key in keys_to_release:
            try:
                controller.release(key)
            except:
                pass

    def _execute_paste(self, controller):
        """Execute the paste command"""
        controller.press(pynput.keyboard.Key.cmd)
        controller.press('v')
        controller.release('v')
        controller.release(pynput.keyboard.Key.cmd)