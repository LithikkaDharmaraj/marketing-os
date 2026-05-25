from pydantic import BaseModel, Field


class BrandVoice(BaseModel):
    tone: str = ""
    style: str = ""
    personality: list[str] = Field(default_factory=list)
    avoid: list[str] = Field(default_factory=list)
    example_phrases: list[str] = Field(default_factory=list)


class PainNarrative(BaseModel):
    pain: str
    segment: str
    narrative: str
    emotion: str = ""


class ProofPoint(BaseModel):
    claim: str
    evidence: str = ""
    source: str = ""


class ChannelContext(BaseModel):
    email: dict = Field(default_factory=dict)
    linkedin: dict = Field(default_factory=dict)
    ads: dict = Field(default_factory=dict)
    landing_page: dict = Field(default_factory=dict)


class CampaignContextSchema(BaseModel):
    brand_voice: BrandVoice
    key_messages: list[str] = Field(default_factory=list)
    pain_narratives: list[PainNarrative] = Field(default_factory=list)
    proof_points: list[ProofPoint] = Field(default_factory=list)
    cta_variants: list[str] = Field(default_factory=list)
    channel_context: ChannelContext = Field(default_factory=ChannelContext)
    hooks: list[str] = Field(default_factory=list, description="Attention-grabbing openers")
