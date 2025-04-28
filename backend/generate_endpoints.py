import json
import sys

# Usage: python generate_endpoints.py openapi.json > api-endpoints-list.md

def main(spec_path):
    with open(spec_path) as f:
        spec = json.load(f)
    paths = spec.get('paths', {})

    print('# API Endpoint Reference')
    print()
    print('| Method | Path |')
    print('| ------ | ---- |')
    for path, ops in sorted(paths.items()):
        for method in sorted(ops.keys()):
            print(f'| {method.upper():6s} | `{path}` |')

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python generate_endpoints.py openapi.json')
        sys.exit(1)
    main(sys.argv[1])