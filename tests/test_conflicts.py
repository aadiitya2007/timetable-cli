import unittest
from timetable.conflicts import do_overlap, find_conflicts


class TestConflicts(unittest.TestCase):
    def test_touching_boundaries_do_not_overlap(self):
        a = {"start": "09:00", "end": "10:00", "subject": "Math", "room": "101"}
        b = {"start": "10:00", "end": "11:00", "subject": "Physics", "room": "102"}
        self.assertFalse(do_overlap(a, b))

    def test_partial_overlap_detected(self):
        a = {"start": "09:00", "end": "10:30", "subject": "Math", "room": "101"}
        b = {"start": "10:00", "end": "11:00", "subject": "Physics", "room": "102"}
        self.assertTrue(do_overlap(a, b))

    def test_contained_overlap_detected(self):
        a = {"start": "09:00", "end": "12:00", "subject": "Lab", "room": "L1"}
        b = {"start": "10:00", "end": "11:00", "subject": "Tut", "room": "L1"}
        self.assertTrue(do_overlap(a, b))

    def test_overnight_slot_overlaps_late_evening_slot(self):
        overnight = {"start": "23:00", "end": "01:00", "subject": "Night", "room": "101"}
        late = {"start": "23:30", "end": "23:45", "subject": "Late", "room": "102"}
        self.assertTrue(do_overlap(overnight, late))

    def test_two_overnight_slots_overlap(self):
        first = {"start": "22:00", "end": "02:00", "subject": "First", "room": "101"}
        second = {"start": "23:00", "end": "01:00", "subject": "Second", "room": "102"}
        self.assertTrue(do_overlap(first, second))

    def test_find_conflicts_deterministic_and_no_duplicates(self):
        data = {
            "monday": [
                {"start": "09:00", "end": "10:30", "subject": "Math", "room": "101"},
                {"start": "10:00", "end": "11:00", "subject": "Physics", "room": "102"},
            ],
            "tuesday": [
                {"start": "09:00", "end": "10:00", "subject": "Chem", "room": "103"},
            ]
        }
        conflicts = find_conflicts(data)
        self.assertEqual(len(conflicts), 1)
        day, a, b = conflicts[0]
        self.assertEqual(day, "monday")
        self.assertEqual(a["subject"], "Math")
        self.assertEqual(b["subject"], "Physics")

    def test_empty_timetable_returns_no_conflicts(self):
        self.assertEqual(find_conflicts({}), [])

    def test_overnight_conflicts_with_next_day_slot(self):
        data = {
            "friday": [
                {"start": "23:00", "end": "01:00", "subject": "Night", "room": "101"},
            ],
            "saturday": [
                {"start": "00:30", "end": "01:30", "subject": "Early", "room": "102"},
            ],
        }
        conflicts = find_conflicts(data)
        self.assertEqual(len(conflicts), 1)
        self.assertEqual(conflicts[0][0], "friday")

    def test_sunday_overnight_conflicts_after_week_wrap(self):
        data = {
            "sunday": [
                {"start": "23:00", "end": "01:00", "subject": "Night", "room": "101"},
            ],
            "monday": [
                {"start": "00:30", "end": "01:30", "subject": "Early", "room": "102"},
            ],
        }
        conflicts = find_conflicts(data)
        self.assertEqual(len(conflicts), 1)
        self.assertEqual(conflicts[0][0], "sunday")
        self.assertEqual(conflicts[0][1]["subject"], "Night")
        self.assertEqual(conflicts[0][2]["subject"], "Early")


if __name__ == "__main__":
    unittest.main()
