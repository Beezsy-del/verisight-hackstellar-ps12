"""Counts from one labelled prediction run; undefined ratios are unavailable, not zero."""
import math

def threshold_metrics(labels, scores, threshold):
    if len(labels) != len(scores) or not math.isfinite(threshold) or not 0 <= threshold <= 1:
        raise ValueError("Invalid evaluation inputs")
    counts = dict(tp=0, fp=0, tn=0, fn=0)
    for label, score in zip(labels, scores):
        if label not in (0,1) or not math.isfinite(score) or not 0 <= score <= 1:
            raise ValueError("Invalid label or score")
        predicted = score >= threshold
        counts["tp" if label and predicted else "fn" if label else "fp" if predicted else "tn"] += 1
    tp, fp, tn, fn = (counts[k] for k in ("tp","fp","tn","fn"))
    def ratio(a,b): return a/b if b else None
    return dict(counts, threshold=threshold, sensitivity=ratio(tp,tp+fn), specificity=ratio(tn,tn+fp), precision=ratio(tp,tp+fp), fpr=ratio(fp,fp+tn), fnr=ratio(fn,fn+tp))
