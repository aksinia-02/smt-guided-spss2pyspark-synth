from typing import List
from invariants import Primitive

class SemanticMatcher:
    @staticmethod
    def match_score(decoded_spec: dict, prim: Primitive) -> float:
        """
        Calculates a semantic match score between a decoded SPSS parameter
        and a primitive. Returns 0.0 if incompatible.
        """
        sem = prim.semantics
        score = 1.0

        # 1. Target Type Match (Strict)
        decoded_type = decoded_spec.target_type
        if decoded_type and sem.target_type:
            # Map decoded string types to DateType enum if necessary
            if str(decoded_type).lower() != str(sem.target_type.value).lower():
                return 0.0

        # 2. Direction Match
        if decoded_spec.direction != sem.direction:
            if decoded_spec.direction is not None or sem.direction is not None:
                return 0.0

        # 3. Unit Match
        if decoded_spec.unit and sem.unit:
            decoded_unit = str(decoded_spec.unit).lower()
            if decoded_unit != str(sem.unit.value).lower():
                return 0.0

        # 4. Jump / Ultimo Match
        if decoded_spec.jump != sem.jump:
            return 0.0

        # 5. Amount Match (Fixed vs Dynamic)
        decoded_amount = decoded_spec.amount
        if decoded_amount is not None:
            if sem.amount is not None:
                # Fixed primitive (e.g. minus_30days)
                if sem.amount != decoded_amount:
                    return 0.0
                score += 2.0  # Prefer exact fixed primitive match
            else:
                # Dynamic primitive needing argument instantiation (e.g., minus_day(30))
                score += 1.0

        return score

    @classmethod
    def filter_candidates(cls, decoded_spec: dict, primitives: List[Primitive]) -> List[tuple[Primitive, float]]:
        """Returns sorted candidate primitives with non-zero match scores."""
        scored = []
        for p in primitives:
            score = cls.match_score(decoded_spec, p)
            if score > 0.0:
                scored.append((p, score))
        return sorted(scored, key=lambda x: x[1], reverse=True)