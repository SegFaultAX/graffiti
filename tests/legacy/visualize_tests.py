from graffiti.legacy import visualize
from graffiti.legacy.core import compile_graph

def test_to_graphviz():
    graph = compile_graph({ "a": lambda n: 1 })
    viz = visualize.to_graphviz(graph)

    assert "a" in viz["nodes"]
    assert "n" in viz["nodes"]
    assert ("a", "n") in viz["edges"]
