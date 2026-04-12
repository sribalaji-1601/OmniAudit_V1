"""
Pydantic models for OmniAudit Environment
Strict OpenEnv compliance with BaseModel classes
"""

from enum import Enum
from typing import List, Dict, Any, Optional

try:
    # Pydantic v2
    from pydantic import BaseModel, Field
    PYDANTIC_V2 = True
except ImportError:
    # Pydantic v1
    from pydantic import BaseModel, Field
    PYDANTIC_V2 = False

class ActionType(str, Enum):
    """Action types for the environment"""
    PATCH_UI_ATTR = "PATCH_UI_ATTR"
    PATCH_UI_TEXT = "PATCH_UI_TEXT"
    SYNC_BACKEND = "SYNC_BACKEND"

class UIElement(BaseModel):
    """Represents a UI element in the frontend"""
    id: str
    tag: str
    text: Optional[str] = None
    attributes: Dict[str, str]

class Observation(BaseModel):
    """Complete environment observation"""
    ui_elements: List[UIElement]
    backend_record: Dict[str, Any]
    screen_reader_summary: str

class Action(BaseModel):
    """Action that can be taken in the environment"""
    cmd: ActionType
    target_id: str
    key: Optional[str] = None
    value: Optional[str] = None
    
    class Config:
        arbitrary_types_allowed = True

class Reward(BaseModel):
    """Reward for an action"""
    total: float = 0.0
    accessibility: float = 0.0
    data_integrity: float = 0.0
    semantic_accuracy: float = 0.0
    feedback: str = ""

class TaskInfo(BaseModel):
    """Information about a task"""
    name: str
    description: str
    difficulty: str
    reward_weight: float
    current_score: float = 0.01

class EnvironmentState(BaseModel):
    """Current state of the environment"""
    step_count: int = 0
    total_reward: float = 0.0
    is_complete: bool = False
    tasks_completed: List[str] = []
