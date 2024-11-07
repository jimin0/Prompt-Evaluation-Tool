from typing import Dict, Any
import yaml
import os

class Config:
    """설정 관리 클래스"""
    
    DEFAULT_CONFIG = {
        'database': {
            'path': 'prompts.db',
            'backup_path': 'backups/'
        },
        'similarity': {
            'threshold': 0.8,
            'min_length': 10
        },
        'version': {
            'initial': '1.0.0',
            'auto_increment': True
        },
        'ui': {
            'theme': 'light',
            'page_size': 20
        }
    }

    def __init__(self, config_path: str = 'config.yaml'):
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """설정 파일 로드"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return self.DEFAULT_CONFIG

    def get(self, key: str, default: Any = None) -> Any:
        """설정값 조회"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
                
        return value if value is not None else default

    def set(self, key: str, value: Any):
        """설정값 변경"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            config = config.setdefault(k, {})
        
        config[keys[-1]] = value
        self._save_config()

    def _save_config(self):
        """설정 파일 저장"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.config, f, allow_unicode=True)