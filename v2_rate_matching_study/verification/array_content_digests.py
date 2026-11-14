"""SHA-256 of the content (raw bytes), shape and dtype of every array in the processed input files.
File checksums of .npz files are not comparable between builds (the container stores time stamps); these digests are.
Usage: python3 array_content_digests.py <PROCESSED_DIR> <out.json>   (PROCESSED_DIR holds E3-D/ and E4/)"""
import hashlib, json, sys
from pathlib import Path
import numpy as np
proc, out = Path(sys.argv[1]), sys.argv[2]
res = {}
for arm in ("E3-D", "E4"):
    for k in range(1, 10):
        z = np.load(proc / arm / f"dataset_fold_{k}.npz")
        res[f"{arm}/dataset_fold_{k}"] = {key: dict(shape=list(z[key].shape), dtype=str(z[key].dtype),
                                                     sha256=hashlib.sha256(np.ascontiguousarray(z[key]).tobytes()).hexdigest())
                                          for key in sorted(z.files)}
json.dump(res, open(out, "w"), indent=1); print(len(res), "files")
