from reasoner_pydantic import Attribute, Message


# Some sample attributes
ATTRIBUTE_A = Attribute.model_validate(
    {
        "attribute_type_id": "biolink:knowledge_source",
        "value": "https://automat.renci.org/",
        "attributes": [
            {"attribute_type_id": "biolink:publication", "value": "pubmed_central"},
            {"attribute_type_id": "biolink:has_p-value_evidence", "value": 0.04},
        ],
    }
)

ATTRIBUTE_B = Attribute.model_validate(
    {
        "attribute_type_id": "biolink:publication",
        "value": "pubmed_central",
        "attributes": [
            {"attribute_type_id": "biolink:has_original_source", "value": True},
        ],
    }
)


def test_result_merging():
    """Test that duplicate results and analyses are merged correctly"""

    message = {
        "knowledge_graph": {
            "nodes": {},
            "edges": {
                "ke0": {
                    "subject": "kn0",
                    "object": "kn1",
                    "predicate": "biolink:ameliorates",
                    "sources": [
                        {
                            "resource_id": "kp0",
                            "resource_role": "primary_knowledge_source",
                        }
                    ],
                    "attributes": [],
                },
                "ke1": {
                    "subject": "kn0",
                    "object": "kn1",
                    "predicate": "biolink:ameliorates",
                    "sources": [
                        {
                            "resource_id": "kp1",
                            "resource_role": "primary_knowledge_source",
                        }
                    ],
                    "attributes": [],
                },
            },
        },
        "results": [
            {
                "node_bindings": {"n0": [{"id": "kn0", "attributes": []}]},
                "analyses": [
                    {
                        "resource_id": "ara0",
                        "edge_bindings": {"e0": [{"id": "ke0", "attributes": []}]},
                        "attributes": [],
                    }
                ],
            },
            {
                "node_bindings": {"n0": [{"id": "kn0", "attributes": []}]},
                "analyses": [
                    {
                        "resource_id": "ara0",
                        "edge_bindings": {"e0": [{"id": "ke0", "attributes": []}]},
                        "attributes": [],
                    },
                    {
                        "resource_id": "ara1",
                        "edge_bindings": {"e0": [{"id": "ke0", "attributes": []}]},
                        "attributes": [],
                    },
                ],
            },
        ],
    }

    m = Message.model_validate(message)
    assert m.results is not None
    assert len(m.results) == 1
    assert len(next(iter(m.results)).analyses) == 2


def test_different_result_merging():
    """Test that different results are not merged"""

    message = {
        "knowledge_graph": {
            "nodes": {},
            "edges": {
                "ke0": {
                    "subject": "kn0",
                    "object": "kn1",
                    "predicate": "biolink:ameliorates",
                    "sources": [
                        {
                            "resource_id": "kp0",
                            "resource_role": "primary_knowledge_source",
                        }
                    ],
                    "attributes": [],
                },
                "ke1": {
                    "subject": "kn0",
                    "object": "kn1",
                    "predicate": "biolink:ameliorates",
                    "sources": [
                        {
                            "resource_id": "kp1",
                            "resource_role": "primary_knowledge_source",
                        }
                    ],
                    "attributes": [],
                },
            },
        },
        "results": [
            {
                "node_bindings": {"n0": [{"id": "kn0", "attributes": []}]},
                "analyses": [
                    {
                        "resource_id": "ara0",
                        "edge_bindings": {"e0": [{"id": "ke0", "attributes": []}]},
                        "attributes": [],
                    }
                ],
            },
            {
                "node_bindings": {"n0": [{"id": "kn1", "attributes": []}]},
                "analyses": [
                    {
                        "resource_id": "ara0",
                        "edge_bindings": {"e0": [{"id": "ke0", "attributes": []}]},
                        "attributes": [],
                    },
                    {
                        "resource_id": "ara1",
                        "edge_bindings": {"e0": [{"id": "ke0", "attributes": []}]},
                        "attributes": [],
                    },
                ],
            },
        ],
    }
    m = Message.model_validate(message)
    assert len(m.results) == 2


def test_deduplicate_results_out_of_order():
    """
    Test that we successfully deduplicate results when given
    the same results but in a different order
    """

    message = {
        "knowledge_graph": {
            "nodes": {},
            "edges": {
                "ke0": {
                    "subject": "kn0",
                    "object": "kn1",
                    "predicate": "biolink:ameliorates",
                    "sources": [
                        {
                            "resource_id": "kp0",
                            "resource_role": "primary_knowledge_source",
                        }
                    ],
                    "attributes": [],
                },
                "ke1": {
                    "subject": "kn0",
                    "object": "kn1",
                    "predicate": "biolink:ameliorates",
                    "sources": [
                        {
                            "resource_id": "kp1",
                            "resource_role": "primary_knowledge_source",
                        }
                    ],
                    "attributes": [],
                },
            },
        },
        "results": [
            {
                "node_bindings": {
                    "a": [
                        {"id": "MONDO:0011122", "attributes": []},
                        {"id": "CHEBI:88916", "attributes": []},
                    ]
                },
                "analyses": [
                    {
                        "resource_id": "ara0",
                        "edge_bindings": {"e0": [{"id": "ke0", "attributes": []}]},
                        "attributes": [],
                    }
                ],
            },
            {
                "node_bindings": {
                    "a": [
                        {"id": "CHEBI:88916", "attributes": []},
                        {"id": "MONDO:0011122", "attributes": []},
                    ],
                },
                "analyses": [
                    {
                        "resource_id": "ara0",
                        "edge_bindings": {"e0": [{"id": "ke0", "attributes": []}]},
                        "attributes": [],
                    },
                    {
                        "resource_id": "ara1",
                        "edge_bindings": {"e0": [{"id": "ke0", "attributes": []}]},
                        "attributes": [],
                    },
                ],
            },
        ],
    }

    m = Message.model_validate(message)
    assert m.results is not None
    assert len(m.results) == 1


def test_deduplicate_results_different():
    """
    Test that we don't deduplicate results when given
    different binding information
    """

    message = {
        "knowledge_graph": {"nodes": {}, "edges": {}},
        "results": [
            {
                "node_bindings": {
                    "b": [
                        {"id": "CHEBI:88916", "attributes": []},
                        {"id": "MONDO:0011122", "attributes": []},
                    ],
                },
                "analyses": [],
            },
            {
                "node_bindings": {
                    "a": [
                        {"id": "MONDO:0011122", "attributes": []},
                        {"id": "CHEBI:88916", "attributes": []},
                    ],
                },
                "analyses": [],
            },
        ],
    }

    m = Message.model_validate(message)
    assert m.results is not None
    assert len(m.results) == 2


def test_merge_knowledge_graph_nodes():
    """
    Test that we do a smart merge when given knowledge
    graph nodes with the same keys
    """

    message_a = {
        "knowledge_graph": {
            "nodes": {
                "MONDO:1": {
                    "name": "Ebola",
                    "categories": ["biolink:Disease"],
                    "attributes": [ATTRIBUTE_A],
                }
            },
            "edges": {},
        },
        "results": [],
    }

    message_b = {
        "knowledge_graph": {
            "nodes": {
                "MONDO:1": {
                    "name": "Ebola Hemorrhagic Fever",
                    "categories": ["biolink:DiseaseOrPhenotypicFeature"],
                    "attributes": [ATTRIBUTE_B],
                }
            },
            "edges": {},
        },
        "results": [],
    }

    m = Message()

    m.update(Message.model_validate(message_a))
    m.update(Message.model_validate(message_b))

    # Validate output
    assert m.knowledge_graph is not None
    nodes = m.knowledge_graph.nodes
    assert len(nodes) == 1
    node = next(iter(nodes.values()))

    assert ATTRIBUTE_A in node.attributes
    assert ATTRIBUTE_B in node.attributes


def test_normalize_knowledge_graph_edges():
    """
    Test that KG edge IDs are normalized, so even if we pass
    in edges with the same name they are not merged by default
    """

    message_a = {
        "knowledge_graph": {
            "nodes": {
                "MONDO:1": {"categories": ["biolink:NamedThing"], "attributes": []},
                "CHEBI:1": {"categories": ["biolink:NamedThing"], "attributes": []},
            },
            "edges": {
                "n0n1": {
                    "subject": "MONDO:1",
                    "object": "CHEBI:1",
                    "predicate": "biolink:treated_by",
                    "attributes": [ATTRIBUTE_A],
                    "sources": [
                        {
                            "resource_id": "kp0",
                            "resource_role": "primary_knowledge_source",
                        }
                    ],
                }
            },
        },
        "results": [
            {
                "node_bindings": {},
                "analyses": [
                    {
                        "resource_id": "ara0",
                        "edge_bindings": {"qe0": [{"id": "n0n1", "attributes": []}]},
                    }
                ],
            }
        ],
    }

    message_b = {
        "knowledge_graph": {
            "nodes": {
                "MONDO:1": {"categories": ["biolink:NamedThing"], "attributes": []},
                "CHEBI:1": {"categories": ["biolink:NamedThing"], "attributes": []},
            },
            "edges": {
                "n0n1": {
                    "subject": "MONDO:1",
                    "object": "CHEBI:1",
                    "predicate": "biolink:treated_by",
                    "attributes": [ATTRIBUTE_B],
                    "sources": [
                        {
                            "resource_id": "kp1",
                            "resource_role": "primary_knowledge_source",
                        }
                    ],
                }
            },
        },
        "results": [],
    }

    m = Message()

    m_a = Message.model_validate(message_a)
    m_b = Message.model_validate(message_b)

    m.update(m_a)
    m.update(m_b)

    # Check that we didn't combine edges
    assert m.knowledge_graph is not None
    edges = m.knowledge_graph.edges
    assert len(edges) == 2

    # Check that the result was updated to point to the correct edge
    edge_id, edge = next(iter(edges.items()))
    assert m.results is not None
    result = next(iter(m.results))
    analysis = next(iter(result.analyses))
    assert next(iter(analysis.edge_bindings["qe0"])).id == edge_id


def test_merge_identical_attributes():
    """
    Tests that identical attributes are merged
    """

    message_a = {
        "knowledge_graph": {
            "nodes": {
                "MONDO:1": {
                    "name": "Ebola",
                    "categories": ["biolink:Disease"],
                    "attributes": [ATTRIBUTE_A],
                }
            },
            "edges": {},
        },
        "results": [],
    }

    message_b = {
        "knowledge_graph": {
            "nodes": {
                "MONDO:1": {
                    "name": "Ebola Hemorrhagic Fever",
                    "categories": ["biolink:DiseaseOrPhenotypicFeature"],
                    "attributes": [ATTRIBUTE_A],
                }
            },
            "edges": {},
        },
        "results": [],
    }

    m = Message()

    m.update(Message.model_validate(message_a))

    print(m)
    print()

    m.update(Message.model_validate(message_b))

    print(m)
    # Validate output
    assert m.knowledge_graph is not None
    nodes = m.knowledge_graph.nodes
    assert len(nodes) == 1
    node = next(iter(nodes.values()))

    assert ATTRIBUTE_A in node.attributes
    assert len(node.attributes) == 1


def test_merge_knowledge_graph_edges():
    """
    Test that knowledge graph edges are merged properly
    """

    message_a = {
        "knowledge_graph": {
            "nodes": {},
            "edges": {
                "ke0": {
                    "subject": "kn0",
                    "object": "kn1",
                    "predicate": "biolink:ameliorates",
                    "sources": [
                        {
                            "resource_id": "ks0",
                            "resource_role": "primary_knowledge_source",
                        },
                        {
                            "resource_id": "kp0",
                            "resource_role": "aggregator_knowledge_source",
                            "upstream_resource_ids": ["ks0"],
                        },
                        {
                            "resource_id": "ara0",
                            "resource_role": "aggregator_knowledge_source",
                            "upstream_resource_ids": ["kp0"],
                        },
                    ],
                    "attributes": [
                        {
                            "attribute_type_id": "biolink:agent_type",
                            "value": "automated_agent",
                        }
                    ],
                }
            },
        },
        "results": [],
    }

    message_b = {
        "knowledge_graph": {
            "nodes": {},
            "edges": {
                "ke0": {
                    "subject": "kn0",
                    "object": "kn1",
                    "predicate": "biolink:ameliorates",
                    "sources": [
                        {
                            "resource_id": "ks0",
                            "resource_role": "primary_knowledge_source",
                        },
                        {
                            "resource_id": "kp1",
                            "resource_role": "aggregator_knowledge_source",
                            "upstream_resource_ids": ["ks0"],
                        },
                        {
                            "resource_id": "ara0",
                            "resource_role": "aggregator_knowledge_source",
                            "upstream_resource_ids": ["kp1"],
                        },
                    ],
                    "attributes": [
                        {
                            "attribute_type_id": "biolink:agent_type",
                            "value": "automated_agent",
                        }
                    ],
                }
            },
        },
        "results": [],
    }

    m = Message()

    m.update(Message.model_validate(message_a))
    m.update(Message.model_validate(message_b))

    assert m.knowledge_graph is not None
    edges = m.knowledge_graph.edges
    assert len(edges) == 1
    edge = next(iter(edges.values()))

    sources = edge.sources
    assert len(sources) == 4
    for source in sources:
        if source.resource_id == "ara0":
            assert source.upstream_resource_ids is not None
            assert len(source.upstream_resource_ids) == 2
