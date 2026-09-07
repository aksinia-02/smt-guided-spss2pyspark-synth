from abc import ABC, abstractmethod
from typing import Any, List, Tuple

class BaseCandidateHandler(ABC):
    @abstractmethod
    def select_candidate(self, candidates: List[Tuple[Any, float]]) -> Tuple[Any, float]:
        """
        Given a list of candidates, returns the chosen (best_primitive, top_score) tuple.
        """
        pass

class UserConsoleHandler(BaseCandidateHandler):
    def select_candidate(self, synthesized_expressions: str) -> Tuple[Any, float]:
        """
        Iterates through candidates. 
        Input '1' -> move to the next candidate.
        Input '2' (or anything else) -> accept current candidate.
        """
        for i, exp in enumerate(synthesized_expressions):

            print(f"\n--- Candidate {i + 1}/{len(synthesized_expressions)} ---")

            print(f"{exp}")


            user_input = input("Enter '1' to see next candidate, or '2' to accept: ").strip()
            if user_input == '2':
                return exp
                
        print("\nNo more candidates available. Defaulting to the last candidate.")
        return None


class GecisVerifierHandler(BaseCandidateHandler):
    def __init__(self, verifier_client):
        self.verifier = verifier_client

    def select_candidate(self, candidates):
        # Your GECIS verification logic here
        for candidate in candidates:
            if self.verifier.verify(candidate):
                return candidate
        return candidates[0]