from graffiti.legacy import keys

def test_expand_key_default():
    simple = keys.expand_key("a__b", 1)
    assert simple == { "a": { "b": 1 } }

def test_expand_key_custom_separator():
    separator = keys.expand_key("a.b", 1, ".")
    assert separator == { "a": { "b": 1 } }

def test_expand_keys_single():
    single = keys.expand_keys({ "a__b": 1})
    assert single == {"a": { "b": 1 } }

def test_expand_keys_multiple():
    multiple = keys.expand_keys({ "a__b": 1, "c__d": 2 })
    assert multiple == { "a": { "b": 1 }, "c": { "d": 2 } }

def test_expand_keys_merged_keys():
    merged = keys.expand_keys({ "a__b": 1, "a__c": 2 })
    assert merged == { "a": { "b": 1, "c": 2 } }

def test_expand_keys_override_keys():
    merged = keys.expand_keys({ "a__b": 1, "a__b": 2 })
    assert merged == { "a": { "b": 2 } }

def test_simplify_flat():
    flat = keys.simplify({ "a": 1 })
    assert flat == { "a": 1 }

def test_simplify_nested():
    nested = keys.simplify({ "a": { "b": 1 } })
    assert nested == { "a__b": 1}

def test_simplify_deep_nested():
    deep = keys.simplify({ "a": { "b": { "c": { "d": 1 } } } })
    assert deep == { "a__b__c__d": 1 }

def test_simplify_multiple_root():
    multi = keys.simplify({ "a": { "b": 1 }, "c": { "d": 2 } })
    assert multi == { "a__b": 1, "c__d": 2 }

def test_desimplify_flat():
    flat = keys.desimplify({ "a__b": 1})
    assert flat == { "a": { "b": 1 } }

def test_desimplify_nested():
    nested = keys.desimplify({ "a__b__c__d": 1 })
    assert nested == { "a": { "b": { "c": { "d": 1 } } } }

def test_desimplify_subkey():
    nested = keys.desimplify({ "a__b": { "c__d": 1 } })
    assert nested == { "a": { "b": { "c__d": 1 } }}

def test_desimplify_recursive():
    nested = keys.desimplify({ "a__b": { "c__d": 1 } }, recursive=True)
    assert nested == { "a": { "b": { "c": { "d": 1 } } }}

