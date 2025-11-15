"""Quick helper script to inspect contradiction parsing."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from hegelion_server.dialectics import HegelionEngine

SAMPLE_ANTITHESIS = """
I will now dismantle the security-first position. Each contradiction shows why the thesis collapses in
practice.

**CONTRADICTION 1: The Security Paradox**
EVIDENCE: Absolute surveillance corrodes public trust, which is the substrate of collective safety.

**CONTRADICTION 2: The Misdefinition of "Security"**
EVIDENCE: Limiting safety to physical harms ignores informational, economic, and civic security.

**CONTRADICTION 3: The Flawed "Public Square" Analogy**
EVIDENCE: Treating digital spaces like controllable town squares misreads decentralized networks.

**CONTRADICTION 4: The Impracticality of the "Harm Principle" Justification**
EVIDENCE: A state intrusive enough to inspect every message cannot credibly self-limit to preventing harm.
""".strip()


if __name__ == "__main__":
    contradictions = HegelionEngine._extract_contradictions(SAMPLE_ANTITHESIS)
    print(f"Found {len(contradictions)} contradictions:")
    for idx, item in enumerate(contradictions, start=1):
        print(f"{idx}. {item}")
