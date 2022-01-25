import jsonpatch

src = {'foo': {"1": 'bar'}, 'numbers': [1, 3, 4, 8]}
dst = {'foo': {'qux': '123'}, 'numbers': [1, 4, 7]}
patch = jsonpatch.JsonPatch.from_diff(src, dst)
print(patch)

patch = jsonpatch.make_patch(src, dst)
print(patch)

doc = {}
result = patch.apply(doc)
print(result)