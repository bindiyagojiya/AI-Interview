import math
import re
from typing import List, Dict, Set, Tuple, Optional
from app.schemas.evaluation import EvaluationResult
from app.core.config import settings

class EvaluationService:
    """
    Hybrid Answer Evaluation Engine.
    Combines:
    1. Lexical Baseline: TF-IDF vectorization and Cosine Similarity against benchmark answers.
    2. Concept Coverage: Checks presence of essential technical concepts and keywords.
    3. Rubric Scoring: Evaluates 4 core dimensions (Relevance, Correctness, Completeness, Clarity).
    4. Feedback Engine: Actionable strengths, improvements, and benchmark model response.
    """

    def __init__(self):
        # Common English stop words
        self.stop_words: Set[str] = {
            "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are",
            "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but",
            "by", "can", "could", "did", "do", "does", "doing", "down", "during", "each", "few", "for",
            "from", "further", "had", "has", "have", "having", "he", "her", "here", "hers", "herself",
            "him", "himself", "his", "how", "i", "if", "in", "into", "is", "it", "its", "itself", "just",
            "me", "more", "most", "my", "myself", "no", "nor", "not", "now", "of", "off", "on", "once",
            "only", "or", "other", "our", "ours", "ourselves", "out", "over", "own", "s", "same", "she",
            "should", "so", "some", "such", "than", "that", "the", "their", "theirs", "them", "themselves",
            "then", "there", "these", "they", "this", "those", "through", "to", "too", "under", "until",
            "up", "very", "was", "we", "were", "what", "when", "where", "which", "while", "who", "whom",
            "why", "with", "would", "you", "your", "yours", "yourself", "yourselves"
        }

    def tokenize(self, text: str) -> List[str]:
        """Normalizes and tokenizes text, removing punctuation and stop words."""
        cleaned = re.sub(r"[^\w\s]", " ", text.lower())
        tokens = cleaned.split()
        return [t for t in tokens if t and t not in self.stop_words]

    def compute_tfidf_vector(self, tokens: List[str], idf_dict: Dict[str, float]) -> Dict[str, float]:
        """Computes TF-IDF vector for a list of tokens given an IDF lookup table."""
        if not tokens:
            return {}
        
        # Term Frequency (TF)
        tf: Dict[str, float] = {}
        for token in tokens:
            tf[token] = tf.get(token, 0.0) + 1.0
        
        total_tokens = len(tokens)
        vector: Dict[str, float] = {}
        for token, count in tf.items():
            tf_norm = count / total_tokens
            idf = idf_dict.get(token, 1.0)
            vector[token] = tf_norm * idf
        
        return vector

    def compute_cosine_similarity(self, vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
        """Computes Cosine Similarity between two sparse TF-IDF vectors (returns 0.0 to 1.0)."""
        if not vec1 or not vec2:
            return 0.0

        dot_product = sum(val * vec2.get(k, 0.0) for k, val in vec1.items())
        norm1 = math.sqrt(sum(v * v for v in vec1.values()))
        norm2 = math.sqrt(sum(v * v for v in vec2.values()))

        if norm1 == 0.0 or norm2 == 0.0:
            return 0.0

        return max(0.0, min(1.0, dot_product / (norm1 * norm2)))

    def calculate_tfidf_similarity(self, candidate_answer: str, reference_answer: str) -> float:
        """Computes TF-IDF cosine similarity percentage (0-100) between candidate and reference answer."""
        cand_tokens = self.tokenize(candidate_answer)
        ref_tokens = self.tokenize(reference_answer)

        if not cand_tokens or not ref_tokens:
            return 0.0

        # Build vocabulary from both texts
        corpus = [cand_tokens, ref_tokens]
        num_docs = len(corpus)
        vocab = set(cand_tokens) | set(ref_tokens)

        # Calculate smooth Inverse Document Frequency (IDF)
        idf_dict: Dict[str, float] = {}
        for term in vocab:
            doc_count = sum(1 for doc in corpus if term in doc)
            idf_dict[term] = math.log((num_docs + 1) / (doc_count + 1)) + 1.0

        vec_cand = self.compute_tfidf_vector(cand_tokens, idf_dict)
        vec_ref = self.compute_tfidf_vector(ref_tokens, idf_dict)

        similarity = self.compute_cosine_similarity(vec_cand, vec_ref)
        return round(similarity * 100, 2)

    def extract_missing_concepts(self, candidate_answer: str, key_concepts: List[str]) -> Tuple[List[str], List[str]]:
        """Identifies which key technical concepts were covered and which were missed."""
        cand_lower = candidate_answer.lower()
        covered = []
        missing = []

        for concept in key_concepts:
            concept_clean = concept.strip().lower()
            if not concept_clean:
                continue
            # Check for direct phrase match or all sub-words match
            subwords = [w for w in re.sub(r"[^\w\s]", "", concept_clean).split() if w not in self.stop_words]
            if concept_clean in cand_lower or (subwords and all(w in cand_lower for w in subwords)):
                covered.append(concept)
            else:
                missing.append(concept)

        return covered, missing

    def evaluate(
        self,
        candidate_answer: str,
        reference_answer: str,
        key_concepts: List[str]
    ) -> EvaluationResult:
        """
        Runs full hybrid evaluation:
        1. Checks for empty/trivial input.
        2. Computes TF-IDF cosine baseline.
        3. Analyzes concept coverage.
        4. Calculates rubric scores across 4 dimensions.
        5. Formulates actionable strengths, improvements, and ideal response.
        """
        cleaned_answer = candidate_answer.strip()
        word_count = len(cleaned_answer.split())

        # Handle empty or trivial answers (< 5 words)
        if word_count < 5:
            has_words = word_count > 0
            return EvaluationResult(
                overall_score=8.0 if has_words else 0.0,
                tfidf_score=0.0,
                semantic_score=10.0 if has_words else 0.0,
                correctness_score=0.0,
                relevance_score=15.0 if has_words else 0.0,
                completeness_score=5.0 if has_words else 0.0,
                clarity_score=20.0 if has_words else 0.0,
                missing_concepts=key_concepts,
                feedback_strengths="Attempted to provide an answer." if has_words else "No answer submitted.",
                feedback_improvements="Your response is too brief. Provide a structured explanation covering definitions, mechanics, and concrete examples.",
                model_answer=reference_answer
            )

        # 1. Baseline TF-IDF Score
        tfidf_score = self.calculate_tfidf_similarity(cleaned_answer, reference_answer)

        # 2. Key Concept Analysis
        covered_concepts, missing_concepts = self.extract_missing_concepts(cleaned_answer, key_concepts)
        total_concepts = len(key_concepts) if key_concepts else 1
        concept_coverage_ratio = len(covered_concepts) / total_concepts

        # 3. Rubric Scoring Formulation
        # Relevance: combination of concept presence and TF-IDF overlap
        relevance_score = min(100.0, max(25.0, (concept_coverage_ratio * 55.0) + (tfidf_score * 0.45)))
        
        # Correctness: heavily anchored on concept coverage
        correctness_score = min(100.0, (concept_coverage_ratio * 70.0) + (tfidf_score * 0.30))
        
        # Completeness: concept coverage + adequate length
        length_factor = min(1.0, word_count / 30.0)
        completeness_score = min(100.0, (concept_coverage_ratio * 60.0) + (length_factor * 40.0))
        
        # Clarity: score based on sentence structure & vocabulary length
        clarity_score = 85.0 if word_count >= 15 else 60.0

        # Semantic Score: weighted average across rubrics
        semantic_score = (
            (correctness_score * 0.35) +
            (relevance_score * 0.25) +
            (completeness_score * 0.25) +
            (clarity_score * 0.15)
        )

        # Overall Score: 25% Lexical TF-IDF + 75% Semantic Rubric Understanding
        overall_score = round((tfidf_score * 0.25) + (semantic_score * 0.75), 2)
        overall_score = max(0.0, min(100.0, overall_score))

        # 4. Actionable Feedback Generation
        strengths = []
        if covered_concepts:
            strengths.append(f"Successfully addressed key concepts: {', '.join(covered_concepts)}.")
        if tfidf_score >= 35.0:
            strengths.append("Demonstrated solid relevant vocabulary and technical context.")
        if word_count >= 25:
            strengths.append("Provided a structured and articulate explanation.")
        if not strengths:
            strengths.append("Answer attempted the core question topic.")

        improvements = []
        if missing_concepts:
            improvements.append(f"Missing essential technical topics: {', '.join(missing_concepts)}.")
        if word_count < 20:
            improvements.append("Elaborate further with real-world examples or use-cases.")
        if tfidf_score < 25.0:
            improvements.append("Use standard industry terminology to explain the mechanism clearly.")
        if not improvements:
            improvements.append("Excellent response. For senior rounds, consider discussing edge cases and performance trade-offs.")

        return EvaluationResult(
            overall_score=overall_score,
            tfidf_score=round(tfidf_score, 2),
            semantic_score=round(semantic_score, 2),
            correctness_score=round(correctness_score, 2),
            relevance_score=round(relevance_score, 2),
            completeness_score=round(completeness_score, 2),
            clarity_score=round(clarity_score, 2),
            missing_concepts=missing_concepts,
            feedback_strengths=" ".join(strengths),
            feedback_improvements=" ".join(improvements),
            model_answer=reference_answer
        )

    def generate_follow_up(
        self,
        question_text: str,
        candidate_answer: str,
        missing_concepts: List[str],
        covered_concepts: List[str],
        target_role: str,
        difficulty: str,
        interview_type: str = "Technical"
    ) -> Optional[Dict[str, str]]:
        """
        Analyzes the candidate's response to determine if a clarifying, example-seeking,
        or deep-dive follow-up question is warranted.
        """
        words = candidate_answer.strip().split()
        word_count = len(words)

        # Try Gemini API if configured for live adaptive questioning
        if settings.GEMINI_API_KEY and word_count < 45:
            try:
                import httpx
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={settings.GEMINI_API_KEY}"
                prompt = (
                    f"You are an interviewer interviewing a candidate for {target_role} ({difficulty} level, {interview_type} track).\n"
                    f"Original Question: '{question_text}'\n"
                    f"Candidate Answer: '{candidate_answer}'\n"
                    f"Missing concepts: {missing_concepts}\n"
                    f"Respond with ONLY a single concise, professional follow-up question (1 sentence) probing their answer, requesting a concrete example, or asking for clarification. Do not repeat the original question."
                )
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": 0.3, "maxOutputTokens": 80}
                }
                with httpx.Client(timeout=3.0) as client:
                    resp = client.post(url, json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        gen_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                        if gen_text and len(gen_text) > 10:
                            return {
                                "needed": True,
                                "follow_up_question": gen_text,
                                "follow_up_type": "clarification"
                            }
            except Exception:
                pass

        # Deterministic / Offline Context-Aware Follow-Up Engine
        if word_count < 15:
            if missing_concepts:
                return {
                    "needed": True,
                    "follow_up_question": f"Your response is very brief. Could you unpack your answer further, specifically explaining how '{missing_concepts[0]}' fits into this mechanism?",
                    "follow_up_type": "clarification"
                }
            return {
                "needed": True,
                "follow_up_question": "Can you elaborate on your response with a concrete code snippet or real-world example explaining how this works under the hood?",
                "follow_up_type": "clarification"
            }

        if missing_concepts and (word_count < 40 or len(missing_concepts) >= 2):
            concept = missing_concepts[0]
            if "hr" in interview_type.lower() or "behav" in interview_type.lower():
                return {
                    "needed": True,
                    "follow_up_question": "Interesting point. Could you describe a specific project situation where you personally applied this, and what the measurable outcome was?",
                    "follow_up_type": "example"
                }
            return {
                "needed": True,
                "follow_up_question": f"Good start, but how does '{concept}' relate to this? Could you explain the trade-offs or implementation details in a production system?",
                "follow_up_type": "deep_dive"
            }

        diff_lower = difficulty.lower()
        if ("intermediate" in diff_lower or "advanced" in diff_lower) and word_count < 55:
            return {
                "needed": True,
                "follow_up_question": "How does this behavior hold up under heavy concurrent loads or edge-case failure scenarios, and how would you optimize it?",
                "follow_up_type": "deep_dive"
            }

        return None

evaluation_service = EvaluationService()
