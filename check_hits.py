import json

results = json.load(open('team_results.json'))
test = json.load(open('public_test_set.json'))

for r, t in zip(results, test):
    expected = t['expected_standards'][0]
    retrieved = r['retrieved_standards']
    hit = any(expected == s for s in retrieved[:3])
    status = "HIT" if hit else "MISS"
    print(f"{r['id']} | {status} | Expected: {expected}")
    if not hit:
        print(f"         Got: {retrieved[:3]}")