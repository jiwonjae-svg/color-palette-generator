"""
AI Color Recommendation Module
Generate color palettes using Google Gemini API
"""

import os
import json
import re
from typing import List, Tuple, Optional

try:
    import google.generativeai as genai  # type: ignore[import-untyped]
    GENAI_AVAILABLE = True
except ImportError:
    genai = None
    GENAI_AVAILABLE = False

from language_manager import LanguageManager


class AIColorRecommender:
    """AI-based color recommendation class"""
    
    def __init__(self, api_key: Optional[str] = None, lang: Optional[LanguageManager] = None):
        self.api_key = api_key
        self.model = None
        self.lang = lang or LanguageManager('en')
        
        if api_key:
            self.initialize_model()

    def _t(self, key: str, **kwargs) -> str:
        text = self.lang.get(key)
        return text.format(**kwargs) if kwargs else text
    
    def initialize_model(self):
        """Initialize Gemini model"""
        try:
            if not GENAI_AVAILABLE:
                raise ImportError(self._t('ai_recommender_missing_library', install_cmd='pip install google-generativeai'))
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash-lite')
            return True
        except ImportError as e:
            raise e
        except Exception as e:
            raise Exception(self._t('ai_recommender_init_failed', error=str(e)))
    
    def set_api_key(self, api_key: str) -> bool:
        """Set API key"""
        self.api_key = api_key
        try:
            self.initialize_model()
            return True
        except Exception:
            return False
    
    def generate_palettes(self, num_palettes: int = 5, keywords: str = "", num_colors: int = 5) -> List[dict]:
        """
        Generate color palettes using AI
        
        Args:
            num_palettes: Number of palettes to generate
            keywords: Keywords (e.g.: "ocean, calm, blue")
            num_colors: Number of colors per palette
        
        Returns:
            List of palettes (each palette is a {'name': str, 'colors': List[str]} dict)
        """
        if not self.model:
            raise Exception(self._t('ai_recommender_api_key_not_set'))
        
        # Generate prompt (including name)
        if keywords.strip():
            prompt = self._t(
                'ai_recommender_prompt_with_keywords',
                num_palettes=num_palettes,
                num_colors=num_colors,
                keywords=keywords,
            )
        else:
            prompt = self._t(
                'ai_recommender_prompt_without_keywords',
                num_palettes=num_palettes,
                num_colors=num_colors,
            )
        
        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            
            # Parse response
            palettes = self._parse_response(text, num_colors)
            return palettes[:num_palettes]  # Return up to the requested count
            
        except Exception as e:
            raise Exception(self._t('ai_recommender_generation_failed', error=str(e)))
    
    def _parse_response(self, text: str, expected_colors: int) -> List[dict]:
        """Parse AI response - extract palette names and colors"""
        palettes = []
        
        # HEX color code pattern
        hex_pattern = r'#[0-9A-Fa-f]{6}'
        
        # Process line by line
        lines = text.split('\n')
        for line in lines:
            # Parse "PaletteName: #HEX,#HEX,..." format
            if ':' in line:
                parts = line.split(':', 1)
                name = parts[0].strip()
                colors = re.findall(hex_pattern, parts[1])
                
                if colors and len(colors) >= expected_colors and name:
                    # Normalize to uppercase
                    colors = [c.upper() for c in colors[:expected_colors]]
                    palettes.append({
                        'name': name,
                        'colors': colors
                    })
            else:
                # Colors only without name (backward compatibility)
                colors = re.findall(hex_pattern, line)
                if colors and len(colors) >= expected_colors:
                    # Normalize to uppercase
                    colors = [c.upper() for c in colors[:expected_colors]]
                    palettes.append({
                        'name': self.lang.get('palette_numbered').format(i=len(palettes) + 1),
                        'colors': colors
                    })
        
        return palettes
    
    def test_api_key(self) -> Tuple[bool, str]:
        """Test API key"""
        if not self.api_key:
            return False, self._t('ai_recommender_api_key_not_set')
        
        try:
            self.initialize_model()
            # Simple test request
            response = self.model.generate_content(self._t('ai_recommender_test_prompt'))
            if response and response.text:
                return True, self._t('ai_recommender_test_success')
            else:
                return False, self._t('ai_recommender_test_no_response')
        except Exception as e:
            return False, self._t('ai_recommender_test_failed', error=str(e))


class AISettings:
    """AI settings management"""
    
    @classmethod
    def save_settings(cls, file_handler, api_key: str, num_colors: int = 5, keywords: str = "") -> bool:
        """Save settings (using FileHandler)"""
        try:
            data = {
                'api_key': api_key,
                'num_colors': num_colors,
                'keywords': keywords
            }
            return file_handler.save_data_file('ai_config.dat', data)
        except Exception:
            return False
    
    @classmethod
    def load_settings(cls, file_handler) -> dict:
        """Load settings (using FileHandler)"""
        return file_handler.load_data_file('ai_config.dat', default={
            'api_key': '',
            'num_colors': 5,
            'keywords': ''
        })

