import re
import time
from typing import List, Dict, Tuple, Optional
from sqlalchemy.orm import Session
from models.knowledge_base import Document, DocumentChunk
import json

class DocumentProcessor:
    """Service for processing and chunking documents for RAG system"""
    
    def __init__(self):
        self.default_chunk_size = 1000
        self.default_overlap = 200
        
        # ReckonSales-specific keywords for better chunking
        self.section_markers = [
            'step', 'procedure', 'guide', 'how to', 'error', 'solution',
            'billing', 'invoice', 'gst', 'inventory', 'order', 'customer',
            'pharmacy', 'auto parts', 'fmcg', 'restaurant'
        ]
    
    def chunk_document(self, text: str, chunk_size: int = None, overlap: int = None) -> List[Dict]:
        """
        Split document text into overlapping chunks optimized for RAG retrieval
        
        Args:
            text: Document content to chunk
            chunk_size: Maximum characters per chunk
            overlap: Characters to overlap between chunks
            
        Returns:
            List of chunk dictionaries with text, index, and metadata
        """
        chunk_size = chunk_size or self.default_chunk_size
        overlap = overlap or self.default_overlap
        
        if overlap >= chunk_size:
            overlap = chunk_size // 4  # Ensure overlap is reasonable
        
        # Clean and normalize text
        text = self._clean_text(text)
        
        # Try intelligent chunking first (by sections/paragraphs)
        chunks = self._intelligent_chunking(text, chunk_size, overlap)
        
        # If intelligent chunking fails, fall back to simple chunking
        if not chunks:
            chunks = self._simple_chunking(text, chunk_size, overlap)
        
        # Post-process chunks
        return self._post_process_chunks(chunks)
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize document text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters that might interfere with chunking
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\"\'\/\@\#\$\%\&\*\+\=]', '', text)
        
        # Ensure proper spacing after punctuation
        text = re.sub(r'([.!?])([A-Z])', r'\1 \2', text)
        
        return text.strip()
    
    def _intelligent_chunking(self, text: str, chunk_size: int, overlap: int) -> List[Dict]:
        """
        Attempt to chunk text intelligently by sections, paragraphs, and sentences
        """
        chunks = []
        
        # Split by double newlines (paragraphs) first
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        current_chunk = ""
        chunk_index = 0
        
        for paragraph in paragraphs:
            # If adding this paragraph would exceed chunk size
            if len(current_chunk) + len(paragraph) > chunk_size:
                if current_chunk:
                    # Save current chunk
                    chunks.append({
                        'text': current_chunk.strip(),
                        'index': chunk_index,
                        'size': len(current_chunk),
                        'section_title': self._extract_section_title(current_chunk)
                    })
                    chunk_index += 1
                    
                    # Start new chunk with overlap
                    overlap_text = self._get_overlap_text(current_chunk, overlap)
                    current_chunk = overlap_text
                
                # Handle very large paragraphs
                if len(paragraph) > chunk_size:
                    # Split large paragraph by sentences
                    sentences = self._split_by_sentences(paragraph)
                    for sentence in sentences:
                        if len(current_chunk) + len(sentence) > chunk_size:
                            if current_chunk:
                                chunks.append({
                                    'text': current_chunk.strip(),
                                    'index': chunk_index,
                                    'size': len(current_chunk),
                                    'section_title': self._extract_section_title(current_chunk)
                                })
                                chunk_index += 1
                                overlap_text = self._get_overlap_text(current_chunk, overlap)
                                current_chunk = overlap_text
                        
                        current_chunk += " " + sentence if current_chunk else sentence
                else:
                    current_chunk += " " + paragraph if current_chunk else paragraph
            else:
                current_chunk += " " + paragraph if current_chunk else paragraph
        
        # Add final chunk
        if current_chunk.strip():
            chunks.append({
                'text': current_chunk.strip(),
                'index': chunk_index,
                'size': len(current_chunk),
                'section_title': self._extract_section_title(current_chunk)
            })
        
        return chunks
    
    def _simple_chunking(self, text: str, chunk_size: int, overlap: int) -> List[Dict]:
        """
        Fallback: Simple sliding window chunking
        """
        chunks = []
        start = 0
        chunk_index = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk_text = text[start:end]
            
            # Try to end at a word boundary
            if end < len(text):
                last_space = chunk_text.rfind(' ')
                if last_space > chunk_size * 0.8:  # Only adjust if we don't lose too much
                    chunk_text = chunk_text[:last_space]
                    end = start + last_space
            
            chunks.append({
                'text': chunk_text.strip(),
                'index': chunk_index,
                'size': len(chunk_text),
                'section_title': self._extract_section_title(chunk_text)
            })
            
            chunk_index += 1
            start = end - overlap
        
        return chunks
    
    def _split_by_sentences(self, text: str) -> List[str]:
        """Split text by sentences"""
        # Simple sentence splitting (can be improved with nltk)
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _get_overlap_text(self, text: str, overlap: int) -> str:
        """Get the last 'overlap' characters for chunk overlap"""
        if len(text) <= overlap:
            return text
        
        overlap_text = text[-overlap:]
        
        # Try to start from a word boundary
        first_space = overlap_text.find(' ')
        if first_space > 0:
            overlap_text = overlap_text[first_space + 1:]
        
        return overlap_text
    
    def _extract_section_title(self, text: str) -> Optional[str]:
        """
        Try to extract a section title from the chunk text
        """
        lines = text.split('\n')
        first_line = lines[0].strip()
        
        # Check if first line looks like a title (short, has keywords)
        if len(first_line) < 100 and any(marker in first_line.lower() for marker in self.section_markers):
            return first_line
        
        # Look for numbered steps or procedures
        step_match = re.match(r'^(step\s+\d+|procedure\s+\d+|\d+\.\s*)', first_line, re.IGNORECASE)
        if step_match:
            return first_line
        
        return None
    
    def _post_process_chunks(self, chunks: List[Dict]) -> List[Dict]:
        """
        Post-process chunks to add metadata and improve quality
        """
        processed_chunks = []
        
        for chunk in chunks:
            # Extract keywords
            keywords = self._extract_keywords(chunk['text'])
            
            # Calculate confidence score based on content quality
            confidence = self._calculate_confidence_score(chunk['text'])
            
            processed_chunk = {
                **chunk,
                'keywords': ', '.join(keywords) if keywords else None,
                'confidence_score': confidence,
                'overlap_with_previous': 0  # Will be set when saving to DB
            }
            
            processed_chunks.append(processed_chunk)
        
        # Set overlap information
        for i in range(1, len(processed_chunks)):
            prev_chunk = processed_chunks[i - 1]['text']
            current_chunk = processed_chunks[i]['text']
            
            # Calculate actual overlap
            overlap = self._calculate_text_overlap(prev_chunk, current_chunk)
            processed_chunks[i]['overlap_with_previous'] = overlap
        
        return processed_chunks
    
    def _extract_keywords(self, text: str) -> List[str]:
        """
        Extract relevant keywords from chunk text
        """
        keywords = []
        text_lower = text.lower()
        
        # ReckonSales-specific keywords
        reckon_keywords = [
            'billing', 'invoice', 'gst', 'tax', 'payment', 'receipt',
            'inventory', 'stock', 'product', 'item', 'quantity',
            'order', 'purchase', 'sale', 'customer', 'supplier',
            'pharmacy', 'medicine', 'prescription', 'patient',
            'auto parts', 'vehicle', 'spare parts', 'garage',
            'fmcg', 'grocery', 'supermarket', 'retail',
            'restaurant', 'menu', 'table', 'kitchen',
            'error', 'solution', 'fix', 'troubleshoot',
            'setup', 'configuration', 'installation',
            'report', 'analytics', 'dashboard', 'export'
        ]
        
        for keyword in reckon_keywords:
            if keyword in text_lower:
                keywords.append(keyword)
        
        # Extract procedural keywords
        if re.search(r'\b(step|procedure|how to|guide)\b', text_lower):
            keywords.append('procedure')
        
        if re.search(r'\b(error|problem|issue)\b', text_lower):
            keywords.append('troubleshooting')
        
        return list(set(keywords))  # Remove duplicates
    
    def _calculate_confidence_score(self, text: str) -> float:
        """
        Calculate a confidence score for the chunk quality (0.0 to 1.0)
        """
        score = 0.5  # Base score
        
        # Bonus for reasonable length
        if 100 <= len(text) <= 2000:
            score += 0.2
        
        # Bonus for having ReckonSales keywords
        text_lower = text.lower()
        keyword_count = sum(1 for kw in ['billing', 'inventory', 'order', 'customer', 'gst'] 
                          if kw in text_lower)
        score += min(keyword_count * 0.1, 0.3)
        
        # Bonus for structured content (steps, procedures)
        if re.search(r'\b(step\s+\d+|procedure|how to)\b', text_lower, re.IGNORECASE):
            score += 0.1
        
        # Penalty for very short or very long chunks
        if len(text) < 50:
            score -= 0.2
        elif len(text) > 3000:
            score -= 0.1
        
        return max(0.0, min(1.0, score))
    
    def _calculate_text_overlap(self, text1: str, text2: str) -> int:
        """
        Calculate character overlap between two text chunks
        """
        # Simple approach: find common suffix of text1 and prefix of text2
        max_overlap = min(len(text1), len(text2), 500)  # Limit search
        
        for i in range(max_overlap, 0, -1):
            if text1[-i:] == text2[:i]:
                return i
        
        return 0
    
    def save_document_with_chunks(self, 
                                 db: Session, 
                                 title: str,
                                 content: str,
                                 document_type: str,
                                 industry_type: str = None,
                                 language: str = "en",
                                 chunk_size: int = None,
                                 chunk_overlap: int = None) -> Tuple[Document, List[DocumentChunk], int]:
        """
        Save document and its chunks to database
        
        Returns:
            Tuple of (document, chunks, processing_time_ms)
        """
        start_time = time.time()
        
        # Create document
        document = Document(
            title=title,
            content=content,
            document_type=document_type,
            industry_type=industry_type,
            language=language,
            file_size=len(content)
        )
        
        db.add(document)
        db.commit()
        db.refresh(document)
        
        # Process and save chunks
        chunks_data = self.chunk_document(content, chunk_size, chunk_overlap)
        
        chunk_objects = []
        for chunk_data in chunks_data:
            chunk = DocumentChunk(
                document_id=document.id,
                chunk_text=chunk_data['text'],
                chunk_index=chunk_data['index'],
                chunk_size=chunk_data['size'],
                overlap_with_previous=chunk_data['overlap_with_previous'],
                keywords=chunk_data.get('keywords'),
                section_title=chunk_data.get('section_title'),
                confidence_score=chunk_data.get('confidence_score')
            )
            chunk_objects.append(chunk)
        
        db.add_all(chunk_objects)
        db.commit()
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return document, chunk_objects, processing_time