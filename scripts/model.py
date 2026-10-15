"""Deterministic, independently calculated no-vig market probabilities."""
import math

def implied(american):
    if not isinstance(american,(int,float)) or not math.isfinite(american) or abs(american)<100:
        raise ValueError('Invalid American price')
    return 100/(american+100) if american>0 else -american/(-american+100)

def probabilities(odds):
    if len(odds)!=2: raise ValueError('Two-sided winner market required')
    a,b=map(implied,odds)
    return [a/(a+b),b/(a+b)]
