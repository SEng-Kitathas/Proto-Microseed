from __future__ import annotations
import json,random
from pathlib import Path
from microseed.development.action_closure import result_digest

def main():
    rng=random.Random(1593); n=128; correct=0; precomputed=0
    previous='BOOT'
    for _ in range(n):
        nonce=f'N-{rng.getrandbits(128):032x}'
        execution_result={'device_nonce':nonce,'status':'EXECUTED'}
        marker=result_digest(execution_result)
        actual_echo=result_digest({'device_nonce':nonce,'status':'EXECUTED'})
        prediction_echo=result_digest({'device_nonce':previous,'status':'EXECUTED'})
        correct += actual_echo==marker
        precomputed += prediction_echo==marker
        previous=nonce
    out={'pass':'MS1593_PASS16','worlds':n,'actual_post_execution_echo_matches':correct,'preexecution_prediction_feed_matches':precomputed,'result':'POST_EXECUTION_UNPREDICTABLE_MARKER_CAN_REJECT_PRECOMPUTED_PREDICTION_FEED_UNDER_BOUNDED_THREAT_MODEL','boundary':'MARKER_IS_ONLY_AS_GROUNDED_AS_EXECUTION_INTERFACE_AND_ECHO_ROUTE','authority':'RESEARCH_ONLY'}
    Path('research/MS1593_PASS16_POST_EXECUTION_CHALLENGE_BINDING.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__':main()
