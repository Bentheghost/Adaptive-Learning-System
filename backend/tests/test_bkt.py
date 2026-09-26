"""
Bayesian Knowledge Tracing (BKT) Math Verification Suite
"""
import sys
import os

# Ensure backend root is on sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from knowledge_tracker import KnowledgeTracker

def test_bkt():
    tracker = KnowledgeTracker()
    
    # Initial state
    p_init = 0.20
    print("--- BKT Verification ---")
    print(f"Initial Prior P(L_0): {p_init}")
    
    # Single correct answer test (Beginner level: p_trans=0.25, p_guess=0.30, p_slip=0.10)
    post_corr = tracker.calculate_posterior(p_init, is_correct=True, p_slip=0.10, p_guess=0.30)
    step1_corr = tracker.apply_transition(post_corr, p_trans=0.25)
    print(f"Correct Answer -> Posterior P(L|O=1): {post_corr:.4f} | After Transition P(L_1): {step1_corr:.4f}")
    assert post_corr > p_init, "Posterior should increase after correct answer"
    assert step1_corr > post_corr, "Transition step should increase mastery further"

    # Single incorrect answer test
    post_inc = tracker.calculate_posterior(p_init, is_correct=False, p_slip=0.10, p_guess=0.30)
    step1_inc = tracker.apply_transition(post_inc, p_trans=0.25)
    print(f"Incorrect Answer -> Posterior P(L|O=0): {post_inc:.4f} | After Transition P(L_1): {step1_inc:.4f}")
    assert post_inc < p_init, "Posterior should decrease after incorrect answer"

    # Sequential correct answers test
    mastery = p_init
    print("\n--- Sequential Correct Answers (Beginner) ---")
    for item in range(1, 6):
        mastery = tracker.update_bkt_step(mastery, is_correct=True, difficulty="beginner")
        print(f"Item {item}: Correct -> Mastery: {mastery:.4f}")
    
    assert mastery > 0.85, f"Mastery after 5 correct answers should be high (got {mastery:.4f})"
    
    # Sequential incorrect answers test
    mastery = 0.80
    print("\n--- Sequential Incorrect Answers (Advanced) ---")
    for item in range(1, 5):
        mastery = tracker.update_bkt_step(mastery, is_correct=False, difficulty="advanced")
        print(f"Item {item}: Incorrect -> Mastery: {mastery:.4f}")

    print("\n[SUCCESS] All BKT mathematical assertions passed cleanly!")

if __name__ == "__main__":
    test_bkt()
