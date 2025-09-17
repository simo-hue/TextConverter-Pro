"""
Enhanced Feedback Dialog for User Experience Insights
"""

import rumps
from typing import Optional, Dict, Any
from ..utils.feedback_system import get_feedback_system
from ..utils.logger import get_logger

class FeedbackDialog:
    """Professional feedback dialog for user experience insights"""

    def __init__(self):
        self.feedback_system = get_feedback_system()
        self.logger = get_logger()

    def show_detailed_statistics(self) -> None:
        """Show comprehensive statistics with export option"""
        try:
            # Get detailed usage summary
            summary = self.feedback_system.get_usage_summary(30)
            insights = self.feedback_system.get_user_experience_insights()

            stats_content = f"""📊 TextConverter Pro - Detailed Statistics

📈 Usage Summary (Last 30 Days):
──────────────────────────────────────
🔄 Text Conversions:
   • Total Attempts: {summary['conversions']['total']}
   • Successful: {summary['conversions']['successful']}
   • Failed: {summary['conversions']['failed']}
   • Success Rate: {summary['conversions']['success_rate']}%
   • Average Processing Time: {summary['conversions']['avg_processing_time']}s

📊 Most Used Features:
   • Primary Conversion: {summary['conversions']['most_used_type'].title()}
   • Hotkey Activations: {summary['hotkey_activations']}

⚠️ Error Analysis:
   • Total Errors: {summary['errors']['total']}
   • Most Common: {summary['errors']['most_common']}

💡 User Experience Insights:
──────────────────────────────────────"""

            for insight in insights:
                stats_content += f"\n• {insight}"

            stats_content += f"""

🔧 Current Session:
──────────────────────────────────────
• Session Duration: {summary['session_info']['session_duration']} minutes
• Session Events: {summary['session_info']['session_events']}

💾 Data Export Available:
Click 'Export Data' to save detailed analytics for analysis."""

            # Show dialog with export option
            response = rumps.alert(
                "Detailed Statistics & Insights",
                stats_content,
                ok="Close",
                cancel="Export Data"
            )

            # Handle export if user clicked cancel (export button)
            if response == 0:  # Cancel button (Export Data)
                self._export_feedback_data()

        except Exception as e:
            self.logger.error("Failed to show detailed statistics", exception=e)
            rumps.alert("Error", "Failed to generate detailed statistics. Please check logs.")

    def show_performance_metrics(self) -> None:
        """Show performance metrics and optimization suggestions"""
        try:
            summary = self.feedback_system.get_usage_summary(7)  # Last 7 days

            performance_content = f"""⚡ Performance Metrics (Last 7 Days)

🚀 Speed Analysis:
──────────────────────────────────────
• Average Conversion Time: {summary['conversions']['avg_processing_time']}s
• Total Conversions: {summary['conversions']['total']}
• Success Rate: {summary['conversions']['success_rate']}%

📊 Performance Rating:"""

            # Analyze performance
            avg_time = summary['conversions']['avg_processing_time']
            success_rate = summary['conversions']['success_rate']

            if avg_time < 0.1:
                performance_content += "\n🟢 Excellent - Lightning fast conversions!"
            elif avg_time < 0.5:
                performance_content += "\n🟡 Good - Conversions are reasonably fast"
            else:
                performance_content += "\n🔴 Slow - Consider restarting the application"

            if success_rate > 95:
                performance_content += "\n🟢 Excellent - Very high success rate"
            elif success_rate > 80:
                performance_content += "\n🟡 Good - Acceptable success rate"
            else:
                performance_content += "\n🔴 Poor - Check system permissions"

            performance_content += f"""

🔧 Optimization Tips:
──────────────────────────────────────
• Restart app if conversions are slow
• Check Accessibility permissions if failures occur
• Clear clipboard history if using large texts
• Consider shorter text snippets for better performance

📈 Trending:
• Error Rate: {(summary['errors']['total'] / max(1, summary['total_events'])) * 100:.1f}%
• Hotkey Usage: {summary['hotkey_activations']} activations"""

            rumps.alert("Performance Analysis", performance_content)

        except Exception as e:
            self.logger.error("Failed to show performance metrics", exception=e)
            rumps.alert("Error", "Failed to generate performance metrics.")

    def show_usage_trends(self) -> None:
        """Show usage trends and patterns"""
        try:
            # Get trends for different periods
            week_summary = self.feedback_system.get_usage_summary(7)
            month_summary = self.feedback_system.get_usage_summary(30)

            trends_content = f"""📈 Usage Trends & Patterns

📊 Comparison Analysis:
──────────────────────────────────────
                    Last 7 Days    Last 30 Days
Conversions:        {week_summary['conversions']['total']:>8}    {month_summary['conversions']['total']:>10}
Success Rate:       {week_summary['conversions']['success_rate']:>7.1f}%    {month_summary['conversions']['success_rate']:>9.1f}%
Hotkey Usage:       {week_summary['hotkey_activations']:>8}    {month_summary['hotkey_activations']:>10}
Errors:             {week_summary['errors']['total']:>8}    {month_summary['errors']['total']:>10}

🎯 Usage Patterns:
──────────────────────────────────────
• Primary Feature: {month_summary['conversions']['most_used_type'].title()}
• Weekly Activity: {week_summary['conversions']['total']} conversions
• Daily Average: {week_summary['conversions']['total'] / 7:.1f} conversions

📊 Growth Analysis:"""

            # Calculate growth
            weekly_avg = week_summary['conversions']['total'] / 7
            monthly_avg = month_summary['conversions']['total'] / 30

            if weekly_avg > monthly_avg * 1.1:
                trends_content += "\n🚀 Growing Usage - You're using TextConverter more!"
            elif weekly_avg < monthly_avg * 0.9:
                trends_content += "\n📉 Declining Usage - Consider exploring more features"
            else:
                trends_content += "\n📊 Stable Usage - Consistent workflow integration"

            trends_content += f"""

💡 Insights:
──────────────────────────────────────"""

            # Add contextual insights
            insights = self.feedback_system.get_user_experience_insights()
            for insight in insights[:3]:  # Show top 3 insights
                trends_content += f"\n• {insight}"

            rumps.alert("Usage Trends", trends_content)

        except Exception as e:
            self.logger.error("Failed to show usage trends", exception=e)
            rumps.alert("Error", "Failed to generate usage trends.")

    def _export_feedback_data(self) -> None:
        """Export detailed feedback data to file"""
        try:
            import json
            from pathlib import Path
            from datetime import datetime

            # Get comprehensive data export
            export_data = self.feedback_system.export_feedback_data(include_events=True)

            # Create export filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_filename = f"TextConverter_Analytics_{timestamp}.json"

            # Save to Downloads folder
            downloads_path = Path.home() / "Downloads"
            export_file = downloads_path / export_filename

            with open(export_file, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)

            rumps.alert(
                "Data Exported Successfully",
                f"Analytics data exported to:\n{export_file}\n\nThis file contains your usage patterns, performance metrics, and insights for analysis."
            )

            self.logger.info("Analytics data exported successfully", file_path=str(export_file))

        except Exception as e:
            self.logger.error("Failed to export feedback data", exception=e)
            rumps.alert("Export Failed", "Failed to export analytics data. Please check logs.")

    def show_feedback_summary_dialog(self) -> None:
        """Show a summary dialog with key metrics and quick actions"""
        try:
            summary = self.feedback_system.get_usage_summary(7)
            insights = self.feedback_system.get_user_experience_insights()

            quick_summary = f"""📊 TextConverter Pro - Quick Summary

🔄 This Week: {summary['conversions']['total']} conversions
✅ Success Rate: {summary['conversions']['success_rate']}%
⚡ Avg Speed: {summary['conversions']['avg_processing_time']}s
⌨️ Hotkeys Used: {summary['hotkey_activations']} times

💡 Top Insight: {insights[0] if insights else 'Start using to get insights!'}

📈 Want more details?
• View Detailed Statistics
• Check Performance Metrics
• Analyze Usage Trends"""

            response = rumps.alert(
                "Feedback Summary",
                quick_summary,
                ok="Close",
                cancel="Detailed View"
            )

            if response == 0:  # Cancel button (Detailed View)
                self.show_detailed_statistics()

        except Exception as e:
            self.logger.error("Failed to show feedback summary", exception=e)
            rumps.alert("Error", "Failed to generate feedback summary.")

# Global instance
_feedback_dialog = None

def get_feedback_dialog() -> FeedbackDialog:
    """Get global feedback dialog instance"""
    global _feedback_dialog
    if _feedback_dialog is None:
        _feedback_dialog = FeedbackDialog()
    return _feedback_dialog