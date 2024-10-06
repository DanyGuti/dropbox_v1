from dataclasses import dataclass, field

@dataclass
class Response:
    message: str = ""
    status_code: int = 0
    data: dict = field(default_factory=dict)

@dataclass
class Request:
    src_path: str = ""
    action: str = ""
    file_name: str = ""
    destination_path: str = ""
    is_directory: bool = ""