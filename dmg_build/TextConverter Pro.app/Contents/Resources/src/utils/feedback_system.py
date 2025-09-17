"""
Professional User Feedback and Analytics System
"""

import time
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum

from .logger import get_logger
from .settings import get_settings_manager

class FeedbackType(Enum):
    """Types of user feedback events"""
    CONVERSION_SUCCESS = "conversion_success"
    CONVERSION_FAILURE = "conversion_failure"
    HOTKEY_ACTIVATION = "hotkey_activation"
    SETTINGS_CHANGE = "settings_change"
    ERROR_ENCOUNTERED = "error_encountered"
    PERFORMANCE_METRIC = "performance_metric"
    USER_ACTION = "user_action"

@dataclass
class FeedbackEvent:
    """Single feedback event record"""
    timestamp: float
    event_type: FeedbackType
    context: str
    details: Dict[str, Any]
    processing_time: Optional[float] = None
    success: bool = True
    error_code: Optional[str] = None

@dataclass
class UsageStatistics:
    """Aggregated usage statistics"""
    total_conversions: int = 0
    successful_conversions: int = 0
    failed_conversions: int = 0
    most_used_conversion: str = ""
    average_processing_time: float = 0.0
    hotkey_activations: int = 0
    settings_changes: int = 0
    errors_encountered: int = 0
    first_use: Optional[float] = None
    last_use: Optional[float] = None
    usage_sessions: int = 0

class FeedbackSystem:
    """Professional feedback and analytics system for user experience improvement"""

    def __init__(self):
        self.logger = get_logger()
        self.settings_manager = get_settings_manager()

        # Setup feedback storage
        self.feedback_dir = Path.home() / "Library" / "Application Support" / "TextConverter" / "Feedback"
        self.feedback_dir.mkdir(parents=True, exist_ok=True)

        self.events_file = self.feedback_dir / "user_events.json"
        self.stats_file = self.feedback_dir / "usage_stats.json"

        # In-memory storage for current session
        self.session_events: List[FeedbackEvent] = []
        self.session_start_time = time.time()

        # Load existing data
        self.usage_stats = self._load_usage_statistics()

        self.logger.info("Feedback system initialized")

    def record_conversion_attempt(
        self,
        conversion_type: str,
        text_length: int,
        processing_time: float,
        success: bool,
        error_message: Optional[str] = None
    ):
        """Record a text conversion attempt with detailed metrics"""
        try:
            event = FeedbackEvent(
                timestamp=time.time(),
                event_type=FeedbackType.CONVERSION_SUCCESS if success else FeedbackType.CONVERSION_FAILURE,
                context=f"conversion_{conversion_type}",
                details={
                    "conversion_type": conversion_type,
                    "text_length": text_length,
                    "success": success,
                    "error_message": error_message
                },
                processing_time=processing_time,
                success=success,
                error_code=None if success else "CONVERSION_FAILED"
            )

            self._record_event(event)

            # Update statistics
            self.usage_stats.total_conversions += 1
            if success:
                self.usage_stats.successful_conversions += 1
                # Update most used conversion
                self._update_most_used_conversion(conversion_type)
                # Update average processing time
                self._update_average_processing_time(processing_time)
            else:
                self.usage_stats.failed_conversions += 1
                self.usage_stats.errors_encountered += 1

            self.usage_stats.last_use = time.time()

            self.logger.debug("Conversion attempt recorded",
                            type=conversion_type, success=success, processing_time=processing_time)

        except Exception as e:
            self.logger.error("Failed to record conversion attempt", exception=e)

    def record_hotkey_activation(self, hotkey_combination: str, conversion_type: str):
        """Record hotkey activation for usage pattern analysis"""
        try:
            event = FeedbackEvent(
                timestamp=time.time(),
                event_type=FeedbackType.HOTKEY_ACTIVATION,
                context=f"hotkey_{conversion_type}",
                details={
                    "hotkey_combination": hotkey_combination,
                    "conversion_type": conversion_type
                }
            )

            self._record_event(event)
            self.usage_stats.hotkey_activations += 1

            self.logger.debug("Hotkey activation recorded", hotkey=hotkey_combination)

        except Exception as e:
            self.logger.error("Failed to record hotkey activation", exception=e)

    def record_settings_change(self, setting_category: str, setting_name: str, old_value: Any, new_value: Any):
        """Record settings changes for user behavior analysis"""
        try:
            event = FeedbackEvent(
                timestamp=time.time(),
                event_type=FeedbackType.SETTINGS_CHANGE,
                context=f"settings_{setting_category}",
                details={
                    "category": setting_category,
                    "setting": setting_name,
                    "old_value": str(old_value),
                    "new_value": str(new_value)
                }
            )

            self._record_event(event)
            self.usage_stats.settings_changes += 1

            self.logger.debug("Settings change recorded",
                            setting=f"{setting_category}.{setting_name}")

        except Exception as e:
            self.logger.error("Failed to record settings change", exception=e)

    def record_error(self, error_type: str, error_message: str, context: str, recoverable: bool = True):
        """Record error occurrences for quality improvement"""
        try:
            event = FeedbackEvent(
                timestamp=time.time(),
                event_type=FeedbackType.ERROR_ENCOUNTERED,
                context=context,
                details={
                    "error_type": error_type,
                    "error_message": error_message,
                    "recoverable": recoverable
                },
                success=False,
                error_code=error_type
            )

            self._record_event(event)
            self.usage_stats.errors_encountered += 1

            self.logger.debug("Error recorded for feedback", error_type=error_type)

        except Exception as e:
            self.logger.error("Failed to record error feedback", exception=e)

    def record_performance_metric(self, metric_name: str, value: float, unit: str = "ms"):
        """Record performance metrics for optimization analysis"""
        try:
            event = FeedbackEvent(
                timestamp=time.time(),
                event_type=FeedbackType.PERFORMANCE_METRIC,
                context=f"performance_{metric_name}",
                details={
                    "metric_name": metric_name,
                    "value": value,
                    "unit": unit
                },
                processing_time=value if unit in ["ms", "s"] else None
            )

            self._record_event(event)

            self.logger.debug("Performance metric recorded", metric=metric_name, value=value)

        except Exception as e:
            self.logger.error("Failed to record performance metric", exception=e)

    def record_user_action(self, action: str, context: str, additional_data: Optional[Dict[str, Any]] = None):
        """Record general user actions for usage pattern analysis"""
        try:
            details = {
                "action": action,
                "context": context
            }
            if additional_data:
                details.update(additional_data)

            event = FeedbackEvent(
                timestamp=time.time(),
                event_type=FeedbackType.USER_ACTION,
                context=f"action_{action}",
                details=details
            )

            self._record_event(event)

            self.logger.debug("User action recorded", action=action)

        except Exception as e:
            self.logger.error("Failed to record user action", exception=e)

    def get_usage_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive usage summary for the specified period"""
        try:
            cutoff_time = time.time() - (days * 24 * 3600)
            recent_events = [
                event for event in self._load_recent_events(cutoff_time)
                if event.timestamp >= cutoff_time
            ]

            # Analyze recent usage
            conversion_events = [e for e in recent_events if e.event_type in
                               [FeedbackType.CONVERSION_SUCCESS, FeedbackType.CONVERSION_FAILURE]]

            hotkey_events = [e for e in recent_events if e.event_type == FeedbackType.HOTKEY_ACTIVATION]
            error_events = [e for e in recent_events if e.event_type == FeedbackType.ERROR_ENCOUNTERED]

            # Calculate success rate
            successful_conversions = len([e for e in conversion_events if e.success])
            total_conversions = len(conversion_events)
            success_rate = (successful_conversions / total_conversions * 100) if total_conversions > 0 else 0

            # Most used features
            conversion_types = [e.details.get("conversion_type", "unknown") for e in conversion_events]
            most_used = max(set(conversion_types), key=conversion_types.count) if conversion_types else "none"

            # Average performance
            processing_times = [e.processing_time for e in conversion_events
                              if e.processing_time and e.success]
            avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0

            # Error analysis
            error_types = [e.details.get("error_type", "unknown") for e in error_events]
            most_common_error = max(set(error_types), key=error_types.count) if error_types else "none"

            summary = {
                "period_days": days,
                "total_events": len(recent_events),
                "conversions": {
                    "total": total_conversions,
                    "successful": successful_conversions,
                    "failed": total_conversions - successful_conversions,
                    "success_rate": round(success_rate, 2),
                    "most_used_type": most_used,
                    "avg_processing_time": round(avg_processing_time, 3)
                },
                "hotkey_activations": len(hotkey_events),
                "errors": {
                    "total": len(error_events),
                    "most_common": most_common_error
                },
                "session_info": {
                    "session_duration": round((time.time() - self.session_start_time) / 60, 2),
                    "session_events": len(self.session_events)
                }
            }

            return summary

        except Exception as e:
            self.logger.error("Failed to generate usage summary", exception=e)
            return {"error": "Failed to generate summary"}

    def get_user_experience_insights(self) -> List[str]:
        """Generate user experience insights and recommendations"""
        try:
            insights = []
            stats = self.usage_stats

            # Usage frequency insights
            if stats.total_conversions == 0:
                insights.append("💡 Try using the text conversion hotkeys to transform text quickly!")
            elif stats.total_conversions < 10:
                insights.append("🚀 You're getting started! Explore all three conversion types.")
            else:
                insights.append(f"🎉 You've performed {stats.total_conversions} conversions! You're a power user!")

            # Success rate insights
            if stats.total_conversions > 0:
                success_rate = (stats.successful_conversions / stats.total_conversions) * 100
                if success_rate < 80:
                    insights.append("⚠️ Some conversions failed. Check accessibility permissions.")
                elif success_rate > 95:
                    insights.append("✅ Excellent conversion success rate!")

            # Performance insights
            if stats.average_processing_time > 1.0:
                insights.append("🐌 Conversions seem slow. Consider restarting the app.")
            elif stats.average_processing_time < 0.1:
                insights.append("⚡ Lightning fast conversions! Great performance!")

            # Error insights
            if stats.errors_encountered > stats.successful_conversions * 0.1:
                insights.append("🔧 Frequent errors detected. Check system diagnostics.")

            # Usage pattern insights
            if stats.most_used_conversion:
                insights.append(f"📊 Your favorite conversion: {stats.most_used_conversion.title()}")

            return insights

        except Exception as e:
            self.logger.error("Failed to generate user experience insights", exception=e)
            return ["❌ Unable to analyze usage patterns"]

    def export_feedback_data(self, include_events: bool = False) -> Dict[str, Any]:
        """Export feedback data for analysis or support"""
        try:
            export_data = {
                "export_timestamp": time.time(),
                "usage_statistics": asdict(self.usage_stats),
                "usage_summary": self.get_usage_summary(30),
                "user_insights": self.get_user_experience_insights()
            }

            if include_events:
                recent_events = self._load_recent_events(time.time() - (7 * 24 * 3600))  # Last 7 days
                export_data["recent_events"] = [asdict(event) for event in recent_events[-100:]]

            return export_data

        except Exception as e:
            self.logger.error("Failed to export feedback data", exception=e)
            return {"error": "Export failed"}

    def cleanup_old_data(self, days_to_keep: int = 90):
        """Clean up old feedback data to manage storage"""
        try:
            cutoff_time = time.time() - (days_to_keep * 24 * 3600)

            # Load and filter events
            all_events = self._load_all_events()
            recent_events = [event for event in all_events if event.timestamp >= cutoff_time]

            # Save filtered events
            self._save_events(recent_events)

            removed_count = len(all_events) - len(recent_events)
            self.logger.info("Feedback data cleanup completed",
                           removed_events=removed_count, kept_events=len(recent_events))

        except Exception as e:
            self.logger.error("Failed to cleanup feedback data", exception=e)

    # Private methods

    def _record_event(self, event: FeedbackEvent):
        """Record a single feedback event"""
        try:
            # Add to session events
            self.session_events.append(event)

            # Persist to disk (append mode for efficiency)
            self._append_event_to_disk(event)

            # Update first use if not set
            if self.usage_stats.first_use is None:
                self.usage_stats.first_use = event.timestamp

            # Save updated statistics
            self._save_usage_statistics()

        except Exception as e:
            self.logger.error("Failed to record event", exception=e)

    def _update_most_used_conversion(self, conversion_type: str):
        """Update most used conversion type tracking"""
        try:
            # Simple approach: just track the latest successful conversion
            # For more accuracy, we'd analyze all events, but this is sufficient
            self.usage_stats.most_used_conversion = conversion_type

        except Exception as e:
            self.logger.error("Failed to update most used conversion", exception=e)

    def _update_average_processing_time(self, new_time: float):
        """Update rolling average processing time"""
        try:
            current_avg = self.usage_stats.average_processing_time
            successful = self.usage_stats.successful_conversions

            if successful <= 1:
                self.usage_stats.average_processing_time = new_time
            else:
                # Rolling average calculation
                self.usage_stats.average_processing_time = (
                    (current_avg * (successful - 1)) + new_time
                ) / successful

        except Exception as e:
            self.logger.error("Failed to update average processing time", exception=e)

    def _load_usage_statistics(self) -> UsageStatistics:
        """Load usage statistics from disk"""
        try:
            if self.stats_file.exists():
                with open(self.stats_file, 'r') as f:
                    data = json.load(f)
                    return UsageStatistics(**data)
        except Exception as e:
            self.logger.debug("Failed to load usage statistics, using defaults", exception=e)

        return UsageStatistics()

    def _save_usage_statistics(self):
        """Save usage statistics to disk"""
        try:
            with open(self.stats_file, 'w') as f:
                json.dump(asdict(self.usage_stats), f, indent=2)
        except Exception as e:
            self.logger.error("Failed to save usage statistics", exception=e)

    def _append_event_to_disk(self, event: FeedbackEvent):
        """Append single event to disk file"""
        try:
            # Simple append approach - for production might use database
            event_data = asdict(event)
            event_data['event_type'] = event.event_type.value

            if self.events_file.exists():
                # Read existing events
                with open(self.events_file, 'r') as f:
                    events = json.load(f)
            else:
                events = []

            events.append(event_data)

            # Keep only last 1000 events to manage file size
            if len(events) > 1000:
                events = events[-1000:]

            with open(self.events_file, 'w') as f:
                json.dump(events, f, indent=2)

        except Exception as e:
            self.logger.error("Failed to append event to disk", exception=e)

    def _load_recent_events(self, since_timestamp: float) -> List[FeedbackEvent]:
        """Load events since the specified timestamp"""
        try:
            all_events = self._load_all_events()
            return [event for event in all_events if event.timestamp >= since_timestamp]
        except Exception as e:
            self.logger.error("Failed to load recent events", exception=e)
            return []

    def _load_all_events(self) -> List[FeedbackEvent]:
        """Load all events from disk"""
        try:
            if not self.events_file.exists():
                return []

            with open(self.events_file, 'r') as f:
                events_data = json.load(f)

            events = []
            for event_data in events_data:
                # Convert back to enum
                event_data['event_type'] = FeedbackType(event_data['event_type'])
                events.append(FeedbackEvent(**event_data))

            return events

        except Exception as e:
            self.logger.error("Failed to load all events", exception=e)
            return []

    def _save_events(self, events: List[FeedbackEvent]):
        """Save events list to disk"""
        try:
            events_data = []
            for event in events:
                event_data = asdict(event)
                event_data['event_type'] = event.event_type.value
                events_data.append(event_data)

            with open(self.events_file, 'w') as f:
                json.dump(events_data, f, indent=2)

        except Exception as e:
            self.logger.error("Failed to save events", exception=e)

# Global feedback system instance
_feedback_system = None

def get_feedback_system() -> FeedbackSystem:
    """Get global feedback system instance"""
    global _feedback_system
    if _feedback_system is None:
        _feedback_system = FeedbackSystem()
    return _feedback_system