from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class EnvironmentVariable:
	name: str
	category: str
	description: str = ""
	required: bool = False
	sensitive: bool = False
	min_length: Optional[int] = None
	pattern: Optional[str] = None
	default_dev: Optional[str] = None
	default_prod: Optional[str] = None
	detected_in: List[str] = field(default_factory=list)



