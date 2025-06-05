from pydantic import BaseModel, field_validator, HttpUrl, Field, UUID4
from typing import List, Literal, Optional
from datetime import datetime, timezone
from services.check_file import ACCEPTED_FILE_TYPES
import pathlib


# * CUSTOM VALIDATORS   
class FileModel(BaseModel):
    """
    Represents a file with validation on its extension.
    Only accepts filenames with extensions listed in ACCEPTED_FILE_TYPES
    """
    filename: str
    
    @field_validator("filename")
    @classmethod
    def validate_filetype(cls, v: str):
        ext = pathlib.Path(v).suffix.lower()
        if ext not in ACCEPTED_FILE_TYPES:
            raise ValueError(f"File type {ext}, not accepted.")
        
        return v
    

# * SCHEMAS
class GroupLog(BaseModel):
    """
    Logs actions performed in a group.
    """
    timestamp: datetime
    action: str
    details: Optional[str]

class GroupSettings(BaseModel):
    """
    Settings controlling group behavior and detection preferences.
    """
    # user access controls
    whitelist: List[str] # list of usernames
    blacklist: List[str]
    moderators: List[str] 

    # detection settings
    spam_sensitivity: Literal["low", "moderate", "high"]
    virus_sensitivity: Literal["low", "moderate", "high"]
    blacklist_keywords: List[str]
    auto_delete: bool
    notify_admins: bool
    notify_users: bool

    # scan behavior & scheduling
    # scan_interval: int = Field(..., description="Scan interval in seconds.")
    pause_scan: Optional[bool] = False

    # file & content handling
    skip_files: List[FileModel] = Field(default_factory=list)
    skip_urls: List[HttpUrl] = Field(default_factory=list)

class UserSchema(BaseModel):
    """
    Represents a user in the system.
    """
    username: str
    user_id: int
    groups: List[int] # group chat id
    
class GroupSchema(BaseModel):
    """
    Represents a group chat.
    """
    group_id: int
    group_name: str
    admin: int
    settings: GroupSettings
    logs: Optional[List[GroupLog]] = Field(default_factory=list)

# TOKEN SCHEMA
class TokenSchema(BaseModel):
    token: str # UUID
    user_id: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
