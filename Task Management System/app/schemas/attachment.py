from datetime import datetime
from pydantic import BaseModel, ConfigDict


class AttachmentOut(BaseModel):
	model_config = ConfigDict(from_attributes=True)
	id: int
	task_id: int
	file_name: str
	file_path: str
	file_type: str
	file_size: int
	uploaded_at: datetime
