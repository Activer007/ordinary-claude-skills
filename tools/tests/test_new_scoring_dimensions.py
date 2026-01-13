
import pytest
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import List

# Add parent directory to path to import tools
sys.path.insert(0, str(Path(__file__).parent.parent))

from analyzer.technical_scorer import TechnicalScorer
from analyzer.content_scorer import ContentScorer

@dataclass
class MockCodeBlock:
    language: str
    content: str = ""
    line_count: int = 5
    has_comments: bool = False
    is_complete: bool = False
    has_error_handling: bool = False

class MockSkillDocument:
    def __init__(self, code_blocks=None):
        self.code_blocks = code_blocks or []
        self.markdown_body = ""
        self.sections = []

    def has_section(self, name):
        return False

class TestNewScoringDimensions:
    
    @pytest.fixture
    def scorer(self, config):
        return TechnicalScorer(config)

    @pytest.fixture
    def content_scorer(self, config):
        return ContentScorer(config)

    def test_score_code_diversity(self, scorer):
        # 0 blocks
        doc = MockSkillDocument([])
        assert scorer._score_code_diversity(doc) == 0

        # 1 language
        doc = MockSkillDocument([MockCodeBlock(language="python")])
        assert scorer._score_code_diversity(doc) == 1

        # 2 languages
        doc = MockSkillDocument([
            MockCodeBlock(language="python"),
            MockCodeBlock(language="javascript")
        ])
        assert scorer._score_code_diversity(doc) == 2

        # 3 languages
        doc = MockSkillDocument([
            MockCodeBlock(language="python"),
            MockCodeBlock(language="javascript"),
            MockCodeBlock(language="bash")
        ])
        assert scorer._score_code_diversity(doc) == 3

        # Duplicates shouldn't count
        doc = MockSkillDocument([
            MockCodeBlock(language="python"),
            MockCodeBlock(language="python"),
            MockCodeBlock(language="javascript")
        ])
        assert scorer._score_code_diversity(doc) == 2

        # Unknown shouldn't count
        doc = MockSkillDocument([
            MockCodeBlock(language="unknown"),
            MockCodeBlock(language="python")
        ])
        assert scorer._score_code_diversity(doc) == 1

    def test_score_example_quality(self, scorer):
        # Base case
        doc = MockSkillDocument([MockCodeBlock(language="python")])
        assert scorer._score_example_quality(doc) == 0 # No completeness, no comments, length 10 (Wait, default length is 10)
        
        # Check default length logic: 
        # "good_length_blocks = [b for b in doc.code_blocks if 10 <= b.line_count <= 50]"
        # If I have 1 block of length 10, score += 1.
        # So base case with default MockCodeBlock(length=10) should be 1.
        
        doc = MockSkillDocument([MockCodeBlock(language="python", line_count=5)])
        assert scorer._score_example_quality(doc) == 0

        # Completeness (+2)
        doc = MockSkillDocument([MockCodeBlock(language="python", is_complete=True, line_count=5)])
        assert scorer._score_example_quality(doc) == 2

        # Comments (+1)
        doc = MockSkillDocument([MockCodeBlock(language="python", has_comments=True, line_count=5)])
        assert scorer._score_example_quality(doc) == 1

        # Good Length (+1 for 1 block)
        doc = MockSkillDocument([MockCodeBlock(language="python", line_count=20)])
        assert scorer._score_example_quality(doc) == 1

        # Good Length (+2 for 2 blocks)
        doc = MockSkillDocument([
            MockCodeBlock(language="python", line_count=20),
            MockCodeBlock(language="js", line_count=30)
        ])
        assert scorer._score_example_quality(doc) == 2

        # Combined
        doc = MockSkillDocument([
            MockCodeBlock(language="python", is_complete=True, has_comments=True, line_count=20),
            MockCodeBlock(language="js", line_count=30)
        ])
        # Completeness: +2
        # Comments: +1
        # Length: +2
        # Total: 5
        assert scorer._score_example_quality(doc) == 5

    def test_score_input_output_examples(self, content_scorer):
        # Match "input...output"
        content = "Input: x. Output: y."
        assert content_scorer._score_input_output_examples(content) == 3

        # Match "request...response"
        content = "Request: {}. Response: {}."
        assert content_scorer._score_input_output_examples(content) == 3

        # Match ">>>"
        content = ">>> print('hello')"
        assert content_scorer._score_input_output_examples(content) == 3

        # No match
        content = "Just some text."
        assert content_scorer._score_input_output_examples(content) == 0

    def test_integration_technical_scorer(self, scorer):
        # Test _score_code_quality aggregation
        # 5 blocks (+5 quantity)
        # 3 languages (+3 diversity)
        # 2 complete, commented, good length (+4 quality)
        # Security keywords (+3 security)
        
        doc = MockSkillDocument([
            MockCodeBlock(language="python", is_complete=True, has_comments=True, line_count=20),
            MockCodeBlock(language="js", is_complete=True, has_comments=True, line_count=20),
            MockCodeBlock(language="bash", line_count=10),
            MockCodeBlock(language="go", line_count=10),
            MockCodeBlock(language="rust", line_count=10)
        ])
        content = "secure validate" # Has security keywords
        
        # Diversity: 5 languages -> 3 pts
        # Quality: 
        #   Completeness: +2
        #   Comments: +1
        #   Length: +2 (5 blocks > 2)
        #   Total Quality: 5 -> capped at 4 in _score_code_quality logic I wrote?
        #   Wait, in _score_code_quality I wrote: score += min(self._score_example_quality(doc), 4)
        #   So Quality = 4.
        
        # Quantity: 5 blocks -> 5 pts
        # Security: "validate" is in keywords -> +3 pts
        
        # Total: 5 + 3 + 4 + 3 = 15.
        
        score = scorer._score_code_quality(content, doc)
        assert score == 15

