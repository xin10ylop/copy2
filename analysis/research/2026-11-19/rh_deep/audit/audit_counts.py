import glob,gzip,json,collections,sys
c=collections.Counter()
for f in glob.glob(sys.argv[1]+"/logs_*.json.gz"):
    n=len(json.load(gzip.open(f))); c[n]+=1
top=sorted(c.items(), key=lambda x:-x[0])[:8]; print("largest chunk sizes (logs: files):", top); print("files with a round count:", {k:v for k,v in c.items() if k in (1000,2000,5000,10000,20000,50000)})
