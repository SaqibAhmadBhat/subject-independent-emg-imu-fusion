import json, os, sys

results_dir = "results"
exps = ["E1","E2","E3","E4"]
folds = [f"fold_{i}" for i in range(1,10)]

forbidden_keys = {"test_loss","test_acc","val_loss","val_acc"}
required_history_keys = {"train_loss","train_acc"}

errors = []
summary = []

for exp in exps:
    for fold in folds:
        path = os.path.join(results_dir, exp, fold)
        
        for fname in ["model.pt","history.json","meta.json"]:
            fp = os.path.join(path, fname)
            if not os.path.exists(fp):
                errors.append(f"MISSING: {exp}/{fold}/{fname}")
        
        hist_path = os.path.join(path, "history.json")
        try:
            with open(hist_path) as f:
                hist = json.load(f)
            
            for k in required_history_keys:
                if k not in hist:
                    errors.append(f"{exp}/{fold}/history.json: missing key '{k}'")
                elif len(hist[k]) != 50:
                    errors.append(f"{exp}/{fold}/history.json: '{k}' has {len(hist[k])} entries (expected 50)")
            
            for k in forbidden_keys:
                if k in hist:
                    errors.append(f"{exp}/{fold}/history.json: FORBIDDEN key '{k}' found")
            
            n_train_loss = len(hist.get("train_loss", []))
            n_train_acc  = len(hist.get("train_acc", []))
            
        except Exception as e:
            errors.append(f"{exp}/{fold}/history.json: parse error: {e}")
            n_train_loss = n_train_acc = -1
        
        meta_path = os.path.join(path, "meta.json")
        try:
            with open(meta_path) as f:
                meta = json.load(f)
            
            exp_val  = meta.get("experiment","")
            fold_val = meta.get("fold", meta.get("fold_idx",""))
            epochs   = meta.get("epochs", meta.get("num_epochs", ""))
            
            if str(exp_val) != exp:
                errors.append(f"{exp}/{fold}/meta.json: experiment='{exp_val}' expected '{exp}'")
            
            fold_num = int(fold.split("_")[1])
            if int(fold_val) != fold_num:
                errors.append(f"{exp}/{fold}/meta.json: fold='{fold_val}' expected '{fold_num}'")
            
            if int(epochs) != 50:
                errors.append(f"{exp}/{fold}/meta.json: epochs='{epochs}' expected 50")
            
        except Exception as e:
            errors.append(f"{exp}/{fold}/meta.json: parse error: {e}")
        
        summary.append(f"OK  {exp}/{fold}  train_loss={n_train_loss}  train_acc={n_train_acc}")

print("=== PER-FOLD VERIFICATION ===")
for s in summary:
    print(s)

print()
if errors:
    print("=== ERRORS FOUND ===")
    for e in errors:
        print("ERROR:", e)
    sys.exit(1)
else:
    print("=== ALL 36 FOLDS VERIFIED - NO ERRORS ===")
