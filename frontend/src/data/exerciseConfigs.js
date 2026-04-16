/**
 * exerciseConfigs.js
 *
 * Centralized, exercise-specific configuration for the Athlix analysis pipeline.
 * Adding a new exercise = adding a new key to EXERCISE_CONFIGS.
 * Every other module (analysisService, FormCorrectionPreview, Results) reads from here.
 */

export const EXERCISE_CONFIGS = {

  // ═══════════════════════════════════════════════════════════════
  // SQUAT
  // ═══════════════════════════════════════════════════════════════
  squat: {
    displayName: "Back Squat",
    description: "Evaluating squat depth, knee tracking, and torso angle.",
    usesWeight: true,

    issueCatalog: [
      {
        id: 1,
        issue: "Incomplete Depth",
        baseProbability: 0.6,
        baseSeverity: "High",
        detail: "Hip crease did not drop below the patella.",
        intensityScale: 0.4,
        fatigueScale: 0.3,
        flag: "incomplete_depth",
        joints: ["hip"],
      },
      {
        id: 2,
        issue: "Knee Valgus",
        baseProbability: 0.55,
        baseSeverity: "Medium",
        detail: "Medial collapse detected during the concentric phase.",
        intensityScale: 0.35,
        fatigueScale: 0.4,
        flag: "knee_valgus",
        joints: ["knee"],
      },
      {
        id: 3,
        issue: "Excessive Forward Lean",
        baseProbability: 0.35,
        baseSeverity: "Medium",
        detail: "Torso angle exceeded safe thresholds relative to vertical.",
        intensityScale: 0.3,
        fatigueScale: 0.25,
        flag: "excessive_forward_lean",
        joints: ["back", "shoulder"],
      },
      {
        id: 4,
        issue: "Heel Rise",
        baseProbability: 0.3,
        baseSeverity: "Low",
        detail: "Heel lifted off the platform during descent.",
        intensityScale: 0.1,
        fatigueScale: 0.15,
        flag: "heel_rise",
        joints: ["ankle"],
      },
      {
        id: 5,
        issue: "Lateral Shift",
        baseProbability: 0.2,
        baseSeverity: "Low",
        detail: "Lateral weight distribution asymmetry detected.",
        intensityScale: 0.15,
        fatigueScale: 0.3,
        flag: "lateral_shift",
        joints: ["hip"],
      },
    ],

    coachingMap: {
      "Incomplete Depth":       { action: "Increase Squat Depth", cue: "Focus on breaking parallel. Use a box squat or pause at the bottom to build proprioceptive awareness.", target: "Hip Mobility" },
      "Knee Valgus":            { action: "Active Glute Engagement", cue: "Drive knees outward during the concentric phase. Cue 'spread the floor' with your feet.", target: "Knee Tracking" },
      "Excessive Forward Lean": { action: "Maintain Vertical Torso", cue: "Keep chest proud and eyes forward. Consider front-squatting to reinforce upright mechanics.", target: "Spinal Neutrality" },
      "Heel Rise":              { action: "Improve Ankle Mobility", cue: "Work on ankle dorsiflexion with wall stretches. Consider elevated-heel squat shoes.", target: "Ankle ROM" },
      "Lateral Shift":          { action: "Unilateral Correction", cue: "Add single-leg exercises (Bulgarian split squats) to eliminate asymmetry.", target: "Bilateral Symmetry" },
    },

    correctionPose: {
      original: {
        shoulder: { x: 38, y: 22 },
        hip:      { x: 36, y: 44 },
        knee:     { x: 30, y: 65 },
        ankle:    { x: 28, y: 88 },
      },
      corrected: {
        shoulder: { x: 40, y: 20 },
        hip:      { x: 38, y: 48 },
        knee:     { x: 30, y: 68 },
        ankle:    { x: 28, y: 88 },
      },
      limbChain: [
        ["shoulder", "hip"],
        ["hip", "knee"],
        ["knee", "ankle"],
      ],
      labels: {
        knee_valgus:            { label: "Knee tracking corrected", joint: "knee" },
        incomplete_depth:       { label: "Depth improved",          joint: "hip" },
        excessive_forward_lean: { label: "Torso uprighted",         joint: "shoulder" },
      },
      subtitle: "Lower-body kinematic chain",
    },
  },

  // ═══════════════════════════════════════════════════════════════
  // DEADLIFT
  // ═══════════════════════════════════════════════════════════════
  deadlift: {
    displayName: "Conventional Deadlift",
    description: "Evaluating spine neutrality, hip hinge, and lockout posture.",
    usesWeight: true,

    issueCatalog: [
      {
        id: 1,
        issue: "Rounded Back",
        baseProbability: 0.6,
        baseSeverity: "High",
        detail: "Thoracic and/or lumbar spine lost neutral position under load.",
        intensityScale: 0.45,
        fatigueScale: 0.35,
        flag: "rounded_back",
        joints: ["back", "shoulder"],
      },
      {
        id: 2,
        issue: "Poor Hip Hinge",
        baseProbability: 0.5,
        baseSeverity: "Medium",
        detail: "Insufficient hip flexion leading to quad-dominant lift pattern.",
        intensityScale: 0.3,
        fatigueScale: 0.3,
        flag: "poor_hip_hinge",
        joints: ["hip"],
      },
      {
        id: 3,
        issue: "Bar Drift",
        baseProbability: 0.35,
        baseSeverity: "Medium",
        detail: "Bar path deviated away from the midline during the pull.",
        intensityScale: 0.25,
        fatigueScale: 0.2,
        flag: "bar_drift",
        joints: ["shoulder"],
      },
      {
        id: 4,
        issue: "Incomplete Lockout",
        baseProbability: 0.3,
        baseSeverity: "Low",
        detail: "Hips did not fully extend at the top of the movement.",
        intensityScale: 0.2,
        fatigueScale: 0.25,
        flag: "incomplete_lockout",
        joints: ["hip"],
      },
      {
        id: 5,
        issue: "Knee Cave",
        baseProbability: 0.25,
        baseSeverity: "Medium",
        detail: "Knees collapsed inward during the initial drive off the floor.",
        intensityScale: 0.3,
        fatigueScale: 0.35,
        flag: "knee_cave",
        joints: ["knee"],
      },
    ],

    coachingMap: {
      "Rounded Back":       { action: "Brace & Set the Back", cue: "Take a deep diaphragmatic breath, brace the core, and 'chest up' before initiating the pull.", target: "Spinal Integrity" },
      "Poor Hip Hinge":     { action: "Hinge Pattern Drill", cue: "Practice Romanian deadlifts and hip hinge wall drills to groove the posterior chain loading pattern.", target: "Hip Mechanics" },
      "Bar Drift":          { action: "Keep the Bar Close", cue: "Engage the lats to sweep the bar into the body. Think 'paint the shins with the bar.'", target: "Lat Engagement" },
      "Incomplete Lockout": { action: "Drive Hips Through", cue: "Squeeze the glutes aggressively at the top. Avoid hyperextending the lumbar spine.", target: "Glute Activation" },
      "Knee Cave":          { action: "Spread the Floor", cue: "Push knees outward in sync with the pull. Strengthen with banded deadlifts.", target: "Knee Stability" },
    },

    correctionPose: {
      original: {
        shoulder: { x: 32, y: 24 },
        hip:      { x: 40, y: 50 },
        knee:     { x: 38, y: 70 },
        ankle:    { x: 36, y: 90 },
      },
      corrected: {
        shoulder: { x: 38, y: 20 },
        hip:      { x: 40, y: 46 },
        knee:     { x: 38, y: 70 },
        ankle:    { x: 36, y: 90 },
      },
      limbChain: [
        ["shoulder", "hip"],
        ["hip", "knee"],
        ["knee", "ankle"],
      ],
      labels: {
        rounded_back:       { label: "Spine neutralized",   joint: "shoulder" },
        poor_hip_hinge:     { label: "Hinge improved",      joint: "hip" },
        incomplete_lockout: { label: "Lockout completed",    joint: "hip" },
      },
      subtitle: "Posterior chain alignment",
    },
  },

  // ═══════════════════════════════════════════════════════════════
  // PUSH-UP
  // ═══════════════════════════════════════════════════════════════
  pushup: {
    displayName: "Push-Up",
    description: "Evaluating elbow angle, depth, hip alignment, and symmetry.",
    usesWeight: false,

    issueCatalog: [
      {
        id: 1,
        issue: "Insufficient Depth",
        baseProbability: 0.55,
        baseSeverity: "High",
        detail: "Chest did not reach within fist-distance of the floor.",
        intensityScale: 0.2,
        fatigueScale: 0.4,
        flag: "insufficient_depth",
        joints: ["shoulder"],
      },
      {
        id: 2,
        issue: "Hip Sag",
        baseProbability: 0.5,
        baseSeverity: "High",
        detail: "Core lost rigidity — hips dropped below the shoulder-ankle line.",
        intensityScale: 0.15,
        fatigueScale: 0.45,
        flag: "hip_sag",
        joints: ["hip"],
      },
      {
        id: 3,
        issue: "Wide Elbow Flare",
        baseProbability: 0.45,
        baseSeverity: "Medium",
        detail: "Elbows flared beyond 60° from the torso, stressing the shoulder capsule.",
        intensityScale: 0.1,
        fatigueScale: 0.3,
        flag: "elbow_flare",
        joints: ["shoulder"],
      },
      {
        id: 4,
        issue: "Asymmetric Descent",
        baseProbability: 0.25,
        baseSeverity: "Low",
        detail: "One side descended faster or deeper than the other.",
        intensityScale: 0.05,
        fatigueScale: 0.35,
        flag: "asymmetric_descent",
        joints: ["shoulder"],
      },
      {
        id: 5,
        issue: "Neck Hyperextension",
        baseProbability: 0.2,
        baseSeverity: "Low",
        detail: "Head position tilted upward, breaking cervical neutrality.",
        intensityScale: 0.05,
        fatigueScale: 0.15,
        flag: "neck_hyperextension",
        joints: ["shoulder"],
      },
    ],

    coachingMap: {
      "Insufficient Depth":   { action: "Full Range of Motion", cue: "Lower until your chest is fist-height from the floor. Use deficit push-ups to build end-range strength.", target: "Chest Activation" },
      "Hip Sag":              { action: "Engage Core Throughout", cue: "Squeeze the glutes and brace the abs as if preparing for impact. Maintain a rigid plank line.", target: "Core Stability" },
      "Wide Elbow Flare":     { action: "Tuck the Elbows", cue: "Keep elbows at ~45° from the torso. Think 'arrow shape' not 'T-shape' at the bottom.", target: "Shoulder Health" },
      "Asymmetric Descent":   { action: "Bilateral Focus", cue: "Perform slow single-arm negatives and use a mirror or video to check symmetry.", target: "Symmetry" },
      "Neck Hyperextension":  { action: "Pack the Chin", cue: "Maintain a neutral cervical spine — look at a spot 6 inches ahead of your fingertips.", target: "Cervical Alignment" },
    },

    correctionPose: {
      // Horizontal side view of push-up
      original: {
        shoulder: { x: 30, y: 40 },
        hip:      { x: 50, y: 48 },  // sagging
        knee:     { x: 62, y: 44 },
        ankle:    { x: 72, y: 44 },
      },
      corrected: {
        shoulder: { x: 30, y: 40 },
        hip:      { x: 50, y: 40 },  // aligned
        knee:     { x: 62, y: 40 },
        ankle:    { x: 72, y: 40 },
      },
      limbChain: [
        ["shoulder", "hip"],
        ["hip", "knee"],
        ["knee", "ankle"],
      ],
      labels: {
        hip_sag:            { label: "Hip aligned",       joint: "hip" },
        insufficient_depth: { label: "Depth corrected",   joint: "shoulder" },
        elbow_flare:        { label: "Elbow tucked",      joint: "shoulder" },
      },
      subtitle: "Plank-line alignment",
    },
  },
};

/** Convenience: get config or fallback to squat */
export function getExerciseConfig(exerciseType) {
  return EXERCISE_CONFIGS[exerciseType] || EXERCISE_CONFIGS.squat;
}
