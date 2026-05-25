from pydantic import BaseModel, Field


class SegmentPositioning(BaseModel):
    segment: str
    headline: str
    tagline: str
    proof_point: str = ""
    channel: str = ""


class MessagingAngle(BaseModel):
    angle_name: str
    message: str
    emotional_hook: str = ""
    use_case: str = ""
    target_persona: str = ""


class EmotionalTrigger(BaseModel):
    trigger: str
    audience: str
    message: str


class ObjectionResponse(BaseModel):
    objection: str
    response: str


class CorePositioning(BaseModel):
    statement: str = Field(description="One-sentence positioning statement")
    category: str = Field(description="Product category e.g. AI Compliance Platform")
    market_frame: str = Field(default="", description="How you frame the market")
    unique_mechanism: str = Field(default="", description="The 'how' that makes it work")


class PositioningProfileSchema(BaseModel):
    core_positioning: CorePositioning
    segment_positioning: list[SegmentPositioning] = Field(default_factory=list)
    messaging_angles: list[MessagingAngle] = Field(default_factory=list)
    emotional_triggers: list[EmotionalTrigger] = Field(default_factory=list)
    competitive_moats: list[str] = Field(default_factory=list)
    value_propositions: list[str] = Field(default_factory=list)
    objection_handling: list[ObjectionResponse] = Field(default_factory=list)
    brand_personality: list[str] = Field(default_factory=list, description="3-5 personality traits")
    confidence_score: float = Field(default=0.8, ge=0.0, le=1.0)
