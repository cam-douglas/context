import os
import unittest

os.environ.setdefault("CONTEXT_GENERATOR", "pedalboard")

from context_sidecar.generation import _musicgen_prompt
from context_sidecar.genres import genre_count, lineage_for, lineage_text, match_genres, match_style


class GenreIndexTests(unittest.TestCase):
    def test_index_is_wide(self):
        self.assertGreaterEqual(genre_count(), 6000)

    def test_longest_match_and_aliases(self):
        self.assertEqual(match_style("dark ambient pad")[0], "dark ambient")
        self.assertIn("uk garage", match_genres("32 bar uk garage"))
        self.assertIn("drum and bass", match_genres("8 bar dnb loop"))
        self.assertTrue(match_genres("boom bap verse"))
        self.assertTrue(match_genres("shoegaze guitar"))

    def test_musicgen_prompt_includes_bars(self):
        text = _musicgen_prompt(
            "make it darker",
            {"style": "shoegaze", "genres": ["shoegaze"], "bars": 8, "tempo_bpm": 120, "key": "Am"},
        )
        self.assertIn("8-bar", text)
        self.assertIn("shoegaze", text)
        self.assertIn("120 bpm", text)

    def test_wikidata_lineage_not_musicmap(self):
        shoegaze = lineage_for("shoegaze")
        self.assertTrue(shoegaze["parents"] or shoegaze["year"])
        house = lineage_for("house")
        self.assertIn("electronic dance music", house["parents"] + house["ancestors"])
        text = lineage_text("dark ambient")
        self.assertTrue(text)
        prompted = _musicgen_prompt(
            "make it darker",
            {
                "style": "dark ambient",
                "genres": ["dark ambient"],
                "bars": 8,
                "tempo_bpm": 80,
                "key": "Am",
                "lineage_text": text,
            },
        )
        self.assertIn("emerged around", prompted)


if __name__ == "__main__":
    unittest.main()
