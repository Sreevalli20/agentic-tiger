"""Dataset parser for TigerGraph Agentic GraphRAG."""
import json
import re
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class DatasetParser:
    """Parser for the hackathon dataset."""
    
    def __init__(self, corpus_path: str, questions_path: str):
        """Initialize dataset parser.
        
        Args:
            corpus_path: Path to corpus.jsonl
            questions_path: Path to questions directory
        """
        self.corpus_path = Path(corpus_path)
        self.questions_path = Path(questions_path)
        self.documents = []
        self.public_questions = []
        self.hidden_questions = []
    
    def load_corpus(self) -> List[Dict[str, Any]]:
        """Load and parse corpus.jsonl."""
        logger.info(f"Loading corpus from {self.corpus_path}")
        
        if not self.corpus_path.exists():
            raise FileNotFoundError(f"Corpus file not found: {self.corpus_path}")
        
        documents = []
        with open(self.corpus_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    doc = json.loads(line.strip())
                    documents.append(doc)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse line {line_num}: {e}")
        
        logger.info(f"Loaded {len(documents)} documents from corpus")
        self.documents = documents
        return documents
    
    def load_public_questions(self) -> List[Dict[str, Any]]:
        """Load public evaluation questions."""
        public_path = self.questions_path / "eval_public.jsonl"
        logger.info(f"Loading public questions from {public_path}")
        
        if not public_path.exists():
            raise FileNotFoundError(f"Public questions file not found: {public_path}")
        
        questions = []
        with open(public_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    q = json.loads(line.strip())
                    questions.append(q)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse line {line_num}: {e}")
        
        logger.info(f"Loaded {len(questions)} public questions")
        self.public_questions = questions
        return questions
    
    def load_hidden_questions(self) -> List[Dict[str, Any]]:
        """Load hidden evaluation questions."""
        hidden_path = self.questions_path / "eval_hidden.jsonl"
        logger.info(f"Loading hidden questions from {hidden_path}")
        
        if not hidden_path.exists():
            raise FileNotFoundError(f"Hidden questions file not found: {hidden_path}")
        
        questions = []
        with open(hidden_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    q = json.loads(line.strip())
                    questions.append(q)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse line {line_num}: {e}")
        
        logger.info(f"Loaded {len(questions)} hidden questions")
        self.hidden_questions = questions
        return questions
    
    def extract_event_info(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Extract event information from a document.
        
        Args:
            document: Document dictionary
            
        Returns:
            Dictionary with extracted event information
        """
        text = document.get('text', '')
        title = document.get('title', '')
        
        # Parse infobox data from text
        infobox_data = self._parse_infobox(text)
        
        # Extract games information from title
        games_info = self._extract_games_info(title)
        
        # Extract event name
        event_name = self._extract_event_name(title)
        
        # Extract sport
        sport = self._extract_sport(title)
        
        return {
            'doc_id': document.get('doc_id'),
            'event_id': f"{sport}_{event_name}_{games_info.get('year', 'unknown')}",
            'name': event_name,
            'sport': sport,
            'games': f"{games_info.get('year', 'unknown')} {games_info.get('season', 'unknown')}",
            'year': games_info.get('year'),
            'season': games_info.get('season'),
            'date': infobox_data.get('date'),
            'venue': infobox_data.get('venue'),
            'competitors': infobox_data.get('competitors'),
            'nations': infobox_data.get('nations'),
            'event_type': infobox_data.get('event'),
            'medalists': self._extract_medalists(infobox_data)
        }
    
    def _parse_infobox(self, text: str) -> Dict[str, Any]:
        """Parse infobox data from document text.
        
        Args:
            text: Document text
            
        Returns:
            Dictionary with infobox fields
        """
        infobox_data = {}
        
        # Look for infobox section
        infobox_match = re.search(r'\[Infobox Olympic event\](.*?)(?:\n\n|\Z)', text, re.DOTALL)
        if not infobox_match:
            return infobox_data
        
        infobox_text = infobox_match.group(1)
        
        # Extract key-value pairs
        for line in infobox_text.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()
                infobox_data[key] = value
        
        return infobox_data
    
    def _extract_games_info(self, title: str) -> Dict[str, Any]:
        """Extract Olympic games information from title.
        
        Args:
            title: Document title
            
        Returns:
            Dictionary with year and season
        """
        # Look for year patterns
        year_match = re.search(r'(19|20)\d{2}', title)
        year = int(year_match.group()) if year_match else None
        
        # Determine season
        season = 'Summer' if 'Summer' in title else 'Winter' if 'Winter' in title else 'unknown'
        
        return {
            'year': year,
            'season': season
        }
    
    def _extract_event_name(self, title: str) -> str:
        """Extract event name from title.
        
        Args:
            title: Document title
            
        Returns:
            Event name
        """
        # Remove "Sport at the Year Olympics" prefix
        match = re.search(r'–\s*(.+)$', title)
        if match:
            return match.group(1).strip()
        
        return title
    
    def _extract_sport(self, title: str) -> str:
        """Extract sport from title.
        
        Args:
            title: Document title
            
        Returns:
            Sport name
        """
        # Look for sport before "at the"
        match = re.search(r'^(.+?)\s+at the', title)
        if match:
            return match.group(1).strip()
        
        return 'Unknown'
    
    def _extract_medalists(self, infobox_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract medalists from infobox data.
        
        Args:
            infobox_data: Parsed infobox data
            
        Returns:
            List of medalist dictionaries
        """
        medalists = []
        
        for medal_type in ['gold', 'silver', 'bronze']:
            medalists_key = f'{medal_type}'
            if medalists_key in infobox_data:
                names = infobox_data[medalists_key]
                noc_key = f'{medalists_key}NOC'
                noc = infobox_data.get(noc_key, '')
                
                # Handle concatenated names (e.g., "Rudolf DombiRoland Kökény")
                # This is a known data quality issue
                athlete_names = self._split_concatenated_names(names)
                
                for name in athlete_names:
                    medalists.append({
                        'name': name,
                        'medal_type': medal_type,
                        'noc': noc
                    })
        
        return medalists
    
    def _split_concatenated_names(self, text: str) -> List[str]:
        """Split concatenated athlete names.
        
        Args:
            text: Concatenated names
            
        Returns:
            List of individual names
        """
        # Simple heuristic: split on capital letters
        names = re.findall(r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*', text)
        return names if names else [text]
    
    def validate_document(self, document: Dict[str, Any]) -> bool:
        """Validate a document has required fields.
        
        Args:
            document: Document dictionary
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ['doc_id', 'title', 'text']
        
        for field in required_fields:
            if field not in document or not document[field]:
                logger.warning(f"Document missing required field: {field}")
                return False
        
        return True
    
    def validate_question(self, question: Dict[str, Any]) -> bool:
        """Validate a question has required fields.
        
        Args:
            question: Question dictionary
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ['qid', 'question', 'qtype']
        
        for field in required_fields:
            if field not in question or not question[field]:
                logger.warning(f"Question missing required field: {field}")
                return False
        
        return True
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get dataset statistics.
        
        Returns:
            Dictionary with statistics
        """
        stats = {
            'documents': {
                'total': len(self.documents),
                'total_tokens': sum(doc.get('approx_tokens', 0) for doc in self.documents),
                'avg_tokens': sum(doc.get('approx_tokens', 0) for doc in self.documents) / len(self.documents) if self.documents else 0
            },
            'questions': {
                'public': len(self.public_questions),
                'hidden': len(self.hidden_questions),
                'total': len(self.public_questions) + len(self.hidden_questions)
            },
            'question_types': self._get_question_type_distribution()
        }
        
        return stats
    
    def _get_question_type_distribution(self) -> Dict[str, int]:
        """Get distribution of question types.
        
        Returns:
            Dictionary with question type counts
        """
        distribution = {}
        
        for q in self.public_questions:
            qtype = q.get('qtype', 'unknown')
            distribution[qtype] = distribution.get(qtype, 0) + 1
        
        return distribution
    
    def load_all(self) -> Dict[str, Any]:
        """Load all dataset files.
        
        Returns:
            Dictionary with loaded data
        """
        logger.info("Loading all dataset files...")
        
        self.load_corpus()
        self.load_public_questions()
        self.load_hidden_questions()
        
        # Validate data
        valid_docs = [doc for doc in self.documents if self.validate_document(doc)]
        valid_public = [q for q in self.public_questions if self.validate_question(q)]
        valid_hidden = [q for q in self.hidden_questions if self.validate_question(q)]
        
        logger.info(f"Validation: {len(valid_docs)}/{len(self.documents)} valid documents")
        logger.info(f"Validation: {len(valid_public)}/{len(self.public_questions)} valid public questions")
        logger.info(f"Validation: {len(valid_hidden)}/{len(self.hidden_questions)} valid hidden questions")
        
        return {
            'documents': valid_docs,
            'public_questions': valid_public,
            'hidden_questions': valid_hidden,
            'statistics': self.get_statistics()
        }


def main():
    """Test the dataset parser."""
    import sys
    from pathlib import Path
    
    # Paths to hackathon resources (relative to project root)
    project_root = Path(__file__).parent.parent.parent.parent
    corpus_path = project_root / "hackathon-resources" / "corpus" / "corpus.jsonl"
    questions_path = project_root / "hackathon-resources" / "questions"
    
    parser = DatasetParser(str(corpus_path), str(questions_path))
    
    try:
        data = parser.load_all()
        
        print("\n=== Dataset Statistics ===")
        print(json.dumps(data['statistics'], indent=2))
        
        print("\n=== Sample Document ===")
        if data['documents']:
            sample_doc = data['documents'][0]
            event_info = parser.extract_event_info(sample_doc)
            print(json.dumps(event_info, indent=2))
        
        print("\n=== Sample Public Question ===")
        if data['public_questions']:
            print(json.dumps(data['public_questions'][0], indent=2))
        
        print("\n=== Sample Hidden Question ===")
        if data['hidden_questions']:
            print(json.dumps(data['hidden_questions'][0], indent=2))
        
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
