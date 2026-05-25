export interface CorePositioning {
  statement: string;
  category: string;
  market_frame: string;
  unique_mechanism: string;
}

export interface SegmentPositioning {
  segment: string;
  headline: string;
  tagline: string;
  proof_point: string;
  channel: string;
}

export interface MessagingAngle {
  angle_name: string;
  message: string;
  emotional_hook: string;
  use_case: string;
  target_persona: string;
}

export interface EmotionalTrigger {
  trigger: string;
  audience: string;
  message: string;
}

export interface PositioningProfile {
  core_positioning: CorePositioning;
  segment_positioning: SegmentPositioning[];
  messaging_angles: MessagingAngle[];
  emotional_triggers: EmotionalTrigger[];
  competitive_moats: string[];
  value_propositions: string[];
  objection_handling: Array<{ objection: string; response: string }>;
  brand_personality: string[];
  confidence_score: number;
}
