# app/aggregator.py
from typing import List, Dict

def aggregate_topics(list_of_maps: List[Dict[str,int]]) -> Dict[str,int]:
    out = {}
    for m in list_of_maps:
        for k,v in m.items():
            out[k] = out.get(k,0) + int(v)
    return out
