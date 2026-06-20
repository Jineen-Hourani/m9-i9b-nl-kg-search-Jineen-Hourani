"""End-to-end NL-question pipeline against the recipe KG.

Wires `mapper.detect_shape → mapper.extract_slots → mapper.compile_to_cypher
→ driver.session().run(cypher, **params)` into one function. Raises
`UnsupportedQueryError` (fail-loud) when the question is off-template.
"""

from mapper import (
    detect_shape,
    extract_slots,
    compile_to_cypher,
    UnsupportedQueryError,
)


def answer(driver, question: str) -> list[dict]:
    """Answer one NL question by routing through the deterministic mapper.

    Returns a list of result rows (each row a dict whose keys are the
    Cypher RETURN aliases). Raises UnsupportedQueryError when
    detect_shape returns None — surface that to the caller; do not
    swallow it into an empty result list.
    """
    shape = detect_shape(question)
    if shape is None:
        raise UnsupportedQueryError(f"The query '{question}' is out of scope or unsupported.")
        

    slots = extract_slots(question, shape)
    
    
    cypher, params = compile_to_cypher(shape, slots)
    

    results = []
    with driver.session() as session:
        res = session.run(cypher, **params)
        for record in res:
            results.append(record.data())
            
    return results
