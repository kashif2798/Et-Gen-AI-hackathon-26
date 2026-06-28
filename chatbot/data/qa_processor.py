"""
Q&A Document Parser

Parses q&a.md file into structured Q&A pairs for vector store ingestion.
"""
import re
import json
from typing import List, Dict, Tuple
from pathlib import Path
import logging

# Import from local schemas
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from api.schemas import QAPair

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QAProcessor:
    """
    Processes q&a.md file into structured Q&A pairs
    """
    
    def __init__(self):
        self.categories = {
            1: "Personalized Market Impact",
            2: "Agentic Analysis (Bull vs. Bear)",
            3: "Story Arc & Entity Tracking (GraphRAG)",
            4: "Generative UI & Actionable Data",
            5: "Fact-Checking & Jargon Explainer"
        }
    
    def parse_qa_document(self, file_path: str) -> List[QAPair]:
        """
        Main method to parse q&a.md file
        
        Args:
            file_path: Path to q&a.md file
            
        Returns:
            List of QAPair objects
        """
        logger.info(f"Reading Q&A document from: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        qa_pairs = self.extract_qa_pairs(content)
        
        logger.info(f"Successfully extracted {len(qa_pairs)} Q&A pairs")
        
        return qa_pairs
    
    def extract_qa_pairs(self, content: str) -> List[QAPair]:
        """
        Extract Q&A pairs from markdown content
        
        Args:
            content: Raw markdown content
            
        Returns:
            List of QAPair objects
        """
        qa_pairs = []
        current_category = None
        current_category_number = None
        
        # Split content into lines
        lines = content.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Check for category header
            category_match = re.match(r'^Category (\d+):\s*(.+)$', line)
            if category_match:
                current_category_number = int(category_match.group(1))
                current_category = category_match.group(2).strip()
                logger.info(f"Found Category {current_category_number}: {current_category}")
                i += 1
                continue
            
            # Check for question (starts with number followed by period)
            question_match = re.match(r'^(\d+)\.\s+(.+)$', line)
            if question_match and current_category:
                question_number = int(question_match.group(1))
                question_text = question_match.group(2).strip()
                
                # Look for answer on next line(s)
                i += 1
                answer_text = ""
                
                # Read answer (starts with "Answer:")
                while i < len(lines):
                    answer_line = lines[i].strip()
                    
                    if answer_line.startswith("Answer:"):
                        answer_text = answer_line.replace("Answer:", "").strip()
                        i += 1
                        
                        # Continue reading multi-line answers
                        while i < len(lines):
                            next_line = lines[i].strip()
                            # Stop if we hit next question or category
                            if (re.match(r'^\d+\.', next_line) or 
                                re.match(r'^Category \d+:', next_line) or
                                next_line == ""):
                                break
                            answer_text += " " + next_line
                            i += 1
                        break
                    i += 1
                
                if answer_text:
                    # Create QAPair
                    qa_id = f"qa_{current_category_number:02d}_{question_number:03d}"
                    
                    keywords = self._extract_keywords(question_text, answer_text)
                    
                    qa_pair = QAPair(
                        id=qa_id,
                        question=question_text,
                        answer=answer_text,
                        category=current_category,
                        category_number=current_category_number,
                        question_number=question_number,
                        keywords=keywords,
                        metadata={
                            "question_length": len(question_text),
                            "answer_length": len(answer_text),
                            "total_length": len(question_text) + len(answer_text)
                        }
                    )
                    
                    qa_pairs.append(qa_pair)
                    logger.debug(f"Extracted Q&A {qa_id}: {question_text[:50]}...")
                
                continue
            
            i += 1
        
        return qa_pairs
    
    def _extract_keywords(self, question: str, answer: str) -> List[str]:
        """
        Extract important keywords from question and answer
        
        Args:
            question: Question text
            answer: Answer text
            
        Returns:
            List of keywords
        """
        # Combine question and answer
        text = f"{question} {answer}".lower()
        
        # Common financial/market keywords to look for
        important_terms = [
            'rbi', 'sebi', 'nifty', 'sensex', 'ipo', 'fii', 'dii',
            'repo rate', 'inflation', 'gdp', 'fiscal deficit',
            'mutual fund', 'sip', 'equity', 'debt', 'bond',
            'stock', 'share', 'dividend', 'earnings', 'revenue',
            'bull', 'bear', 'market', 'portfolio', 'investment',
            'tax', 'capital gains', 'ltcg', 'stcg',
            'emi', 'loan', 'interest rate', 'bank',
            'ev', 'green energy', 'psu', 'pli',
            'rupee', 'dollar', 'crude oil', 'gold',
            'budget', 'policy', 'regulation', 'compliance'
        ]
        
        keywords = []
        for term in important_terms:
            if term in text:
                keywords.append(term)
        
        # Also extract capitalized words (likely company/entity names)
        capitalized = re.findall(r'\b[A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)*\b', question + " " + answer)
        keywords.extend([word for word in capitalized if len(word) > 2])
        
        # Remove duplicates and limit to top 10
        keywords = list(dict.fromkeys(keywords))[:10]
        
        return keywords
    
    def validate_qa_pairs(self, pairs: List[QAPair]) -> Tuple[bool, Dict]:
        """
        Validate extracted Q&A pairs
        
        Args:
            pairs: List of QAPair objects
            
        Returns:
            Tuple of (is_valid, validation_report)
        """
        report = {
            "total_pairs": len(pairs),
            "categories": {},
            "issues": [],
            "statistics": {}
        }
        
        # Check each category
        for cat_num in range(1, 6):
            cat_pairs = [p for p in pairs if p.category_number == cat_num]
            report["categories"][cat_num] = {
                "name": self.categories.get(cat_num, "Unknown"),
                "count": len(cat_pairs),
                "question_numbers": [p.question_number for p in cat_pairs]
            }
        
        # Check for missing questions
        for cat_num in range(1, 6):
            cat_pairs = [p for p in pairs if p.category_number == cat_num]
            question_nums = sorted([p.question_number for p in cat_pairs])
            
            # Expected 20 questions per category
            expected = list(range(1, 21))
            if cat_num == 1:
                expected = list(range(1, 21))
            elif cat_num == 2:
                expected = list(range(21, 41))
            elif cat_num == 3:
                expected = list(range(41, 61))
            elif cat_num == 4:
                expected = list(range(61, 81))
            elif cat_num == 5:
                expected = list(range(81, 101))
            
            actual = [p.question_number for p in cat_pairs]
            missing = set(expected) - set(actual)
            
            if missing:
                report["issues"].append(
                    f"Category {cat_num}: Missing questions {sorted(missing)}"
                )
        
        # Check for empty questions or answers
        for pair in pairs:
            if not pair.question.strip():
                report["issues"].append(f"{pair.id}: Empty question")
            if not pair.answer.strip():
                report["issues"].append(f"{pair.id}: Empty answer")
            if len(pair.answer) < 20:
                report["issues"].append(f"{pair.id}: Answer too short ({len(pair.answer)} chars)")
        
        # Statistics
        report["statistics"] = {
            "avg_question_length": sum(p.metadata["question_length"] for p in pairs) / len(pairs),
            "avg_answer_length": sum(p.metadata["answer_length"] for p in pairs) / len(pairs),
            "total_keywords": sum(len(p.keywords) for p in pairs),
            "avg_keywords_per_pair": sum(len(p.keywords) for p in pairs) / len(pairs)
        }
        
        is_valid = len(report["issues"]) == 0
        
        return is_valid, report
    
    def export_to_json(self, pairs: List[QAPair], output_path: str):
        """
        Export Q&A pairs to JSON file
        
        Args:
            pairs: List of QAPair objects
            output_path: Path to output JSON file
        """
        data = [pair.model_dump() for pair in pairs]
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Exported {len(pairs)} Q&A pairs to {output_path}")
    
    def load_from_json(self, input_path: str) -> List[QAPair]:
        """
        Load Q&A pairs from JSON file
        
        Args:
            input_path: Path to JSON file
            
        Returns:
            List of QAPair objects
        """
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        pairs = [QAPair(**item) for item in data]
        logger.info(f"Loaded {len(pairs)} Q&A pairs from {input_path}")
        
        return pairs


def main():
    """
    Main function to run Q&A processing
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Parse Q&A document")
    parser.add_argument("--input", default="q&a.md", help="Input Q&A markdown file")
    parser.add_argument("--output", default="qa_pairs.json", help="Output JSON file")
    parser.add_argument("--validate", action="store_true", help="Validate Q&A pairs")
    
    args = parser.parse_args()
    
    # Initialize processor
    processor = QAProcessor()
    
    # Parse document
    logger.info("=" * 60)
    logger.info("Q&A DOCUMENT PROCESSOR")
    logger.info("=" * 60)
    
    qa_pairs = processor.parse_qa_document(args.input)
    
    # Validate
    if args.validate:
        logger.info("\nValidating Q&A pairs...")
        is_valid, report = processor.validate_qa_pairs(qa_pairs)
        
        logger.info(f"\nValidation Report:")
        logger.info(f"Total pairs: {report['total_pairs']}")
        logger.info(f"\nCategories:")
        for cat_num, cat_info in report['categories'].items():
            logger.info(f"  Category {cat_num} ({cat_info['name']}): {cat_info['count']} pairs")
        
        logger.info(f"\nStatistics:")
        for key, value in report['statistics'].items():
            logger.info(f"  {key}: {value:.2f}")
        
        if report['issues']:
            logger.warning(f"\nIssues found ({len(report['issues'])}):")
            for issue in report['issues'][:10]:  # Show first 10
                logger.warning(f"  - {issue}")
        else:
            logger.info("\n✅ All validations passed!")
    
    # Export
    processor.export_to_json(qa_pairs, args.output)
    
    logger.info("=" * 60)
    logger.info(f"✅ Processing complete! Extracted {len(qa_pairs)} Q&A pairs")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
