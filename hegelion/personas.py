"""Standard critic personas for Hegelion dialectics."""

from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class Persona:
    """A critic persona definition."""

    name: str
    description: str
    focus: str
    instructions: str


# Standard Council of Critics
LOGICIAN = Persona(
    name="The Logician",
    description="Expert in logical consistency and formal reasoning",
    focus="logical fallacies, internal contradictions, invalid inferences, missing premises",
    instructions="Identify logical flaws. Focus on structure and validity of arguments, not the premises themselves.",
)

EMPIRICIST = Persona(
    name="The Empiricist",
    description="Expert in evidence, facts, and empirical grounding",
    focus="factual errors, unsupported claims, missing evidence, contradictions with established science",
    instructions="Identify factual inaccuracies or lack of evidence. Require empirical proof for claims.",
)

ETHICIST = Persona(
    name="The Ethicist",
    description="Expert in ethical implications and societal impact",
    focus="potential harm, ethical blind spots, fairness issues, unintended consequences",
    instructions="Identify ethical risks and societal impacts. Focus on human values and potential harm.",
)

# Specialized Personas
SECURITY_ENGINEER = Persona(
    name="Security Engineer",
    description="Senior security engineer looking for exploits",
    focus="vulnerabilities, attack vectors, data leaks, security best practices",
    instructions="Act as a red teamer. Try to break the system or find ways to exploit the proposed approach.",
)

RUTHLESS_EDITOR = Persona(
    name="Ruthless Editor",
    description="Experienced editor focused on clarity and brevity",
    focus="fluff, redundancy, jargon, unclear phrasing, weak structure",
    instructions="Cut the fluff. Demand clarity and precision. Point out where the argument meanders.",
)

DEVILS_ADVOCATE = Persona(
    name="Devil's Advocate",
    description="Professional contrarian testing robustness",
    focus="alternative interpretations, edge cases, steel-manning opposing views",
    instructions="Take the opposite view regardless of your personal belief. Find the strongest argument against the thesis.",
)

# Persona Registry
PRESETS: Dict[str, List[Persona]] = {
    "council": [LOGICIAN, EMPIRICIST, ETHICIST],
    "security": [SECURITY_ENGINEER],
    "editorial": [RUTHLESS_EDITOR],
    "debate": [DEVILS_ADVOCATE],
    "comprehensive": [LOGICIAN, EMPIRICIST, ETHICIST, DEVILS_ADVOCATE],
}


def get_personas(
    preset_name: Optional[str] = None, custom_personas: Optional[List[Persona]] = None
) -> List[Persona]:
    """Get a list of personas based on preset name or custom definition."""
    if custom_personas:
        return custom_personas

    if not preset_name:
        return []  # Default to standard single antithesis if no preset

    return PRESETS.get(preset_name.lower(), [])
