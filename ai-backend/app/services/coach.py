"""
coach.py
--------
Converts injury risk factors into prioritised, actionable coaching advice.

Lives in app/services/ alongside risk_engine.py and explainer.py.

Public API
~~~~~~~~~~
    get_recommendations(input_features: dict) -> CoachingReport

Usage example
~~~~~~~~~~~~~
    from app.services.coach import get_recommendations

    report = get_recommendations({
        "training_load":   8.5,
        "recovery_score":  25.0,
        "fatigue_index":   8.1,
        "form_decay":      0.82,
        "previous_injury": 1,
    })
    print(report)
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from enum import Enum

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
_SERVICES_DIR = os.path.dirname(os.path.abspath(__file__))
if _SERVICES_DIR not in sys.path:
    sys.path.insert(0, _SERVICES_DIR)

from risk_engine import (
    FATIGUE_HIGH_THRESHOLD,
    FORM_DECAY_HIGH_THRESHOLD,
    RECOVERY_LOW_THRESHOLD,
    _validate_input,
    get_risk_score,
)


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class Priority(str, Enum):
    """How urgent a recommendation is."""
    URGENT      = "Urgent"       # act today — high risk of injury
    RECOMMENDED = "Recommended"  # act this week
    OPTIONAL    = "Optional"     # nice-to-have, preventive


class Category(str, Enum):
    """Which coaching domain the recommendation belongs to."""
    BIOMECHANICS = "Biomechanics"   # posture, alignment, movement quality
    RECOVERY     = "Recovery"       # sleep, nutrition, rest days
    LOAD         = "Load Mgmt"      # training volume / intensity
    MINDSET      = "Mindset"        # mental recovery, stress


# ---------------------------------------------------------------------------
# Suggestion dataclass
# ---------------------------------------------------------------------------

@dataclass
class Suggestion:
    """
    A single coaching recommendation.

    Attributes
    ----------
    priority : Priority  — Urgent / Recommended / Optional.
    category : Category  — Which coaching domain this belongs to.
    title    : str       — Short headline (≤ 60 chars).
    detail   : str       — Longer explanation with context.
    drills   : list[str] — Optional concrete exercises / actions.
    """
    priority: Priority
    category: Category
    title:    str
    detail:   str
    drills:   list[str] = field(default_factory=list)

    def __str__(self) -> str:
        icon = {"Urgent": "[!!]", "Recommended": "[ >]", "Optional": "[ ?]"}
        lines = [f"{icon.get(self.priority.value, '[ ]')} [{self.category.value}] {self.title}"]
        lines.append(f"     {self.detail}")
        for drill in self.drills:
            lines.append(f"     * {drill}")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "priority": self.priority.value,
            "category": self.category.value,
            "title":    self.title,
            "detail":   self.detail,
            "drills":   self.drills,
        }


# ---------------------------------------------------------------------------
# Coaching report dataclass
# ---------------------------------------------------------------------------

@dataclass
class CoachingReport:
    """
    Full coaching output for one athlete session.

    Attributes
    ----------
    risk_score      : float        — Final risk score [0-100].
    risk_level      : str          — "Low" | "Medium" | "High".
    summary         : str          — One-line overall coaching summary.
    suggestions     : list[Suggestion] — Ordered by priority then category.
    positive_notes  : list[str]    — Things the athlete is doing well.
    """
    risk_score:     float
    risk_level:     str
    summary:        str
    suggestions:    list[Suggestion]
    positive_notes: list[str] = field(default_factory=list)

    def __str__(self) -> str:
        sep  = "-" * 60
        lines = [
            sep,
            f"  Coaching Report  |  Risk: {self.risk_score:.1f}/100 ({self.risk_level})",
            f"  {self.summary}",
            sep,
        ]

        if self.suggestions:
            lines.append(f"\n  Recommendations ({len(self.suggestions)}):\n")
            for i, s in enumerate(self.suggestions, 1):
                lines.append(f"  {i}. {s}\n")

        if self.positive_notes:
            lines.append(f"  Doing well:")
            for note in self.positive_notes:
                lines.append(f"    + {note}")

        lines.append(sep)
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "risk_score":     round(self.risk_score, 2),
            "risk_level":     self.risk_level,
            "summary":        self.summary,
            "suggestions":    [s.to_dict() for s in self.suggestions],
            "positive_notes": self.positive_notes,
        }


# ---------------------------------------------------------------------------
# Rule catalogue — all possible recommendations
# ---------------------------------------------------------------------------
# Each function returns a Suggestion if the condition triggers, else None.

def _check_form_decay_critical(f: dict):
    if f["form_decay"] > 0.80:
        return Suggestion(
            priority = Priority.URGENT,
            category = Category.BIOMECHANICS,
            title    = "Critical form breakdown — stop heavy lifts immediately",
            detail   = (
                f"Form decay is at {f['form_decay']*100:.0f}% — at this level the risk of acute "
                "injury (joint, tendon, or muscle) is very high. Do not attempt heavy compound "
                "movements until mechanics are re-established."
            ),
            drills = [
                "Drop to 50% of your normal load and focus on slow, controlled reps",
                "Film yourself from the side to identify the specific breakdown point",
                "Book a session with a movement coach or physiotherapist",
            ],
        )
    return None


def _check_form_decay_high(f: dict):
    if 0.60 < f["form_decay"] <= 0.80:
        return Suggestion(
            priority = Priority.URGENT,
            category = Category.BIOMECHANICS,
            title    = "Fix posture and joint alignment",
            detail   = (
                f"Form decay is at {f['form_decay']*100:.0f}%. Your movement quality has degraded "
                "significantly — likely due to accumulated fatigue. Focus on technique over load."
            ),
            drills = [
                "Knee tracking drill: squat to a box with a band above knees",
                "Hip hinge pattern reset: 3x10 Romanian deadlifts at light weight",
                "Thoracic mobility: 2 min cat-cow + 10 open-book rotations each side",
                "Record your form and compare against your baseline",
            ],
        )
    return None


def _check_form_decay_moderate(f: dict):
    if 0.40 < f["form_decay"] <= 0.60:
        return Suggestion(
            priority = Priority.RECOMMENDED,
            category = Category.BIOMECHANICS,
            title    = "Address early form degradation",
            detail   = (
                f"Form decay at {f['form_decay']*100:.0f}% signals early quality loss. "
                "Proactively reinforcing mechanics now prevents it from compounding."
            ),
            drills = [
                "Start each session with 10 min movement prep (mobility + activation)",
                "Finish sets at technical failure — not muscular failure",
                "Add 1 technique-focused session per week at 60% intensity",
            ],
        )
    return None


def _check_fatigue_critical(f: dict):
    if f["fatigue_index"] >= 9.0:
        return Suggestion(
            priority = Priority.URGENT,
            category = Category.LOAD,
            title    = "Complete rest day required — fatigue is critical",
            detail   = (
                f"Fatigue index is {f['fatigue_index']:.1f}/10. Continuing to train at this level "
                "dramatically increases both acute injury risk and long-term burnout probability. "
                "Performance gains only happen during recovery, not training."
            ),
            drills = [
                "Schedule a full off-day today — no structured training",
                "Light walking (20-30 min) is acceptable to promote blood flow",
                "Review the past 2 weeks of training load for overreaching patterns",
            ],
        )
    return None


def _check_fatigue_high(f: dict):
    if FATIGUE_HIGH_THRESHOLD < f["fatigue_index"] < 9.0:
        return Suggestion(
            priority = Priority.URGENT,
            category = Category.LOAD,
            title    = "Reduce training load — fatigue is high",
            detail   = (
                f"Fatigue index is {f['fatigue_index']:.1f}/10. Accumulated fatigue is outpacing "
                "your recovery. A deload is necessary to prevent overuse injury."
            ),
            drills = [
                "Reduce total training volume by 40% for the next 5-7 days",
                "Replace one session this week with a lower-intensity active recovery workout",
                "Avoid back-to-back high-intensity days — insert rest days between hard sessions",
            ],
        )
    return None


def _check_fatigue_moderate(f: dict):
    if 5.5 < f["fatigue_index"] <= FATIGUE_HIGH_THRESHOLD:
        return Suggestion(
            priority = Priority.RECOMMENDED,
            category = Category.LOAD,
            title    = "Monitor fatigue — consider a lighter session",
            detail   = (
                f"Fatigue index is {f['fatigue_index']:.1f}/10. You're accumulating fatigue "
                "faster than you're recovering. Consider a planned deload next week."
            ),
            drills = [
                "Cap today's session intensity at 70% of your max",
                "Prioritise compound movements over isolation exercises",
                "Plan a deload week every 4th week of hard training",
            ],
        )
    return None


def _check_recovery_critical(f: dict):
    if f["recovery_score"] < 20:
        return Suggestion(
            priority = Priority.URGENT,
            category = Category.RECOVERY,
            title    = "Critically low recovery — training is counterproductive",
            detail   = (
                f"Recovery score is {f['recovery_score']:.0f}/100. At this level, training "
                "causes net tissue damage faster than it can repair. Any session today will "
                "increase injury risk substantially."
            ),
            drills = [
                "Do not train today — rest is the most productive choice",
                "Sleep: target 8-9 hours in a dark, cool room tonight",
                "Hydrate: aim for 3L of water through the day",
                "Nutrition: prioritise protein (1.6-2g/kg body weight) and complex carbohydrates",
            ],
        )
    return None


def _check_recovery_low(f: dict):
    if 20 <= f["recovery_score"] < RECOVERY_LOW_THRESHOLD:
        return Suggestion(
            priority = Priority.URGENT,
            category = Category.RECOVERY,
            title    = "Improve sleep and recovery quality",
            detail   = (
                f"Recovery score is {f['recovery_score']:.0f}/100. Poor recovery is compounding "
                "your fatigue and leaving tissue micro-damage unrepaired. This is a primary "
                "driver of overuse injuries."
            ),
            drills = [
                "Sleep: add 30-60 min to your sleep window for the next 7 nights",
                "Set a consistent bedtime — aim to be asleep by 10:30 PM",
                "Avoid screens for 1 hour before bed; use blue-light glasses if unavoidable",
                "Consider 10 min of breathwork or meditation before sleep",
            ],
        )
    return None


def _check_recovery_moderate(f: dict):
    if RECOVERY_LOW_THRESHOLD <= f["recovery_score"] < 55:
        return Suggestion(
            priority = Priority.RECOMMENDED,
            category = Category.RECOVERY,
            title    = "Optimise recovery habits",
            detail   = (
                f"Recovery score is {f['recovery_score']:.0f}/100. There is room to improve. "
                "Small daily habits compound into significant recovery gains over weeks."
            ),
            drills = [
                "Cold/contrast shower post-training to reduce inflammation",
                "10 min static stretching or yoga before bed",
                "Track HRV daily — train hard only when HRV is elevated vs. your baseline",
            ],
        )
    return None


def _check_acwr(f: dict):
    """ACWR is derived — approximate from training_load trajectory."""
    if f["training_load"] >= 8.5:
        return Suggestion(
            priority = Priority.RECOMMENDED,
            category = Category.LOAD,
            title    = "Monitor acute:chronic workload ratio (ACWR)",
            detail   = (
                f"Training load is {f['training_load']:.1f}/10. A spike in load without a "
                "corresponding chronic base puts you in the injury danger zone (ACWR > 1.3). "
                "Load should be increased by no more than 10% per week."
            ),
            drills = [
                "Apply the 10% rule: increase weekly load by no more than 10% vs. last week",
                "Log your sessions to track acute (7-day) vs. chronic (28-day) load trends",
                "Periodise your training: 3 weeks progressive load, 1 week deload",
            ],
        )
    return None


def _check_previous_injury(f: dict):
    if f["previous_injury"] == 1:
        return Suggestion(
            priority = Priority.RECOMMENDED,
            category = Category.BIOMECHANICS,
            title    = "Protect previously injured areas",
            detail   = (
                "Prior injury history is the strongest predictor of re-injury. Scar tissue "
                "and compensatory movement patterns can persist long after acute symptoms resolve."
            ),
            drills = [
                "Perform targeted prehab exercises for your previously injured area (10 min daily)",
                "Avoid training through pain — distinguish between effort discomfort and injury pain",
                "Schedule a check-in with a physiotherapist every 6-8 weeks during heavy blocks",
            ],
        )
    return None


def _check_mindset_stress(f: dict):
    """Triggered when multiple high-risk factors co-exist."""
    factors_active = sum([
        f["fatigue_index"]  > FATIGUE_HIGH_THRESHOLD,
        f["recovery_score"] < RECOVERY_LOW_THRESHOLD,
        f["form_decay"]     > FORM_DECAY_HIGH_THRESHOLD,
    ])
    if factors_active >= 2:
        return Suggestion(
            priority = Priority.OPTIONAL,
            category = Category.MINDSET,
            title    = "Manage psychological stress alongside physical load",
            detail   = (
                "Multiple high-risk factors are active simultaneously. Psychological stress "
                "elevates cortisol, impairs sleep quality, and slows muscle repair — making "
                "physical recovery significantly harder."
            ),
            drills = [
                "5 min box breathing daily (inhale 4s, hold 4s, exhale 4s, hold 4s)",
                "Journaling: note 3 things in your control before each training session",
                "Consider reducing life stressors temporarily if training load is high",
            ],
        )
    return None


# Priority sort order
_PRIORITY_ORDER = {Priority.URGENT: 0, Priority.RECOMMENDED: 1, Priority.OPTIONAL: 2}


# ---------------------------------------------------------------------------
# Positive note builders
# ---------------------------------------------------------------------------

def _build_positive_notes(f: dict) -> list[str]:
    """Identify things the athlete is doing well and acknowledge them."""
    notes = []
    if f["recovery_score"] >= 70:
        notes.append(f"Recovery score is excellent ({f['recovery_score']:.0f}/100) — keep prioritising sleep and nutrition")
    if f["fatigue_index"] <= 3.0:
        notes.append(f"Fatigue is well managed ({f['fatigue_index']:.1f}/10) — your load-recovery balance is good")
    if f["form_decay"] <= 0.25:
        notes.append(f"Movement quality is strong ({f['form_decay']*100:.0f}% decay) — technique is well preserved")
    if f["training_load"] <= 4.0:
        notes.append(f"Training load is conservative ({f['training_load']:.1f}/10) — a good base for progressive overload")
    return notes


# ---------------------------------------------------------------------------
# Summary builder
# ---------------------------------------------------------------------------

def _build_summary(risk_level: str, suggestions: list[Suggestion]) -> str:
    urgent_count = sum(1 for s in suggestions if s.priority == Priority.URGENT)

    if risk_level == "High":
        if urgent_count >= 3:
            return "Multiple critical risk factors detected. Immediate rest and recovery is the coaching priority."
        return f"{urgent_count} urgent intervention(s) identified. Address these before your next session."
    elif risk_level == "Medium":
        return "Moderate risk — targeted adjustments to load and recovery will significantly reduce injury probability."
    return "Low risk — maintain current habits and focus on progressive development."


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_recommendations(input_features: dict) -> CoachingReport:
    """
    Convert athlete risk factors into a prioritised list of coaching suggestions.

    Parameters
    ----------
    input_features : dict
        Keys: training_load (1-10), recovery_score (0-100),
              fatigue_index (0-10), form_decay (0-1), previous_injury (0/1).
        Missing keys are filled with sensible defaults.

    Returns
    -------
    CoachingReport
        Dataclass containing: risk_score, risk_level, summary,
        ordered suggestions (Urgent first), and positive notes.

    Example
    -------
    >>> report = get_recommendations({
    ...     "training_load": 8.5, "recovery_score": 25.0,
    ...     "fatigue_index": 8.1, "form_decay": 0.82,
    ...     "previous_injury": 1,
    ... })
    >>> print(report)
    """
    # 1. Validate input
    features = _validate_input(input_features)

    # 2. Get risk score
    risk = get_risk_score(features)

    # 3. Run all rule checks — collect non-None suggestions
    rule_checks = [
        _check_form_decay_critical,
        _check_form_decay_high,
        _check_form_decay_moderate,
        _check_fatigue_critical,
        _check_fatigue_high,
        _check_fatigue_moderate,
        _check_recovery_critical,
        _check_recovery_low,
        _check_recovery_moderate,
        _check_acwr,
        _check_previous_injury,
        _check_mindset_stress,
    ]

    suggestions: list[Suggestion] = []
    for check in rule_checks:
        result = check(features)
        if result is not None:
            suggestions.append(result)

    # 4. Sort: Urgent → Recommended → Optional, then by category name
    suggestions.sort(key=lambda s: (_PRIORITY_ORDER[s.priority], s.category.value))

    # 5. Positive feedback
    positive_notes = _build_positive_notes(features)

    # 6. Overall summary
    summary = _build_summary(risk.risk_level, suggestions)

    return CoachingReport(
        risk_score     = risk.risk_score,
        risk_level     = risk.risk_level,
        summary        = summary,
        suggestions    = suggestions,
        positive_notes = positive_notes,
    )


# ---------------------------------------------------------------------------
# Entry point — demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    scenarios = [
        (
            "Elite athlete - low risk",
            {"training_load": 3.0, "recovery_score": 88.0,
             "fatigue_index": 1.5, "form_decay": 0.12, "previous_injury": 0},
        ),
        (
            "Moderate load - average condition",
            {"training_load": 5.5, "recovery_score": 55.0,
             "fatigue_index": 5.0, "form_decay": 0.45, "previous_injury": 0},
        ),
        (
            "Overloaded athlete - maximum risk",
            {"training_load": 8.5, "recovery_score": 25.0,
             "fatigue_index": 8.1, "form_decay": 0.82, "previous_injury": 1},
        ),
        (
            "Heavy training - prior injury history",
            {"training_load": 9.2, "recovery_score": 40.0,
             "fatigue_index": 7.5, "form_decay": 0.75, "previous_injury": 1},
        ),
    ]

    for label, feats in scenarios:
        print(f"\n  >>> Scenario: {label}")
        report = get_recommendations(feats)
        print(report)
