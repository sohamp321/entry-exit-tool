"""
NLP module for generating natural language summaries of student activity logs.
"""

import pandas as pd
import datetime
import random
from collections import defaultdict, Counter

class ActivitySummarizer:
    def __init__(self, database):
        """Initialize the activity summarizer with a database connection"""
        self.database = database

    def _get_time_period_description(self, days=7):
        """Get a description of the time period"""
        if days == 1:
            return "today"
        elif days == 7:
            return "this week"
        elif days == 30:
            return "this month"
        else:
            return f"in the last {days} days"

    def _get_time_category(self, timestamp):
        """Categorize a timestamp into a time of day"""
        time_str = timestamp.split()[1]  # Extract time part
        hour = int(time_str.split(':')[0])

        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 22:
            return "evening"
        else:
            return "night"

    def _is_late_night(self, timestamp):
        """Check if a timestamp is late at night (after 10 PM)"""
        time_str = timestamp.split()[1]  # Extract time part
        hour = int(time_str.split(':')[0])
        return hour >= 22 or hour < 5

    def _get_weekday(self, timestamp):
        """Get the weekday from a timestamp"""
        date_str = timestamp.split()[0]  # Extract date part
        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.strftime("%A")  # Full weekday name

    def _get_date_n_days_ago(self, n):
        """Get the date n days ago in YYYY-MM-DD format"""
        date = datetime.datetime.now() - datetime.timedelta(days=n)
        return date.strftime("%Y-%m-%d")

    def generate_student_summary(self, student_id, days=7):
        """Generate a natural language summary of a student's activity"""
        # Get student details
        student = self.database.get_student_by_id(student_id)
        if not student:
            return "No student found with the given ID."

        # student format: (id, roll_number, name, hostel_name, room_number, contact_number)
        student_name = student[2]
        hostel_name = student[3]
        room_number = student[4]

        # Get logs for the student
        all_logs = self.database.get_student_logs(student_id, limit=100)

        # Filter logs for the specified time period
        cutoff_date = self._get_date_n_days_ago(days)
        recent_logs = [log for log in all_logs if log[1].split()[0] >= cutoff_date]

        if not recent_logs:
            return f"{student_name} has no activity recorded {self._get_time_period_description(days)}."

        # Analyze the logs
        entries = [log for log in recent_logs if log[0] == 'entry']
        exits = [log for log in recent_logs if log[0] == 'exit']

        # Count late night entries and exits
        late_night_entries = [entry for entry in entries if self._is_late_night(entry[1])]
        late_night_exits = [exit for exit in exits if self._is_late_night(exit[1])]

        # Count entries and exits by time of day
        entry_times = Counter([self._get_time_category(entry[1]) for entry in entries])
        exit_times = Counter([self._get_time_category(exit[1]) for exit in exits])  # Fixed: exit[1] instead of exit

        # Count entries and exits by day of week
        entry_days = Counter([self._get_weekday(entry[1]) for entry in entries])
        exit_days = Counter([self._get_weekday(exit[1]) for exit in exits])

        # Generate summary sentences
        sentences = []

        # Basic activity summary
        time_period = self._get_time_period_description(days)
        sentences.append(f"{student_name} from {hostel_name} (Room {room_number}) had {len(entries)} entries and {len(exits)} exits {time_period}.")

        # Late night activity
        if late_night_entries:
            sentences.append(f"{student_name} entered the hostel {len(late_night_entries)} times after 10 PM {time_period}.")

        if late_night_exits:
            sentences.append(f"{student_name} left the hostel {len(late_night_exits)} times after 10 PM {time_period}.")

        # Most common patterns
        if entry_times:
            most_common_entry_time = max(entry_times.items(), key=lambda x: x[1])[0]
            sentences.append(f"{student_name} most frequently enters the hostel in the {most_common_entry_time}.")

        if exit_times:
            most_common_exit_time = max(exit_times.items(), key=lambda x: x[1])[0]
            sentences.append(f"{student_name} most frequently leaves the hostel in the {most_common_exit_time}.")

        if entry_days:
            most_common_entry_day = max(entry_days.items(), key=lambda x: x[1])[0]
            sentences.append(f"{student_name} enters the hostel most often on {most_common_entry_day}s.")

        # Combine sentences into a paragraph
        summary = " ".join(sentences)
        return summary

    def generate_hostel_summary(self, hostel_name=None, days=7):
        """Generate a summary of activity for an entire hostel or all hostels"""
        # Get all students
        all_students = self.database.get_all_students()

        if hostel_name:
            # Filter students by hostel
            students = [s for s in all_students if s[3] == hostel_name]
            if not students:
                return f"No students found in hostel {hostel_name}."
        else:
            students = all_students
            if not students:
                return "No students found in the database."

        # Get all logs
        all_logs = self.database.get_all_logs(limit=1000)

        # Filter logs for the specified time period
        cutoff_date = self._get_date_n_days_ago(days)
        recent_logs = [log for log in all_logs if log[1].split()[0] >= cutoff_date]

        if not recent_logs:
            if hostel_name:
                return f"No activity recorded for hostel {hostel_name} {self._get_time_period_description(days)}."
            else:
                return f"No activity recorded {self._get_time_period_description(days)}."

        # Group logs by student
        student_logs = defaultdict(list)
        for log in recent_logs:
            student_name = log[2]  # Name is at index 2
            student_logs[student_name].append(log)

        # Count total entries and exits
        entries = [log for log in recent_logs if log[0] == 'entry']
        exits = [log for log in recent_logs if log[0] == 'exit']

        # Count late night activity
        late_night_entries = [entry for entry in entries if self._is_late_night(entry[1])]
        late_night_exits = [exit for exit in exits if self._is_late_night(exit[1])]

        # Find students with most activity
        student_activity_count = {name: len(logs) for name, logs in student_logs.items()}
        if student_activity_count:
            most_active_student = max(student_activity_count.items(), key=lambda x: x[1])[0]
        else:
            most_active_student = None

        # Generate summary sentences
        sentences = []

        # Basic activity summary
        time_period = self._get_time_period_description(days)
        if hostel_name:
            sentences.append(f"Hostel {hostel_name} had {len(entries)} entries and {len(exits)} exits {time_period}.")
        else:
            sentences.append(f"All hostels had {len(entries)} entries and {len(exits)} exits {time_period}.")

        # Late night activity
        if late_night_entries:
            sentences.append(f"There were {len(late_night_entries)} late-night entries (after 10 PM) {time_period}.")

        if late_night_exits:
            sentences.append(f"There were {len(late_night_exits)} late-night exits (after 10 PM) {time_period}.")

        # Most active student
        if most_active_student:
            sentences.append(f"{most_active_student} was the most active student with {student_activity_count[most_active_student]} recorded activities.")

        # Combine sentences into a paragraph
        summary = " ".join(sentences)
        return summary
