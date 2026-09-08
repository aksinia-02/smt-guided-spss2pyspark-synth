from typing import List
from primitives.Primitive import Primitive

class SemanticMatcher:
    @staticmethod
    def match_score(decoded_spec: dict, prim: Primitive) -> float:
        """
        Calculates a semantic match score between a decoded SPSS parameter
        and a primitive. Returns 0.0 if incompatible.

        decoded_spec: A dictionary containing the decoded SPSS parameter specification.
        prim: A Primitive object representing a candidate primitive.
        """

        sem = prim.semantics
        score = 1.0

        def print_remove(type: str):
            return
            print(f"removed with {type} filter")
            print(decoded_spec)
            print(sem)

        # Direction Match
        # If the direction is specified in either the decoded spec or the primitive semantics, they must match
        if decoded_spec.direction != sem.direction:
            if decoded_spec.direction is not None or sem.direction is not None:
                print_remove("direction")
                return 0.0

        # Target Type Match
        # If both the decoded spec and the primitive semantics have a target type, they must be compatible
        decoded_type = decoded_spec.target_type
        if decoded_type and sem.target_type:
            dev_score = sem.target_type.eq_score(decoded_type)
            if dev_score == 0:
                return 0
            else:
                score += dev_score * 100

        # Unit Match
        # If both the decoded spec and the primitive semantics have a unit, they must match
        # Example: "week" vs "day" would not match, but "day" vs "day" would.
        if decoded_spec.unit and sem.unit:
            decoded_unit = str(decoded_spec.unit).lower()
            if decoded_unit != str(sem.unit.value).lower():
                print_remove("unit")
                return 0.0

        # Jump Match
        # If either the decoded spec or the primitive semantics has a jump specification, they must match
        if decoded_spec.jump or sem.jump:
            if decoded_spec.jump != sem.jump:
                print_remove("jump")
                return 0.0

        # Amount Match
        # 
        decoded_amount = decoded_spec.amount
        if decoded_amount is not None:
            if sem.amount is not None:
                # Fixed primitive (e.g. minus_30days)
                if sem.amount != decoded_amount:
                    print_remove("amount")
                    return 0.0
                score += 2.0
            else:
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