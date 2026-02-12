"""
Custom color harmony management module (remake)
Simple system using only HSV sliders and fixed colors
"""

import colorsys


class CustomHarmonyManager:
    """Custom color harmony management class"""
    
    def __init__(self, file_handler):
        self.file_handler = file_handler
        self.harmonies = self.load_harmonies()
    
    def load_harmonies(self):
        """Load saved harmonies (using FileHandler)"""
        return self.file_handler.load_data_file('custom_harmonies.dat', default=[])
    
    def save_harmonies(self):
        """Save harmonies (using FileHandler)"""
        return self.file_handler.save_data_file('custom_harmonies.dat', self.harmonies)
    
    def add_harmony(self, harmony_data):
        """Add new harmony"""
        self.harmonies.append(harmony_data)
        return self.save_harmonies()
    
    def update_harmony(self, index, harmony_data):
        """Update harmony"""
        if 0 <= index < len(self.harmonies):
            self.harmonies[index] = harmony_data
            return self.save_harmonies()
        return False
    
    def delete_harmony(self, index):
        """Delete harmony"""
        if 0 <= index < len(self.harmonies):
            self.harmonies.pop(index)
            return self.save_harmonies()
        return False
    
    def apply_harmony(self, base_color_hex, harmony_index):
        """Generate color list by applying harmony rules"""
        if not (0 <= harmony_index < len(self.harmonies)):
            return []
        
        harmony = self.harmonies[harmony_index]
        colors_data = harmony.get('colors', [])
        
        # HEX to RGB
        base_rgb = self.hex_to_rgb(base_color_hex)
        base_h, base_s, base_v = colorsys.rgb_to_hsv(base_rgb[0]/255, base_rgb[1]/255, base_rgb[2]/255)
        
        colors = []
        for color_data in colors_data:
            color_type = color_data.get('type')
            
            if color_type == 'hsv':
                # Apply HSV slider values
                h_offset = color_data.get('h_offset', 0) / 360  # Convert -180~180 degrees to 0~1
                s_offset = color_data.get('s_offset', 0) / 100  # Convert -100~100% to -1~1
                v_offset = color_data.get('v_offset', 0) / 100  # Convert -100~100% to -1~1
                
                new_h = (base_h + h_offset) % 1.0
                new_s = max(0, min(1, base_s + s_offset))
                new_v = max(0, min(1, base_v + v_offset))
                
                rgb = colorsys.hsv_to_rgb(new_h, new_s, new_v)
                colors.append(self.rgb_to_hex(tuple(int(c * 255) for c in rgb)))
            
            elif color_type == 'fixed':
                # Fixed color
                fixed_color = color_data.get('color', '#FFFFFF')
                colors.append(fixed_color)
        
        return colors
    
    @staticmethod
    def hex_to_rgb(hex_color):
        """Convert HEX to RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    @staticmethod
    def rgb_to_hex(rgb):
        """Convert RGB to HEX"""
        return '#{:02x}{:02x}{:02x}'.format(*rgb)



