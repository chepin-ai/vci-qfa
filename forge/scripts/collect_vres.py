import json, sys
p = '/tmp/vres.json'
d = json.load(open(p)) if __import__('os').path.exists(p) else {}
d[sys.argv[1]] = int(sys.argv[2])
json.dump(d, open(p, 'w'))
