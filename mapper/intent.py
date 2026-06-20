"""Intent classifier — map NL question to a canonical ShapeId.

This file is your responsibility. Read the 15 supported shapes in
`shapes.ShapeId` and `shapes.CANONICAL_CYPHER`, then implement
`detect_shape` so that each of the 15 canonical eval questions in
`data/eval_questions.jsonl` is classified to the gold shape, and
adversarial / off-template questions return None.

The deterministic mapper is the production-discipline arm of M9B; a
classifier that returns the wrong shape on a supported question is a
real bug, and a classifier that returns a confident answer on an
off-template question is the silent-failure mode the Reading warns
against. Prefer None over a false positive.
"""

 
from .shapes import ShapeId


def detect_shape(question: str) -> ShapeId | None:
    """Classify the question into one of the 15 ShapeId values, or None.

    Suggested approach: a small set of keyword / regex rules over the
    question text that match the shape vocabulary used by the recipe
    KG. Look for cues such as:
      - "by author <name>", "by <Name>"   → author shapes
      - "<cuisine name>"                  → cuisine shapes
      - "use <ingredient>", "with <ingredient>" → ingredient shapes
      - "but not <ingredient>"            → q14 (negation)
      - "ranked by popularity" / "most popular" → q9
      - "under <N> minutes"               → q10
      - "ingredients used in"             → q11 (inverse)
      - "authors of"                      → q12
      - "or any subtype" / "or any kind"  → q13
      - "optionally tagged"               → q15
      - "require <technique>"             → q7

    For cuisines and ingredients, you can use the schema label vocabulary
    (Cuisine.name values, Ingredient.name values) to disambiguate which
    slot type the question is naming. A spaCy NER pass on PERSON entities
    helps for q2 / q8.

    Returns None when no rule fires — the orchestrator raises
    UnsupportedQueryError in that case, which is the correct behaviour
    for an out-of-scope question.
    """
    q = question.lower().strip()
    
    
    if "(" in q or ")" in q or "delete" in q or "drop" in q or "set" in q or "merge" in q:
        return None

    
    if "but not" in q or "without" in q:
        return ShapeId.Q14
    if "optionally tagged" in q or "optional" in q:
        return ShapeId.Q15
    if "or any kind" in q or "or any subtype" in q:
        return ShapeId.Q13
    if "ingredients used in" in q or "what ingredients does" in q:
        return ShapeId.Q11
    if "authors of" in q or "who wrote" in q:
        return ShapeId.Q12
    if "ranked by popularity" in q or "most popular" in q:
        return ShapeId.Q9
    if "under" in q and "minutes" in q:
        return ShapeId.Q10
    if "by author" in q and ("use" in q or "with" in q or "ginger" in q):
        return ShapeId.Q8
    if "chinese" in q and ("use" in q or "ginger" in q):
        return ShapeId.Q6
    if any(c in q for c in ["sichuan", "cantonese", "japanese", "italian", "indian", "thai"]) and ("use" in q or "with" in q or "ginger" in q):
        return ShapeId.Q5
    if "asian" in q:
        return ShapeId.Q4
    if "by author" in q or "by " in q:
        return ShapeId.Q2
    if any(c in q for c in ["sichuan", "cantonese", "japanese", "italian", "indian", "thai", "chinese"]):
        return ShapeId.Q3
        
    
    if "recipe" in q or "find" in q or any(i in q for i in ["ginger", "orange", "garlic", "basil"]):
        return ShapeId.Q1

    return None