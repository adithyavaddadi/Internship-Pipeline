import unittest
import os
import sys

# Ensure project root is in the path for tests
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import settings
from src.scrapers.base import detect_work_mode
from src.scoring.scorer import score_internship, deduplicate, filter_stipend
from src.utils.hr_finder import find_hr
from src.storage.seen_manager import load_seen, save_seen

class TestInternshipPipeline(unittest.TestCase):
    """Core unit tests verifying the refactored, modular Internship Pipeline functionality."""

    def test_settings_load(self):
        """Verifies configuration tokens load successfully."""
        self.assertIsNotNone(settings.LOCATIONS)
        self.assertGreater(len(settings.ML_ENGINEER_KEYWORDS), 0)
        self.assertEqual(settings.MIN_STIPEND, 5000)

    def test_detect_work_mode(self):
        """Verifies the work mode text classifier functions correctly."""
        self.assertEqual(detect_work_mode("Remote work from home listing"), "Remote")
        self.assertEqual(detect_work_mode("Office in Hyderabad, onsite role"), "Onsite")
        self.assertEqual(detect_work_mode("Hybrid flexible work week"), "Hybrid")
        self.assertEqual(detect_work_mode("Some unspecified requirements"), "Not specified")
        self.assertEqual(detect_work_mode(None), "Not specified")

    def test_scoring_system(self):
        """Asserts job scoring evaluates target skills and titles with proper weights."""
        high_match = {
            "title": "Senior Machine Learning Engineer",
            "skills": "PyTorch, LangChain, Python, ML Pipelines",
            "location": "Hyderabad",
            "mode": "Remote",
            "source": "Wellfound"
        }
        
        low_match = {
            "title": "Frontend Javascript Intern",
            "skills": "React, HTML, CSS",
            "location": "Delhi",
            "mode": "Onsite",
            "source": "Naukri"
        }

        high_score = score_internship(high_match)
        low_score = score_internship(low_match)
        
        self.assertGreater(high_score, low_score)
        self.assertGreater(high_score, 15)  # Should have matching titles and skills
        self.assertEqual(low_score, 0)     # No matching keywords

    def test_deduplicate(self):
        """Ensures identical company + title roles are removed."""
        jobs = [
            {"title": "ML Intern", "company": "Google", "url": "url1"},
            {"title": "ml intern", "company": "Google  ", "url": "url2"}, # Case & space diffs
            {"title": "Data Scientist", "company": "Meta", "url": "url3"}
        ]
        unique_jobs = deduplicate(jobs)
        self.assertEqual(len(unique_jobs), 2)

    def test_stipend_filter(self):
        """Asserts stipends below threshold are filtered, but unspecified are allowed."""
        jobs = [
            {"stipend": "Rs. 2,000 / month", "title": "Cheap job"}, # Below 5000
            {"stipend": "Rs. 10,000 / month", "title": "Good job"}, # Above 5000
            {"stipend": "Unspecified / Competitive", "title": "Hidden Gem"} # Unspecified
        ]
        passed = filter_stipend(jobs)
        self.assertEqual(len(passed), 2)
        self.assertNotIn("Cheap job", [j["title"] for j in passed])

    def test_find_hr(self):
        """Asserts LinkedIn search query URLs are formatted correctly."""
        job = {"company": "Cloudera", "title": "ML Engineer"}
        hr_info = find_hr(job)
        self.assertEqual(hr_info["company"], "Cloudera")
        self.assertIn("HR+Recruiter+Cloudera", hr_info["hr_search"])
        self.assertIn("Talent+Acquisition+Cloudera", hr_info["talent_search"])

if __name__ == "__main__":
    unittest.main()
