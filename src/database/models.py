from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Prompt:
    """프롬프트 모델"""
    id: Optional[int]
    title: str
    description: str
    model: str
    version: str
    category: str
    tags: str
    query: str
    prompt_content: str
    chatbot_response: str
    expected_result: str
    is_best: bool
    changes: str
    improvements: str
    pros: str
    cons: str
    stats: str
    created_by: str
    department: str
    user_role: str
    created_at: datetime = None

    def to_dict(self):
        """데이터클래스를 딕셔너리로 변환"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'model': self.model,
            'version': self.version,
            'category': self.category,
            'tags': self.tags,
            'query': self.query,
            'prompt_content': self.prompt_content,
            'chatbot_response': self.chatbot_response,
            'expected_result': self.expected_result,
            'is_best': self.is_best,
            'changes': self.changes,
            'improvements': self.improvements,
            'pros': self.pros,
            'cons': self.cons,
            'stats': self.stats,
            'created_by': self.created_by,
            'department': self.department,
            'user_role': self.user_role,
            'created_at': self.created_at
        }

@dataclass
class ChangeLog:
    """변경 이력 모델"""
    id: Optional[int]
    name: str
    title: str
    prompt_id: int
    version_number: str
    change_summary: str
    changed_by: str
    changed_at: datetime = None

    def to_dict(self):
        """데이터클래스를 딕셔너리로 변환"""
        return {
            'id': self.id,
            'name': self.name,
            'title': self.title,
            'prompt_id': self.prompt_id,
            'version_number': self.version_number,
            'change_summary': self.change_summary,
            'changed_by': self.changed_by,
            'changed_at': self.changed_at
        }
