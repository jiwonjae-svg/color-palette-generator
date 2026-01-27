"""
Color Palette Generator - Modern CustomTkinter UI
A SaaS-style dashboard for color palette creation and management.

Design System:
- Theme: Dark Mode (Anthracite #1E1E1E)
- Accent: Soft Blue (#3B82F6)
- Corner Radius: 10px
- Font: Segoe UI / SF Pro Display style
"""

from PIL import Image, ImageTk, ImageGrab, ImageDraw
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser
import os
import datetime
import tempfile
import logging
import hashlib
import colorsys
import base64
from cryptography.fernet import Fernet

# Import new modules
from color_generator import ColorPaletteGenerator
from file_handler import FileHandler
from config_manager import ConfigManager
from image_recolorer import ImageRecolorer
from language_manager import LanguageManager

# Import embedded icon
try:
    from embedded_icon import EMBEDDED_ICON_DATA
except ImportError:
    EMBEDDED_ICON_DATA = None

# Import color adjuster if available
try:
    from color_adjuster import apply_contrast, apply_warmth
    COLOR_ADJUSTER_AVAILABLE = True
except Exception:
    COLOR_ADJUSTER_AVAILABLE = False
    apply_contrast = None
    apply_warmth = None

# ============== Design System Constants ==============
COLORS = {
    'bg_dark': '#1E1E1E',          # Anthracite - Main background
    'bg_secondary': '#2D2D2D',     # Secondary background
    'bg_card': '#363636',          # Card background
    'bg_hover': '#404040',         # Hover state
    'accent': '#3B82F6',           # Soft Blue - Primary accent
    'accent_hover': '#2563EB',     # Accent hover
    'accent_light': '#60A5FA',     # Light accent
    'text_primary': '#FFFFFF',     # Primary text
    'text_secondary': '#A1A1AA',   # Secondary text
    'text_muted': '#71717A',       # Muted text
    'border': '#404040',           # Border color
    'success': '#22C55E',          # Success green
    'warning': '#F59E0B',          # Warning amber
    'error': '#EF4444',            # Error red
}

CORNER_RADIUS = 10
PADDING = 10
FONT_FAMILY = "Segoe UI"

# Configure CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Global icon path for all windows
_ICON_PATH = None


def get_icon_path():
    """Get or create icon path from embedded data"""
    global _ICON_PATH
    
    if _ICON_PATH and os.path.exists(_ICON_PATH):
        return _ICON_PATH
    
    if EMBEDDED_ICON_DATA:
        try:
            icon_data = base64.b64decode(EMBEDDED_ICON_DATA.strip())
            temp_icon = tempfile.NamedTemporaryFile(delete=False, suffix='.ico')
            temp_icon.write(icon_data)
            temp_icon.close()
            _ICON_PATH = temp_icon.name
            return _ICON_PATH
        except Exception:
            pass
    
    icon_path = os.path.join(os.path.dirname(__file__), 'icon.ico')
    if os.path.exists(icon_path):
        _ICON_PATH = icon_path
        return _ICON_PATH
    
    return None


def set_window_icon(window):
    """Apply icon to any window (main or Toplevel)"""
    try:
        icon_path = get_icon_path()
        if icon_path:
            window.iconbitmap(icon_path)
    except Exception:
        pass


class ModernCard(ctk.CTkFrame):
    """A modern card component with subtle shadow effect"""
    def __init__(self, master, title=None, **kwargs):
        super().__init__(
            master, 
            corner_radius=CORNER_RADIUS,
            fg_color=COLORS['bg_card'],
            border_width=1,
            border_color=COLORS['border'],
            **kwargs
        )
        
        if title:
            self.title_label = ctk.CTkLabel(
                self,
                text=title,
                font=ctk.CTkFont(family=FONT_FAMILY, size=14, weight="bold"),
                text_color=COLORS['text_primary']
            )
            self.title_label.pack(anchor="w", padx=15, pady=(15, 10))


class ModernButton(ctk.CTkButton):
    """Styled button with consistent design"""
    def __init__(self, master, text="", **kwargs):
        default_kwargs = {
            'corner_radius': CORNER_RADIUS,
            'fg_color': COLORS['accent'],
            'hover_color': COLORS['accent_hover'],
            'text_color': COLORS['text_primary'],
            'font': ctk.CTkFont(family=FONT_FAMILY, size=12),
            'height': 36
        }
        default_kwargs.update(kwargs)
        super().__init__(master, text=text, **default_kwargs)


class ModernSecondaryButton(ctk.CTkButton):
    """Secondary styled button"""
    def __init__(self, master, text="", **kwargs):
        default_kwargs = {
            'corner_radius': CORNER_RADIUS,
            'fg_color': COLORS['bg_secondary'],
            'hover_color': COLORS['bg_hover'],
            'text_color': COLORS['text_primary'],
            'border_width': 1,
            'border_color': COLORS['border'],
            'font': ctk.CTkFont(family=FONT_FAMILY, size=12),
            'height': 36
        }
        default_kwargs.update(kwargs)
        super().__init__(master, text=text, **default_kwargs)


class ModernIconButton(ctk.CTkButton):
    """Icon-only button for toolbar actions"""
    def __init__(self, master, text="", **kwargs):
        default_kwargs = {
            'corner_radius': 8,
            'fg_color': 'transparent',
            'hover_color': COLORS['bg_hover'],
            'text_color': COLORS['text_primary'],
            'font': ctk.CTkFont(size=16),
            'width': 36,
            'height': 36
        }
        default_kwargs.update(kwargs)
        super().__init__(master, text=text, **default_kwargs)


class ColorSwatch(ctk.CTkFrame):
    """A clickable color swatch with hover effect"""
    def __init__(self, master, color="#FFFFFF", size=40, command=None, **kwargs):
        super().__init__(
            master,
            width=size,
            height=size,
            corner_radius=6,
            fg_color=color,
            **kwargs
        )
        self.color = color
        self.command = command
        self.size = size
        
        # Prevent size changes
        self.pack_propagate(False)
        self.grid_propagate(False)
        
        # Bind click event
        if command:
            self.bind("<Button-1>", lambda e: command())
            self.configure(cursor="hand2")


class PaletteApp(ctk.CTk):
    """Main Application - Modern SaaS Dashboard Style"""
    
    def __init__(self):
        super().__init__()
        
        # Set window icon
        set_window_icon(self)
        
        # Initialize managers
        self.file_handler = FileHandler()
        self.config_manager = ConfigManager(self.file_handler)
        
        # Initialize language manager
        current_lang = self.config_manager.get('language', 'ko')
        self.lang = LanguageManager(current_lang)
        
        # Window configuration
        window_width = self.config_manager.get('window_width', 1100)
        window_height = self.config_manager.get('window_height', 700)
        self.geometry(f"{window_width}x{window_height}")
        self.minsize(900, 600)
        
        # Configure window background
        self.configure(fg_color=COLORS['bg_dark'])
        
        # Initialize core components
        self.generator = ColorPaletteGenerator()
        self.image_path = None
        self._temp_screenshot = None
        
        self.ai_recommender = None
        self.ai_palettes = []
        self.ai_palette_offset = 0
        
        self.selected_schemes = ['complementary', 'analogous', 'triadic', 'monochromatic']
        
        self.current_file = None
        self.is_modified = False
        
        self.auto_save_enabled = self.config_manager.get('auto_save_enabled', True)
        self.auto_save_interval = self.config_manager.get('auto_save_interval', 300) * 1000
        self.auto_save_timer = None
        
        # Recent colors storage
        self.recent_colors = self.config_manager.get('recent_colors', []) or []
        try:
            self.max_recent_colors = int(self.config_manager.get('max_recent_colors', 50))
        except Exception:
            self.max_recent_colors = 50
        self.max_recent_colors = max(1, min(100, self.max_recent_colors))

        if len(self.recent_colors) > self.max_recent_colors:
            self.recent_colors = self.recent_colors[:self.max_recent_colors]
            self.config_manager.set('recent_colors', self.recent_colors)
            self.config_manager.save_config()
        
        # Global tooltip tracker to prevent ghosting
        self.active_tooltips = []
        
        self.setup_logging()
        self.log_action("Application started")
        
        # Initialize preset palettes if not exists
        self._init_preset_palettes_async()
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.bind_shortcuts()
        self.setup_drag_drop()

        # Create UI
        self.create_widgets()
        
        self.update_title()
        
        if self.auto_save_enabled:
            self.start_auto_save()
    
    def create_widgets(self):
        """Create the main UI layout with modern dashboard design"""
        
        # ============== Header Section ==============
        self.create_header()
        
        # ============== Main Content Area ==============
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Create TabView for main content
        self.tabview = ctk.CTkTabview(
            self.main_container,
            corner_radius=CORNER_RADIUS,
            fg_color=COLORS['bg_secondary'],
            segmented_button_fg_color=COLORS['bg_card'],
            segmented_button_selected_color=COLORS['accent'],
            segmented_button_unselected_color=COLORS['bg_card'],
            text_color=COLORS['text_primary'],
        )
        self.tabview.pack(fill="both", expand=True)
        
        # Add tabs with language support
        self.tab_palette = self.tabview.add(self.lang.get('tab_palette'))
        self.tab_recolor = self.tabview.add(self.lang.get('tab_recolor'))
        self.tab_custom = self.tabview.add(self.lang.get('tab_custom_harmony'))
        
        # Create content for each tab
        self.create_palette_tab()
        self.create_recolor_tab()
        self.create_custom_harmony_tab()
        
        # Initialize saved palettes
        self.saved_palettes = []
        self._saved_counter = 0
        self._saved_selected = None
        
        # Create initial saved palette
        name = self.lang.get('new_palette_numbered').format(i=self._saved_counter + 1)
        self._saved_counter += 1
        entry = {'name': name, 'colors': []}
        self.saved_palettes.append(entry)
        if self.saved_palettes:
            self._saved_selected = 0
            self.render_saved_list()
        
        # Initial generate
        self.on_source_change()
        self.generate()
    
    def create_header(self):
        """Create the modern app header with navigation"""
        self.header = ctk.CTkFrame(
            self,
            height=60,
            corner_radius=0,
            fg_color=COLORS['bg_secondary']
        )
        self.header.pack(fill="x", padx=0, pady=0)
        self.header.pack_propagate(False)
        
        # Left section: Logo and title
        left_section = ctk.CTkFrame(self.header, fg_color="transparent")
        left_section.pack(side="left", padx=20, fill="y")
        
        # App title
        title_label = ctk.CTkLabel(
            left_section,
            text="🎨 Color Palette Generator",
            font=ctk.CTkFont(family=FONT_FAMILY, size=18, weight="bold"),
            text_color=COLORS['text_primary']
        )
        title_label.pack(side="left", pady=15)
        
        # Right section: Action buttons
        right_section = ctk.CTkFrame(self.header, fg_color="transparent")
        right_section.pack(side="right", padx=20, fill="y")
        
        # File operations dropdown
        self.file_menu_btn = ModernSecondaryButton(
            right_section,
            text=f"📁 {self.lang.get('menu_file')}",
            width=100,
            command=self.show_file_menu
        )
        self.file_menu_btn.pack(side="left", padx=5, pady=12)
        
        # Settings button
        self.settings_btn = ModernSecondaryButton(
            right_section,
            text=f"⚙️ {self.lang.get('menu_settings')}",
            width=100,
            command=self.open_settings
        )
        self.settings_btn.pack(side="left", padx=5, pady=12)
        
        # Tools button
        self.tools_btn = ModernSecondaryButton(
            right_section,
            text=f"🛠️ {self.lang.get('tools')}",
            width=100,
            command=self.show_tools_menu
        )
        self.tools_btn.pack(side="left", padx=5, pady=12)
    
    def create_palette_tab(self):
        """Create the main palette generation tab with sidebar layout"""
        
        # Main container with two columns
        content_frame = ctk.CTkFrame(self.tab_palette, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Configure grid
        content_frame.grid_columnconfigure(0, weight=1, minsize=280)  # Left sidebar
        content_frame.grid_columnconfigure(1, weight=3)  # Main content
        content_frame.grid_rowconfigure(0, weight=1)
        
        # ============== Left Sidebar: Color Settings ==============
        self.create_sidebar(content_frame)
        
        # ============== Right Main Content: Results ==============
        self.create_main_content(content_frame)
    
    def create_sidebar(self, parent):
        """Create the left sidebar with color settings"""
        sidebar_container = ctk.CTkFrame(
            parent,
            corner_radius=CORNER_RADIUS,
            fg_color=COLORS['bg_card'],
            border_width=1,
            border_color=COLORS['border']
        )
        sidebar_container.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=0)
        
        # Sidebar title (fixed at top)
        sidebar_title = ctk.CTkLabel(
            sidebar_container,
            text=self.lang.get('color_settings'),
            font=ctk.CTkFont(family=FONT_FAMILY, size=14, weight="bold"),
            text_color=COLORS['text_primary']
        )
        sidebar_title.pack(anchor="w", padx=15, pady=(15, 10))
        
        # Scrollable content area
        sidebar = ctk.CTkScrollableFrame(
            sidebar_container,
            fg_color="transparent",
            scrollbar_button_color=COLORS['accent'],
            scrollbar_button_hover_color=COLORS['accent_hover']
        )
        sidebar.pack(fill="both", expand=True, padx=5, pady=(0, 5))
        
        # Source type selection
        source_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        source_frame.pack(fill="x", padx=15, pady=5)
        
        source_label = ctk.CTkLabel(
            source_frame,
            text=self.lang.get('source_type'),
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            text_color=COLORS['text_secondary']
        )
        source_label.pack(anchor="w")
        
        self.source_type = ctk.StringVar(value='hex')
        
        # Radio buttons for source type
        radio_frame = ctk.CTkFrame(source_frame, fg_color="transparent")
        radio_frame.pack(fill="x", pady=5)
        
        self.rb_hex = ctk.CTkRadioButton(
            radio_frame,
            text=self.lang.get('pick_color'),
            variable=self.source_type,
            value='hex',
            command=self.on_source_change,
            fg_color=COLORS['accent'],
            hover_color=COLORS['accent_hover'],
            text_color=COLORS['text_primary']
        )
        self.rb_hex.pack(anchor="w", pady=2)
        
        self.rb_img = ctk.CTkRadioButton(
            radio_frame,
            text=self.lang.get('from_image'),
            variable=self.source_type,
            value='image',
            command=self.on_source_change,
            fg_color=COLORS['accent'],
            hover_color=COLORS['accent_hover'],
            text_color=COLORS['text_primary']
        )
        self.rb_img.pack(anchor="w", pady=2)
        
        self.rb_ai = ctk.CTkRadioButton(
            radio_frame,
            text=self.lang.get('ai_palette'),
            variable=self.source_type,
            value='ai',
            command=self.on_source_change,
            fg_color=COLORS['accent'],
            hover_color=COLORS['accent_hover'],
            text_color=COLORS['text_primary']
        )
        self.rb_ai.pack(anchor="w", pady=2)
        
        # Separator
        sep1 = ctk.CTkFrame(sidebar, height=1, fg_color=COLORS['border'])
        sep1.pack(fill="x", padx=15, pady=15)
        
        # Color picker section
        color_section = ctk.CTkFrame(sidebar, fg_color="transparent")
        color_section.pack(fill="x", padx=15, pady=5)
        
        color_label = ctk.CTkLabel(
            color_section,
            text=self.lang.get('selected_color'),
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            text_color=COLORS['text_secondary']
        )
        color_label.pack(anchor="w")
        
        # Color swatch and picker
        self.hex_entry = ctk.StringVar(value="#3498db")
        
        swatch_row = ctk.CTkFrame(color_section, fg_color="transparent")
        swatch_row.pack(fill="x", pady=10)
        
        # Color swatch display (using Canvas for color display)
        self.color_swatch_frame = ctk.CTkFrame(
            swatch_row,
            width=80,
            height=50,
            corner_radius=8,
            fg_color="#3498db"
        )
        self.color_swatch_frame.pack(side="left")
        self.color_swatch_frame.pack_propagate(False)
        
        # Color info
        self.color_info_frame = ctk.CTkFrame(swatch_row, fg_color="transparent")
        self.color_info_frame.pack(side="left", padx=15, fill="y")
        
        self.lbl_hex_value = ctk.CTkLabel(
            self.color_info_frame,
            text="#3498db",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            text_color=COLORS['text_primary']
        )
        self.lbl_hex_value.pack(anchor="w")
        
        self.lbl_rgb_value = ctk.CTkLabel(
            self.color_info_frame,
            text="RGB(52, 152, 219)",
            font=ctk.CTkFont(family=FONT_FAMILY, size=11),
            text_color=COLORS['text_secondary']
        )
        self.lbl_rgb_value.pack(anchor="w")
        
        # Color picker button
        self.btn_color_picker = ModernButton(
            color_section,
            text=f"🎨 {self.lang.get('pick_color')}",
            command=self.open_color_picker
        )
        self.btn_color_picker.pack(fill="x", pady=5)
        
        # Image selection
        self.btn_select_img = ModernSecondaryButton(
            color_section,
            text=f"📷 {self.lang.get('select_image')}",
            command=self.select_image
        )
        self.btn_select_img.pack(fill="x", pady=5)
        
        # Screen picker
        self.btn_screen_pick = ModernSecondaryButton(
            color_section,
            text=f"🔍 {self.lang.get('extract_from_screen')}",
            command=self.start_screen_picker
        )
        self.btn_screen_pick.pack(fill="x", pady=5)
        
        # Image info label
        self.lbl_image = ctk.CTkLabel(
            color_section,
            text=self.lang.get('no_file_selected'),
            font=ctk.CTkFont(family=FONT_FAMILY, size=11),
            text_color=COLORS['text_muted']
        )
        self.lbl_image.pack(anchor="w", pady=5)
        
        # Image thumbnail
        self.img_thumbnail_label = ctk.CTkLabel(color_section, text="")
        self.img_thumbnail_label.pack(pady=5)
        
        # Separator
        sep2 = ctk.CTkFrame(sidebar, height=1, fg_color=COLORS['border'])
        sep2.pack(fill="x", padx=15, pady=15)
        
        # Action buttons
        action_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        action_frame.pack(fill="x", padx=15, pady=5)
        
        self.btn_generate = ModernButton(
            action_frame,
            text=f"✨ {self.lang.get('generate')}",
            command=self.generate,
            height=48,
            font=ctk.CTkFont(family=FONT_FAMILY, size=15, weight="bold")
        )
        self.btn_generate.pack(fill="x", pady=5)
        
        self.btn_random = ModernSecondaryButton(
            action_frame,
            text=f"🎲 {self.lang.get('random_color')}",
            command=self.generate_random
        )
        self.btn_random.pack(fill="x", pady=5)
        
        self.btn_harmony = ModernSecondaryButton(
            action_frame,
            text=f"⚡ {self.lang.get('harmony_options')}",
            command=self.open_harmony_selector
        )
        self.btn_harmony.pack(fill="x", pady=5)
        
        # Recent colors section at bottom
        sep3 = ctk.CTkFrame(sidebar, height=1, fg_color=COLORS['border'])
        sep3.pack(fill="x", padx=15, pady=15)
        
        recent_header = ctk.CTkFrame(sidebar, fg_color="transparent")
        recent_header.pack(fill="x", padx=15)
        
        recent_label = ctk.CTkLabel(
            recent_header,
            text=self.lang.get('recent_colors_title'),
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            text_color=COLORS['text_primary']
        )
        recent_label.pack(side="left")
        
        btn_clear_recent = ModernIconButton(
            recent_header,
            text="🗑️",
            command=self.clear_recent_colors,
            width=30,
            height=30
        )
        btn_clear_recent.pack(side="right")
        
        # Recent colors grid
        self.recent_colors_frame = ctk.CTkScrollableFrame(
            sidebar,
            height=80,
            fg_color="transparent",
            orientation="horizontal"
        )
        self.recent_colors_frame.pack(fill="x", padx=15, pady=10)
        
        self.update_recent_colors_display()
    
    def create_main_content(self, parent):
        """Create the main content area with palette results and saved palettes"""
        main_content = ctk.CTkFrame(parent, fg_color="transparent")
        main_content.grid(row=0, column=1, sticky="nsew")
        
        # Configure grid for main content
        main_content.grid_columnconfigure(0, weight=2)  # Palette display
        main_content.grid_columnconfigure(1, weight=1)  # Saved palettes
        main_content.grid_rowconfigure(0, weight=1)
        
        # ============== Palette Display (Left) ==============
        self.palette_card = ModernCard(main_content, title=self.lang.get('generated_palette'))
        self.palette_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=0)
        
        # Scrollable frame for palette colors
        self.palette_scroll = ctk.CTkScrollableFrame(
            self.palette_card,
            fg_color="transparent"
        )
        self.palette_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Placeholder for palette_inner (for compatibility with existing code)
        self.palette_inner = self.palette_scroll
        
        # ============== Saved Palettes (Right) ==============
        self.saved_card = ModernCard(main_content, title=self.lang.get('saved_palettes'))
        self.saved_card.grid(row=0, column=1, sticky="nsew", pady=0)
        
        # Saved palettes toolbar
        saved_toolbar = ctk.CTkFrame(self.saved_card, fg_color="transparent")
        saved_toolbar.pack(fill="x", padx=15, pady=5)
        
        # Icon buttons for palette management
        self.btn_add = ModernIconButton(saved_toolbar, text="📄", command=self.add_saved_palette)
        self.btn_add.pack(side="left", padx=2)
        self.create_tooltip(self.btn_add, self.lang.get('tooltip_add_palette'))
        
        self.btn_delete = ModernIconButton(saved_toolbar, text="🗑️", command=self.remove_saved_palette)
        self.btn_delete.pack(side="left", padx=2)
        self.create_tooltip(self.btn_delete, self.lang.get('tooltip_delete_palette'))
        
        self.btn_copy = ModernIconButton(saved_toolbar, text="📋", command=self.copy_palette)
        self.btn_copy.pack(side="left", padx=2)
        self.create_tooltip(self.btn_copy, self.lang.get('tooltip_copy_palette'))
        
        self.btn_load = ModernIconButton(saved_toolbar, text="📂", command=self.load_palette)
        self.btn_load.pack(side="left", padx=2)
        self.create_tooltip(self.btn_load, self.lang.get('tooltip_load_palette'))
        
        if COLOR_ADJUSTER_AVAILABLE:
            self.btn_adjust = ModernIconButton(saved_toolbar, text="🎨", command=self.open_color_adjuster)
            self.btn_adjust.pack(side="left", padx=2)
            self.create_tooltip(self.btn_adjust, self.lang.get('tooltip_adjust_color'))
        
        # Scrollable list of saved palettes
        self.saved_scroll = ctk.CTkScrollableFrame(
            self.saved_card,
            fg_color="transparent"
        )
        self.saved_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        # For compatibility
        self.saved_list_container = self.saved_scroll
    
    def create_recolor_tab(self):
        """Create the image recoloring tab"""
        # Placeholder - will be filled when tab is selected
        placeholder = ctk.CTkLabel(
            self.tab_recolor,
            text=f"🖼️ {self.lang.get('apply_palette_to_image')}",
            font=ctk.CTkFont(family=FONT_FAMILY, size=16)
        )
        placeholder.pack(expand=True)
        
        open_btn = ModernButton(
            self.tab_recolor,
            text=self.lang.get('apply_palette_to_image'),
            command=self.apply_palette_to_image
        )
        open_btn.pack(pady=20)
    
    def create_custom_harmony_tab(self):
        """Create the custom harmony editor tab"""
        placeholder = ctk.CTkLabel(
            self.tab_custom,
            text=f"⚙️ {self.lang.get('custom_color_harmonies')}",
            font=ctk.CTkFont(family=FONT_FAMILY, size=16)
        )
        placeholder.pack(expand=True)
        
        open_btn = ModernButton(
            self.tab_custom,
            text=self.lang.get('custom_color_harmonies'),
            command=self.open_custom_harmony
        )
        open_btn.pack(pady=20)

    # ============== Color Swatch Update ==============
    def _update_color_swatch(self, hex_color):
        """Update the color swatch display"""
        try:
            self.color_swatch_frame.configure(fg_color=hex_color)
            self.lbl_hex_value.configure(text=hex_color.upper())
            
            rgb = self.generator.hex_to_rgb(hex_color)
            self.lbl_rgb_value.configure(text=f"RGB({rgb[0]}, {rgb[1]}, {rgb[2]})")
        except Exception:
            pass
    
    # ============== Recent Colors ==============
    def add_to_recent_colors(self, hex_color):
        """Add a color to recent colors history"""
        hex_color = hex_color.upper()
        
        if hex_color in self.recent_colors:
            self.recent_colors.remove(hex_color)
        
        self.recent_colors.insert(0, hex_color)
        self.recent_colors = self.recent_colors[:self.max_recent_colors]
        
        self.config_manager.set('recent_colors', self.recent_colors)
        self.config_manager.save_config()
        
        self.update_recent_colors_display()
    
    def update_recent_colors_display(self):
        """Update the recent colors display panel"""
        # Clear existing widgets
        for widget in self.recent_colors_frame.winfo_children():
            widget.destroy()
        
        if not self.recent_colors:
            empty_label = ctk.CTkLabel(
                self.recent_colors_frame,
                text=self.lang.get('recent_colors_empty'),
                font=ctk.CTkFont(family=FONT_FAMILY, size=10),
                text_color=COLORS['text_muted']
            )
            empty_label.pack(side="left", padx=5)
            return
        
        for hex_color in self.recent_colors[:20]:  # Show max 20
            swatch = ColorSwatch(
                self.recent_colors_frame,
                color=hex_color,
                size=32,
                command=lambda c=hex_color: self._use_color(c)
            )
            swatch.pack(side="left", padx=2, pady=2)
    
    def _use_color(self, hex_color):
        """Use a color from recent colors"""
        self.hex_entry.set(hex_color)
        self._update_color_swatch(hex_color)
        self.log_action(f"Used color: {hex_color}")
    
    def clear_recent_colors(self):
        """Clear recent colors history"""
        if not self.recent_colors:
            return
        
        self.recent_colors = []
        self.config_manager.set('recent_colors', [])
        self.config_manager.save_config()
        self.update_recent_colors_display()
        self.log_action("Cleared recent colors history")

    # ============== Source Type Change ==============
    def on_source_change(self):
        """Handle source type radio button changes"""
        mode = self.source_type.get()
        
        if mode == 'hex':
            self.btn_color_picker.configure(state="normal")
            self.btn_select_img.configure(state="disabled")
        elif mode == 'image':
            self.btn_color_picker.configure(state="disabled")
            self.btn_select_img.configure(state="normal")
        elif mode == 'ai':
            self.btn_color_picker.configure(state="disabled")
            self.btn_select_img.configure(state="disabled")

    # ============== Color Picker ==============
    def open_color_picker(self):
        """Open color chooser dialog"""
        current_color = self.hex_entry.get()
        try:
            color_result = colorchooser.askcolor(color=current_color, title=self.lang.get('pick_color_title'))
            if color_result[1]:
                hex_color = color_result[1]
                self.hex_entry.set(hex_color)
                self._update_color_swatch(hex_color)
                self.add_to_recent_colors(hex_color)
        except Exception as e:
            messagebox.showerror(self.lang.get('error'), self.lang.get('msg_color_picker_failed').format(error=str(e)))

    # ============== Image Selection ==============
    def select_image(self):
        """Select image with validation"""
        if getattr(self, '_temp_screenshot', None):
            try:
                os.unlink(self._temp_screenshot)
            except Exception:
                pass
            self._temp_screenshot = None

        path = filedialog.askopenfilename(
            title=self.lang.get('dialog_select_image'),
            filetypes=[
                (self.lang.get('image_files'), "*.png;*.jpg;*.jpeg;*.bmp;*.gif"),
                (self.lang.get('all_files'), "*.*"),
            ],
        )
        if not path:
            return
        
        try:
            if not os.path.exists(path):
                messagebox.showerror(self.lang.get('error'), self.lang.get('msg_file_not_found'))
                return
            
            file_size = os.path.getsize(path)
            if file_size > 50 * 1024 * 1024:
                response = messagebox.askyesno(
                    self.lang.get('msg_large_file_title'),
                    self.lang.get('msg_large_file_prompt').format(size_mb=file_size // (1024 * 1024)),
                )
                if not response:
                    return
            
            self.image_path = path
            self.log_action(f"Selected image: {os.path.basename(path)}")
            
            name = os.path.basename(path)
            max_len = 20
            if len(name) > max_len:
                name = name[:max_len-3] + "..."
            self.lbl_image.configure(text=name)
            
            # Create thumbnail
            try:
                img = Image.open(path)
                img.thumbnail((48, 48), Image.Resampling.LANCZOS)
                photo = ctk.CTkImage(light_image=img, dark_image=img, size=(48, 48))
                self.img_thumbnail_label.configure(image=photo, text="")
                self.img_thumbnail = photo
                img.close()
            except Exception as e:
                self.log_action(f"Thumbnail creation failed: {str(e)}")
                self.img_thumbnail_label.configure(image=None, text="📷")
            
            self.extracted_colors = []
            
        except Exception as e:
            messagebox.showerror(self.lang.get('error'), self.lang.get('msg_image_load_failed').format(error=str(e)))
            self.log_action(f"Image selection failed: {str(e)}")

    # ============== Screen Picker ==============
    def start_screen_picker(self):
        """Begin screen color picker"""
        try:
            try:
                self._prev_alpha = self.attributes('-alpha')
            except Exception:
                self._prev_alpha = 1.0
            
            try:
                self.attributes('-alpha', 0.0)
                self.update()
                self._did_withdraw = False
            except Exception:
                try:
                    self.withdraw()
                    self._did_withdraw = True
                except Exception:
                    self._did_withdraw = False

            self.after(120, self._capture_and_show_picker)
        except Exception as e:
            messagebox.showerror(self.lang.get('error'), self.lang.get('msg_screen_picker_failed').format(error=str(e)))

    def _capture_and_show_picker(self):
        """Capture screen and show color picker overlay"""
        try:
            screen = ImageGrab.grab(all_screens=True)
        except TypeError:
            try:
                screen = ImageGrab.grab()
            except Exception as e:
                self._restore_window()
                messagebox.showerror(self.lang.get('error'), self.lang.get('msg_capture_failed').format(error=str(e)))
                return
        except Exception as e:
            self._restore_window()
            messagebox.showerror(self.lang.get('error'), self.lang.get('msg_capture_failed').format(error=str(e)))
            return

        self._screen_image = screen
        img_w, img_h = screen.size

        x0 = 0
        y0 = 0
        width = img_w
        height = img_h
        
        try:
            if os.name == 'nt':
                import ctypes
                user32 = ctypes.windll.user32
                SM_XVIRTUALSCREEN = 76
                SM_YVIRTUALSCREEN = 77
                SM_CXVIRTUALSCREEN = 78
                SM_CYVIRTUALSCREEN = 79
                xv = user32.GetSystemMetrics(SM_XVIRTUALSCREEN)
                yv = user32.GetSystemMetrics(SM_YVIRTUALSCREEN)
                cvw = user32.GetSystemMetrics(SM_CXVIRTUALSCREEN)
                cvh = user32.GetSystemMetrics(SM_CYVIRTUALSCREEN)
                x0, y0, width, height = int(xv), int(yv), int(cvw), int(cvh)
        except Exception:
            x0, y0 = 0, 0
            width, height = img_w, img_h

        picker = tk.Toplevel(self)
        picker.overrideredirect(True)
        picker.geometry(f"{width}x{height}+{x0}+{y0}")
        try:
            picker.attributes('-topmost', True)
        except Exception:
            pass
        picker.lift()

        try:
            display_img = screen.resize((width, height))
        except Exception:
            display_img = screen

        photo = ImageTk.PhotoImage(display_img)
        
        mode = self.source_type.get()
        if mode == 'image':
            self._setup_region_picker(picker, photo, screen, x0, y0, width, height)
        else:
            self._setup_pixel_picker(picker, photo, x0, y0, width, height)

        self._screen_origin = (x0, y0)
        self._virtual_size = (width, height)
        picker.focus_force()
    
    def _setup_pixel_picker(self, picker, photo, x0, y0, width, height):
        """Setup single pixel color picker"""
        lbl = tk.Label(picker, image=photo)
        lbl.image = photo
        lbl.place(x=0, y=0, width=width, height=height)

        floating = tk.Label(picker, text='', bd=1, relief='solid', padx=12, pady=8, 
                           font=(FONT_FAMILY, 14, 'bold'))
        floating.place(x=20, y=20)

        self._picker_win = picker
        self._picker_floating = floating

        picker.bind('<Motion>', self._on_picker_move)
        picker.bind('<Button-1>', self._on_picker_click)
    
    def _setup_region_picker(self, picker, photo, screen, x0, y0, width, height):
        """Setup region selection picker for image mode"""
        canvas = tk.Canvas(picker, width=width, height=height, highlightthickness=0)
        canvas.photo = photo
        canvas.create_image(0, 0, image=photo, anchor='nw')
        canvas.pack(fill='both', expand=True)

        canvas._rect_id = None
        canvas._start = None

        def on_press(e):
            canvas._start = (e.x_root, e.y_root)
            if canvas._rect_id:
                canvas.delete(canvas._rect_id)
                canvas._rect_id = None

        def on_drag(e):
            if not canvas._start:
                return
            x0_root, y0_root = canvas._start
            x1_root, y1_root = e.x_root, e.y_root
            lx0 = int((x0_root - x0) * (width / max(1, width)))
            ly0 = int((y0_root - y0) * (height / max(1, height)))
            lx1 = int((x1_root - x0) * (width / max(1, width)))
            ly1 = int((y1_root - y0) * (height / max(1, height)))
            if canvas._rect_id:
                canvas.coords(canvas._rect_id, lx0, ly0, lx1, ly1)
            else:
                canvas._rect_id = canvas.create_rectangle(lx0, ly0, lx1, ly1, 
                                                          outline=COLORS['accent'], width=2)

        def on_release(e):
            if not canvas._start:
                return
            x0_root, y0_root = canvas._start
            x1_root, y1_root = e.x_root, e.y_root
            
            img_w, img_h = screen.size
            vw, vh = width, height
            scale_x = img_w / max(1, vw)
            scale_y = img_h / max(1, vh)
            sx = int((min(x0_root, x1_root) - x0) * scale_x)
            sy = int((min(y0_root, y1_root) - y0) * scale_y)
            ex = int((max(x0_root, x1_root) - x0) * scale_x)
            ey = int((max(y0_root, y1_root) - y0) * scale_y)
            
            sx = max(0, min(img_w - 1, sx))
            sy = max(0, min(img_h - 1, sy))
            ex = max(0, min(img_w, ex))
            ey = max(0, min(img_h, ey))
            
            if ex <= sx or ey <= sy:
                canvas._start = None
                if canvas._rect_id:
                    canvas.delete(canvas._rect_id)
                    canvas._rect_id = None
                return

            region = screen.crop((sx, sy, ex, ey))

            try:
                temp_fd, temp_path = tempfile.mkstemp(suffix='.png')
                os.close(temp_fd)
                region.save(temp_path)
            except Exception as err:
                messagebox.showerror(self.lang.get('save_error_title'), 
                                   self.lang.get('msg_save_screenshot_failed').format(error=str(err)))
                canvas._start = None
                return

            try:
                picker.destroy()
            except Exception:
                pass

            self._restore_window()

            try:
                thumb = region.copy()
                thumb.thumbnail((48, 48))
                photo_thumb = ctk.CTkImage(light_image=thumb, dark_image=thumb, size=(48, 48))
                self.img_thumbnail_label.configure(image=photo_thumb, text="")
                self.img_thumbnail = photo_thumb
                self.lbl_image.configure(text=self.lang.get('screenshot_label'))
                self.image_path = temp_path
                self._temp_screenshot = temp_path
            except Exception:
                try:
                    os.unlink(temp_path)
                except Exception:
                    pass

            try:
                colors = self.generator.extract_main_colors(temp_path, num_colors=5)
                self.extracted_colors = colors
            except Exception:
                self.extracted_colors = []

        canvas.bind('<Button-1>', on_press)
        canvas.bind('<B1-Motion>', on_drag)
        canvas.bind('<ButtonRelease-1>', on_release)
    
    def _on_picker_move(self, event):
        """Handle mouse movement in color picker"""
        x = event.x_root
        y = event.y_root
        img = self._screen_image
        x0, y0 = getattr(self, '_screen_origin', (0, 0))
        
        img_w, img_h = img.size
        vw, vh = getattr(self, '_virtual_size', (img_w, img_h))
        vw = max(1, int(vw))
        vh = max(1, int(vh))
        scale_x = img_w / vw
        scale_y = img_h / vh

        local_x = int((x - x0) * scale_x)
        local_y = int((y - y0) * scale_y)
        
        if local_x < 0 or local_y < 0 or local_x >= img_w or local_y >= img_h:
            return
        
        try:
            rgb = img.getpixel((local_x, local_y))
        except Exception:
            return
        
        if isinstance(rgb, int):
            rgb = (rgb, rgb, rgb)

        hx = self.generator.rgb_to_hex(rgb)
        lum = (0.299*rgb[0] + 0.587*rgb[1] + 0.114*rgb[2])
        txt_fill = '#000000' if lum > 160 else '#ffffff'

        f = self._picker_floating
        f.config(text=hx, bg=hx, fg=txt_fill)

        try:
            vw = int(self._picker_win.winfo_width())
            vh = int(self._picker_win.winfo_height())
        except Exception:
            vw, vh = img_w, img_h

        midx = vw / 2
        midy = vh / 2

        pad = 8
        fw = f.winfo_reqwidth()
        fh = f.winfo_reqheight()

        rel_x = x - x0
        rel_y = y - y0

        if rel_x <= midx and rel_y <= midy:
            quadrant = 1
        elif rel_x > midx and rel_y <= midy:
            quadrant = 2
        elif rel_x <= midx and rel_y > midy:
            quadrant = 3
        else:
            quadrant = 4

        opp = {1:4, 2:3, 3:2, 4:1}[quadrant]

        if opp == 1:
            place_x = int(pad)
            place_y = int(pad)
        elif opp == 2:
            place_x = int(vw - pad - fw)
            place_y = int(pad)
        elif opp == 3:
            place_x = int(pad)
            place_y = int(vh - pad - fh)
        else:
            place_x = int(vw - pad - fw)
            place_y = int(vh - pad - fh)

        place_x = max(4, min(place_x, vw - fw - 4))
        place_y = max(4, min(place_y, vh - fh - 4))
        f.place(x=place_x, y=place_y)

    def _on_picker_click(self, event):
        """Handle click in color picker"""
        hx = self._picker_floating.cget('text')
        try:
            self._picker_win.destroy()
        except Exception:
            pass
        
        self._restore_window()

        try:
            self.hex_entry.set(hx)
            self._update_color_swatch(hx)
            self.add_to_recent_colors(hx)
            self.image_path = None
            self.extracted_colors = []
        except Exception:
            pass
    
    def _restore_window(self):
        """Restore main window after screen picker"""
        try:
            if getattr(self, '_did_withdraw', False):
                self.deiconify()
                self._did_withdraw = False
            else:
                self.attributes('-alpha', self._prev_alpha)
        except Exception:
            pass

    # ============== Palette Generation ==============
    def generate(self):
        """Generate palette with comprehensive validation"""
        source_type = self.source_type.get()
        try:
            if source_type == 'ai':
                self._generate_ai_palette()
                return
            elif source_type == 'hex':
                hex_code = self.hex_entry.get().strip()
                
                if not self.validate_hex_color(hex_code):
                    raise ValueError(self.lang.get('msg_invalid_hex_prompt'))
                
                palette = self.generator.generate_palette(hex_code, source_type='hex')
                self.current_palettes = [palette]
                self.log_action(f"Generated palette from HEX: {hex_code}")
            else:
                if not self.image_path:
                    raise ValueError(self.lang.get('msg_select_image_first'))
                
                if not os.path.exists(self.image_path):
                    self.image_path = None
                    self.lbl_image.configure(text=self.lang.get('no_image_label'))
                    raise ValueError(self.lang.get('msg_image_file_not_found'))
                
                approx = self.generator.approximate_color_count(self.image_path, sample_size=1000)
                k = min(5, max(1, approx))
                main_colors = self.generator.extract_main_colors(self.image_path, num_colors=k)
                
                if not main_colors:
                    raise ValueError(self.lang.get('msg_extract_colors_failed'))
                
                self.extracted_colors = main_colors
                palettes = [self.generator.generate_palette(c, source_type='rgb') for c in main_colors]
                self.current_palettes = palettes
                self.log_action(f"Generated palette from image: {os.path.basename(self.image_path)}")
                
        except ValueError as e:
            messagebox.showerror(self.lang.get('input_error_title'), str(e))
            self.log_action(f"Generate validation error: {str(e)}")
            return
        except Exception as e:
            messagebox.showerror(self.lang.get('error'), self.lang.get('msg_palette_generation_failed').format(error=str(e)))
            self.log_action(f"Generate error: {str(e)}")
            return

        self.clear_palette_display()
        
        if source_type == 'ai':
            self.display_ai_palettes(self.ai_palettes)
        elif source_type == 'hex':
            self.display_single_palette(palette)
        else:
            self.display_multiple_palettes(self.current_palettes)
    
    def _generate_ai_palette(self):
        """Generate AI color palette"""
        from ai_color_recommender import AISettings, AIColorRecommender
        
        settings = AISettings.load_settings(self.file_handler)
        api_key = settings.get('api_key', '')
        
        if not api_key:
            messagebox.showwarning(self.lang.get('warning'), self.lang.get('msg_ai_api_key_required'))
            return
        
        if not self.ai_recommender:
            try:
                self.ai_recommender = AIColorRecommender(api_key, lang=self.lang)
            except Exception as e:
                messagebox.showerror(self.lang.get('error'), self.lang.get('msg_ai_init_failed').format(error=str(e)))
                return
        
        num_colors = settings.get('num_colors', 5)
        keywords = settings.get('keywords', '')
        
        # Show loading dialog
        loading_dialog = ctk.CTkToplevel(self)
        set_window_icon(loading_dialog)
        loading_dialog.title(self.lang.get('ai_generating_title'))
        loading_dialog.geometry("300x100")
        loading_dialog.transient(self)
        loading_dialog.grab_set()
        
        ctk.CTkLabel(
            loading_dialog, 
            text=self.lang.get('ai_generating'),
            font=ctk.CTkFont(family=FONT_FAMILY, size=12)
        ).pack(pady=20)
        
        progress = ctk.CTkProgressBar(loading_dialog, mode='indeterminate', width=250)
        progress.pack(pady=10)
        progress.start()
        
        def generate_ai_palettes():
            try:
                new_palettes = self.ai_recommender.generate_palettes(
                    num_palettes=5,
                    keywords=keywords,
                    num_colors=num_colors
                )
                self.after(0, lambda: self._finish_ai_generation(new_palettes, loading_dialog))
            except Exception as e:
                error_msg = str(e)
                self.after(0, lambda: self._handle_ai_error(error_msg, loading_dialog))
        
        import threading
        thread = threading.Thread(target=generate_ai_palettes, daemon=True)
        thread.start()
    
    def _finish_ai_generation(self, new_palettes, loading_dialog):
        """Handle successful AI palette generation"""
        try:
            loading_dialog.destroy()
            
            self.ai_palettes.extend(new_palettes)
            self.current_palettes = self.ai_palettes
            self.log_action(f"Generated AI palettes: {len(new_palettes)} new palettes")
            
            self.clear_palette_display()
            self.display_ai_palettes(self.ai_palettes)
        except Exception as e:
            messagebox.showerror(self.lang.get('error'), str(e))
    
    def _handle_ai_error(self, error_msg, loading_dialog):
        """Handle AI generation error"""
        try:
            loading_dialog.destroy()
        except:
            pass
        messagebox.showerror(self.lang.get('ai_error_title'), self.lang.get('ai_generation_failed').format(error=error_msg))
        self.log_action(f"AI generation error: {error_msg}")

    def validate_hex_color(self, hex_code):
        """Validate HEX color format"""
        if not isinstance(hex_code, str):
            return False
        hex_code = hex_code.strip()
        if not hex_code.startswith('#'):
            return False
        hex_code = hex_code[1:]
        if len(hex_code) not in (3, 6):
            return False
        try:
            int(hex_code, 16)
            return True
        except ValueError:
            return False

    def generate_random(self):
        """Generate random color palette"""
        self.source_type.set('hex')
        self.on_source_change()

        rgb = self.generator.generate_random_color()
        hex_code = self.generator.rgb_to_hex(rgb)
        
        try:
            self.hex_entry.set(hex_code)
            self._update_color_swatch(hex_code)
        except Exception:
            pass
        
        self.generate()

    def clear_palette_display(self):
        """Clear palette display"""
        try:
            for child in self.palette_inner.winfo_children():
                try:
                    child.destroy()
                except Exception:
                    pass
        except Exception as e:
            self.log_action(f"Clear palette display error: {str(e)}")

    # ============== Palette Display ==============
    def draw_color_box(self, parent, hex_color, label_text, clickable=True):
        """Draw a modern color box with info, hover effect, and tooltip"""
        frm = ctk.CTkFrame(
            parent,
            fg_color=COLORS['bg_secondary'],
            corner_radius=8,
            height=60
        )
        frm.pack(fill='x', pady=3, padx=5)
        frm.pack_propagate(False)
        
        # Color swatch
        swatch = ctk.CTkFrame(
            frm,
            width=60,
            height=50,
            corner_radius=6,
            fg_color=hex_color
        )
        swatch.pack(side='left', padx=8, pady=5)
        swatch.pack_propagate(False)
        
        # Info section
        info_frame = ctk.CTkFrame(frm, fg_color="transparent")
        info_frame.pack(side='left', fill='both', expand=True, padx=10, pady=8)
        
        # Hex code
        hex_label = ctk.CTkLabel(
            info_frame,
            text=hex_color.upper(),
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            text_color=COLORS['text_primary']
        )
        hex_label.pack(anchor='w')
        
        # RGB info
        rgb_label = ctk.CTkLabel(
            info_frame,
            text=label_text,
            font=ctk.CTkFont(family=FONT_FAMILY, size=10),
            text_color=COLORS['text_secondary']
        )
        rgb_label.pack(anchor='w')
        
        if clickable:
            # Tooltip window reference
            tooltip_window = [None]
            show_after_id = [None]
            tooltip_text = self.lang.get('color_box_tooltip') if hasattr(self, 'lang') else "Left-click: Add to palette | Right-click: Set as base color"
            
            def destroy_tooltip():
                if tooltip_window[0] is not None:
                    try:
                        if hasattr(self, 'active_tooltips') and tooltip_window[0] in self.active_tooltips:
                            self.active_tooltips.remove(tooltip_window[0])
                        tooltip_window[0].destroy()
                    except Exception:
                        pass
                    tooltip_window[0] = None
            
            def show_tooltip(x_root, y_root):
                destroy_tooltip()
                tip = ctk.CTkToplevel(self)
                tip.wm_overrideredirect(True)
                try:
                    tip.wm_attributes('-topmost', True)
                except Exception:
                    pass
                tip.wm_geometry(f"+{x_root + 10}+{y_root + 10}")
                tip.configure(fg_color=COLORS['bg_card'])
                
                label = ctk.CTkLabel(
                    tip,
                    text=tooltip_text,
                    font=ctk.CTkFont(family=FONT_FAMILY, size=10),
                    text_color=COLORS['text_primary']
                )
                label.pack(padx=8, pady=4)
                tooltip_window[0] = tip
                if hasattr(self, 'active_tooltips'):
                    self.active_tooltips.append(tip)
            
            # Combined hover effect and tooltip
            def on_enter(e=None):
                frm.configure(fg_color=COLORS['bg_hover'])
                if e:
                    if show_after_id[0] is not None:
                        try:
                            frm.after_cancel(show_after_id[0])
                        except Exception:
                            pass
                        show_after_id[0] = None
                    
                    show_after_id[0] = frm.after(120, lambda: show_tooltip(e.x_root, e.y_root))
            
            def on_leave(e=None):
                frm.configure(fg_color=COLORS['bg_secondary'])
                if show_after_id[0] is not None:
                    try:
                        frm.after_cancel(show_after_id[0])
                    except Exception:
                        pass
                    show_after_id[0] = None
                destroy_tooltip()
            
            def on_motion(e):
                if tooltip_window[0] is not None:
                    try:
                        tooltip_window[0].wm_geometry(f"+{e.x_root + 10}+{e.y_root + 10}")
                    except Exception:
                        pass
            
            # Left click - add to saved palette
            def on_left_click(e=None):
                self.on_palette_color_click(hex_color)
            
            # Right click - set as base color
            def on_right_click(e=None):
                self.set_base_color(hex_color)
            
            for widget in [frm, swatch, info_frame, hex_label, rgb_label]:
                widget.bind('<Button-1>', on_left_click)
                widget.bind('<Button-3>', on_right_click)
                widget.bind('<Enter>', on_enter)
                widget.bind('<Leave>', on_leave)
                widget.bind('<Motion>', on_motion)
                try:
                    widget.configure(cursor='hand2')
                except Exception:
                    pass
    
    def set_base_color(self, hex_color):
        """Set the clicked color as the base color and regenerate palette"""
        try:
            # Set source type to HEX
            self.source_type.set('hex')
            self.on_source_change()
            
            # Set the color in hex_entry
            self.hex_entry.set(hex_color)
            self._update_color_swatch(hex_color)
            
            # Regenerate palette
            self.generate()
            self.log_action(f"Set base color to {hex_color}")
        except Exception as e:
            messagebox.showerror(self.lang.get('error'), f"Failed to set base color: {str(e)}")
    
    def get_luminance(self, hex_color):
        """Calculate luminance (brightness) of a color (0-255)"""
        try:
            rgb = self.generator.hex_to_rgb(hex_color)
            lum = int(0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2])
            return lum
        except Exception:
            return 128

    def display_single_palette(self, palette):
        """Display a single palette (for HEX mode)"""
        base = palette['base']
        if isinstance(base, list):
            base = tuple(base)
        base_hex = self.generator.rgb_to_hex(base)
        
        # Base color header
        header = ctk.CTkLabel(
            self.palette_inner,
            text=self.lang.get('base_color_label'),
            font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
            text_color=COLORS['text_primary']
        )
        header.pack(anchor='w', padx=5, pady=(10, 5))
        
        self.draw_color_box(self.palette_inner, base_hex, f"RGB{base}")

        scheme_labels = {
            'complementary': self.lang.get('complementary_label'),
            'analogous': self.lang.get('analogous_label'),
            'triadic': self.lang.get('triadic_label'),
            'monochromatic': self.lang.get('monochromatic'),
            'split_complementary': self.lang.get('split_complementary'),
            'square': self.lang.get('square'),
            'tetradic': self.lang.get('tetradic'),
            'double_complementary': self.lang.get('double_complementary')
        }

        for scheme in self.selected_schemes:
            if scheme.startswith('custom_'):
                self._display_custom_harmony(scheme, base_hex)
            elif scheme in palette:
                colors = palette[scheme]
                label = scheme_labels.get(scheme, scheme)
                
                scheme_header = ctk.CTkLabel(
                    self.palette_inner,
                    text=label,
                    font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
                    text_color=COLORS['text_primary']
                )
                scheme_header.pack(anchor='w', padx=5, pady=(15, 5))
                
                if isinstance(colors, (tuple, list)) and len(colors) == 3 and all(isinstance(c, int) for c in colors):
                    if isinstance(colors, list):
                        colors = tuple(colors)
                    hx = self.generator.rgb_to_hex(colors)
                    self.draw_color_box(self.palette_inner, hx, f"RGB{colors}")
                else:
                    for idx, col in enumerate(colors, 1):
                        if isinstance(col, list):
                            col = tuple(col)
                        hx = self.generator.rgb_to_hex(col)
                        self.draw_color_box(self.palette_inner, hx, f"{idx}. RGB{col}")
    
    def _display_custom_harmony(self, scheme, base_hex):
        """Display custom harmony colors"""
        try:
            from custom_harmony import CustomHarmonyManager
            manager = CustomHarmonyManager(self.file_handler)
            idx = int(scheme.split('_')[1])
            
            if idx < len(manager.harmonies):
                harmony = manager.harmonies[idx]
                colors = manager.apply_harmony(base_hex, idx)
                label = harmony.get('name', self.lang.get('custom_harmony_default_name'))
                
                scheme_header = ctk.CTkLabel(
                    self.palette_inner,
                    text=label,
                    font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
                    text_color=COLORS['text_primary']
                )
                scheme_header.pack(anchor='w', padx=5, pady=(15, 5))
                
                for color_idx, color_hex in enumerate(colors, 1):
                    rgb = self.generator.hex_to_rgb(color_hex)
                    self.draw_color_box(self.palette_inner, color_hex, f"{color_idx}. RGB{rgb}")
        except Exception:
            pass

    def display_multiple_palettes(self, palettes):
        """Display multiple palettes (for image mode)"""
        scheme_labels = {
            'complementary': self.lang.get('complementary'),
            'analogous': self.lang.get('analogous'),
            'triadic': self.lang.get('triadic'),
            'monochromatic': self.lang.get('monochromatic'),
            'split_complementary': self.lang.get('split_complementary'),
            'square': self.lang.get('square'),
            'tetradic': self.lang.get('tetradic'),
            'double_complementary': self.lang.get('double_complementary')
        }
        
        for i, p in enumerate(palettes, start=1):
            palette_header = ctk.CTkLabel(
                self.palette_inner,
                text=f"🎨 {self.lang.get('representative_color')} {i}",
                font=ctk.CTkFont(family=FONT_FAMILY, size=14, weight="bold"),
                text_color=COLORS['accent_light']
            )
            palette_header.pack(anchor='w', padx=5, pady=(15, 5))
            
            base = p['base']
            if isinstance(base, list):
                base = tuple(base)
            base_hex = self.generator.rgb_to_hex(base)
            self.draw_color_box(self.palette_inner, base_hex, f"{self.lang.get('base_color')} RGB{base}")

            for scheme in self.selected_schemes:
                if scheme.startswith('custom_'):
                    self._display_custom_harmony(scheme, base_hex)
                elif scheme in p:
                    colors = p[scheme]
                    label = scheme_labels.get(scheme, scheme)
                    
                    scheme_label = ctk.CTkLabel(
                        self.palette_inner,
                        text=f"  {label}",
                        font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"),
                        text_color=COLORS['text_secondary']
                    )
                    scheme_label.pack(anchor='w', padx=5)
                    
                    if isinstance(colors, (tuple, list)) and len(colors) == 3 and all(isinstance(c, int) for c in colors):
                        if isinstance(colors, list):
                            colors = tuple(colors)
                        hx = self.generator.rgb_to_hex(colors)
                        self.draw_color_box(self.palette_inner, hx, f"RGB{colors}")
                    else:
                        for idx, col in enumerate(colors, 1):
                            if isinstance(col, list):
                                col = tuple(col)
                            hx = self.generator.rgb_to_hex(col)
                            self.draw_color_box(self.palette_inner, hx, f"{idx}. RGB{col}")
            
            # Separator between palettes
            if i < len(palettes):
                sep = ctk.CTkFrame(self.palette_inner, height=2, fg_color=COLORS['border'])
                sep.pack(fill='x', pady=15, padx=10)

    def display_ai_palettes(self, palettes):
        """Display AI-generated color palettes"""
        if not palettes:
            empty_label = ctk.CTkLabel(
                self.palette_inner,
                text=self.lang.get('ai_no_palettes'),
                font=ctk.CTkFont(family=FONT_FAMILY, size=12),
                text_color=COLORS['text_muted']
            )
            empty_label.pack(pady=20)
            return
        
        for i, palette_data in enumerate(palettes, start=1):
            if isinstance(palette_data, dict):
                palette_name = palette_data.get('name', self.lang.get('ai_palette_name').format(i=i))
                palette_colors = palette_data.get('colors', [])
            else:
                palette_name = self.lang.get('ai_palette_name').format(i=i)
                palette_colors = palette_data
            
            header = ctk.CTkLabel(
                self.palette_inner,
                text=f"✨ {palette_name}",
                font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
                text_color=COLORS['accent_light']
            )
            header.pack(anchor='w', padx=5, pady=(15 if i > 1 else 5, 5))
            
            for j, color_hex in enumerate(palette_colors, start=1):
                rgb = self.generator.hex_to_rgb(color_hex)
                self.draw_color_box(self.palette_inner, color_hex, f"{j}. RGB{rgb}")
            
            if i < len(palettes):
                sep = ctk.CTkFrame(self.palette_inner, height=2, fg_color=COLORS['border'])
                sep.pack(fill='x', pady=15, padx=10)

    # ============== Saved Palettes Management ==============
    def add_saved_palette(self):
        """Add a new saved palette"""
        name = self.lang.get('new_palette_numbered').format(i=self._saved_counter + 1)
        self._saved_counter += 1

        entry = {'name': name, 'colors': []}
        self.saved_palettes.append(entry)
        self.render_saved_list()
        self.mark_modified()
        self.log_action(f"Added new palette: {name}")

    def remove_saved_palette(self):
        """Remove selected palette"""
        if len(self.saved_palettes) <= 1 or self._saved_selected is None:
            return
        
        idx = self._saved_selected
        palette_name = self.saved_palettes[idx]['name'] if idx < len(self.saved_palettes) else 'Unknown'
        
        try:
            del self.saved_palettes[idx]
        except Exception:
            return
        
        if not self.saved_palettes:
            self._saved_selected = None
        else:
            self._saved_selected = max(0, idx - 1)
        
        self.render_saved_list()
        self.log_action(f"Removed palette: {palette_name}")
        self.mark_modified()

    def on_palette_color_click(self, hex_color):
        """Handle clicks on palette swatches"""
        if self._saved_selected is None:
            messagebox.showinfo(self.lang.get('selection_required'), self.lang.get('select_palette_first'))
            return
        
        try:
            entry = self.saved_palettes[self._saved_selected]
            hex_str = hex_color if isinstance(hex_color, str) else self.generator.rgb_to_hex(hex_color)
            
            entry['colors'].append(hex_str)
            self.add_to_recent_colors(hex_str)
            
            self.render_saved_list()
            self.mark_modified()
            self.log_action(f"Added color {hex_str} to palette: {entry['name']}")
        except Exception as e:
            self.log_action(f"Error adding color to palette: {str(e)}")

    def render_saved_list(self):
        """Render saved palettes list with modern design"""
        for c in self.saved_list_container.winfo_children():
            try:
                c.destroy()
            except Exception:
                pass

        for idx, entry in enumerate(self.saved_palettes):
            is_selected = self._saved_selected == idx
            
            # Palette card
            palette_frame = ctk.CTkFrame(
                self.saved_list_container,
                corner_radius=8,
                fg_color=COLORS['accent'] if is_selected else COLORS['bg_secondary'],
                border_width=2 if is_selected else 1,
                border_color=COLORS['accent_light'] if is_selected else COLORS['border']
            )
            palette_frame.pack(fill='x', pady=4, padx=2)
            
            # Header with name
            header = ctk.CTkFrame(palette_frame, fg_color="transparent")
            header.pack(fill='x', padx=10, pady=(8, 5))
            
            name_label = ctk.CTkLabel(
                header,
                text=entry.get('name', self.lang.get('palette_numbered').format(i=idx+1)),
                font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"),
                text_color=COLORS['text_primary']
            )
            name_label.pack(side='left')
            
            # Color count badge
            color_count = len(entry.get('colors', []))
            count_label = ctk.CTkLabel(
                header,
                text=self.lang.get('colors_count').format(count=color_count),
                font=ctk.CTkFont(family=FONT_FAMILY, size=9),
                text_color=COLORS['text_muted']
            )
            count_label.pack(side='right')
            
            # Color bar with Canvas for variable width ratio
            colors = entry.get('colors', [])
            if colors:
                bar_container = ctk.CTkFrame(palette_frame, height=30, fg_color="transparent")
                bar_container.pack(fill='x', padx=10, pady=(0, 8))
                bar_container.pack_propagate(False)
                
                max_display = min(len(colors), 10)  # Show max 10 colors
                display_colors = colors[:max_display]
                
                # Use Canvas for precise width calculation
                canvas = tk.Canvas(
                    bar_container,
                    height=30,
                    bg=COLORS['bg_secondary'],
                    highlightthickness=0
                )
                canvas.pack(fill='both', expand=True)
                
                # Wait for canvas to render and get actual width
                def draw_palette_bar():
                    canvas.delete('all')
                    canvas.update_idletasks()  # Force geometry update
                    canvas_width = canvas.winfo_width()
                    if canvas_width <= 1:
                        canvas_width = 400  # Fallback width
                    
                    box_width = float(canvas_width) / float(len(display_colors))
                    for i, color in enumerate(display_colors):
                        x1 = int(i * box_width)
                        x2 = int((i + 1) * box_width)
                        canvas.create_rectangle(x1, 0, x2, 30, fill=color, outline='')
                
                canvas.after(50, draw_palette_bar)
                
                # Show indicator if more colors
                if len(colors) > max_display:
                    more_label = ctk.CTkLabel(
                        bar_container,
                        text=f"+{len(colors) - max_display}",
                        font=ctk.CTkFont(family=FONT_FAMILY, size=8),
                        text_color=COLORS['text_muted'],
                        width=25
                    )
                    more_label.place(relx=1.0, rely=0.5, anchor='e', x=-5)
            else:
                # Empty palette indicator
                empty_label = ctk.CTkLabel(
                    palette_frame,
                    text=self.lang.get('empty_palette_msg'),
                    font=ctk.CTkFont(family=FONT_FAMILY, size=9),
                    text_color=COLORS['text_muted']
                )
                empty_label.pack(pady=(0, 8))
            
            # Click binding - optimize selection
            def make_select(i):
                def select_handler(e=None):
                    if self._saved_selected != i:
                        self._saved_selected = i
                        self.render_saved_list()
                return select_handler
            
            for widget in [palette_frame, header, name_label]:
                widget.bind('<Button-1>', make_select(idx))
                try:
                    widget.configure(cursor='hand2')
                except Exception:
                    pass
            
            # Right-click context menu
            def make_context_menu(i):
                return lambda e: self.show_palette_context_menu(i, e)
            
            for widget in [palette_frame, header, name_label]:
                widget.bind('<Button-3>', make_context_menu(idx))
            
            # Double-click to edit
            def make_edit(i):
                return lambda e: self.open_palette_editor(i)
            
            for widget in [palette_frame, header, name_label]:
                widget.bind('<Double-Button-1>', make_edit(idx))

        self.update_menu_states()

    def _select_saved_entry(self, idx):
        """Select a saved palette entry"""
        self._saved_selected = idx
        self.render_saved_list()
        self.update_menu_states()

    def show_palette_context_menu(self, idx, event):
        """Show context menu for palette operations"""
        self._saved_selected = idx
        self.render_saved_list()
        
        entry = self.saved_palettes[idx]
        current_mode = entry.get('view_mode', 'rgb')
        view_label = self.lang.get('view_rgb') if current_mode == 'value' else self.lang.get('view_value')
        
        menu = tk.Menu(self, tearoff=0, bg=COLORS['bg_card'], fg=COLORS['text_primary'])
        menu.add_command(label=self.lang.get('context_rename'), command=lambda: self.rename_palette(idx))
        menu.add_command(label=self.lang.get('context_edit_palette'), command=lambda: self.open_palette_editor(idx))
        menu.add_command(label=self.lang.get('context_save_palette'), command=lambda: self.save_palette_file(idx))
        menu.add_separator()
        menu.add_command(label=self.lang.get('context_export_txt'), command=lambda: self.export_palette_txt(idx))
        menu.add_command(label=self.lang.get('context_export_png'), command=lambda: self.export_palette_png(idx))
        menu.add_separator()
        menu.add_command(label=view_label, command=lambda: self.toggle_palette_view(idx))
        
        try:
            menu.post(event.x_root, event.y_root)
        except Exception:
            pass

    def copy_palette(self):
        """Copy currently selected palette"""
        if self._saved_selected is None:
            messagebox.showinfo(self.lang.get('selection_required'), self.lang.get('select_palette_first'))
            return
        try:
            entry = self.saved_palettes[self._saved_selected]
            new_entry = {
                'name': f"{entry['name']}{self.lang.get('copy_suffix')}",
                'colors': entry['colors'].copy()
            }
            self.saved_palettes.append(new_entry)
            self._saved_selected = len(self.saved_palettes) - 1
            self.render_saved_list()
            self.mark_modified()
            self.log_action(f"Copied palette: {entry['name']}")
        except Exception as e:
            messagebox.showerror(self.lang.get('error'), str(e))

    def load_palette(self):
        """Load palette from .mps file"""
        try:
            metadata = self.file_handler.clean_palette_metadata()
            
            if not metadata:
                filename = filedialog.askopenfilename(
                    title=self.lang.get('dialog_open_mps'),
                    filetypes=[(self.lang.get('my_palette_file'), '*.mps'), (self.lang.get('all_files'), '*.*')]
                )
                if filename:
                    self._load_palette_from_file(filename)
            else:
                self._show_palette_selection_dialog(metadata)
                
        except Exception as e:
            messagebox.showerror(self.lang.get('load_error_title'), self.lang.get('msg_load_failed').format(error=str(e)))
            self.log_action(f"Load palette failed: {str(e)}")
    
    def _load_palette_from_file(self, filename):
        """Load palette from a specific file"""
        try:
            import json
            import base64
            with open(filename, 'r', encoding='utf-8') as f:
                encoded = f.read()
            data = json.loads(base64.b64decode(encoded.encode('utf-8')).decode('utf-8'))
            new_entry = {'name': data['name'], 'colors': data['colors']}
            self.saved_palettes.append(new_entry)
            self._saved_selected = len(self.saved_palettes) - 1
            self.render_saved_list()
            self.mark_modified()
            
            self.file_handler.add_palette_metadata(data['name'], data['colors'], filename)
            self.log_action(f"Loaded palette from MPS: {data['name']}")
        except Exception as e:
            raise e

    # ============== Menu Functions ==============
    def show_file_menu(self):
        """Show file operations menu"""
        menu = tk.Menu(self, tearoff=0, bg=COLORS['bg_card'], fg=COLORS['text_primary'])
        menu.add_command(label=self.lang.get('file_new'), command=self.new_pgf)
        menu.add_command(label=self.lang.get('file_save'), command=self.save_pgf)
        menu.add_command(label=self.lang.get('file_save_as'), command=self.save_pgf_as)
        menu.add_command(label=self.lang.get('file_open'), command=self.load_pgf)
        menu.add_separator()
        
        # Recent files submenu
        recent_menu = tk.Menu(menu, tearoff=0, bg=COLORS['bg_card'], fg=COLORS['text_primary'])
        recent_files = self.load_recent_files()
        if recent_files:
            for filepath in recent_files:
                filename = os.path.basename(filepath)
                recent_menu.add_command(label=filename, command=lambda p=filepath: self.load_recent_file(p))
        else:
            recent_menu.add_command(label=self.lang.get('no_recent_files'), state='disabled')
        
        menu.add_cascade(label=self.lang.get('open_recent'), menu=recent_menu)
        menu.add_separator()
        menu.add_command(label=self.lang.get('file_exit'), command=self.on_closing)
        
        try:
            x = self.file_menu_btn.winfo_rootx()
            y = self.file_menu_btn.winfo_rooty() + self.file_menu_btn.winfo_height()
            menu.post(x, y)
        except Exception:
            pass

    def show_tools_menu(self):
        """Show tools menu"""
        menu = tk.Menu(self, tearoff=0, bg=COLORS['bg_card'], fg=COLORS['text_primary'])
        menu.add_command(label=self.lang.get('apply_palette_to_image'), command=self.apply_palette_to_image)
        menu.add_separator()
        menu.add_command(label=self.lang.get('custom_color_harmonies'), command=self.open_custom_harmony)
        menu.add_separator()
        menu.add_command(label=self.lang.get('preset_palettes'), command=self.open_preset_palettes)
        menu.add_separator()
        menu.add_command(label=self.lang.get('settings_api'), command=self.open_ai_settings)
        
        try:
            x = self.tools_btn.winfo_rootx()
            y = self.tools_btn.winfo_rooty() + self.tools_btn.winfo_height()
            menu.post(x, y)
        except Exception:
            pass

    # ============== Harmony Selector ==============
    def open_harmony_selector(self):
        """Open harmony scheme selector dialog"""
        dialog = ctk.CTkToplevel(self)
        set_window_icon(dialog)
        dialog.title(self.lang.get('harmonies_title'))
        dialog.geometry("450x550")
        dialog.transient(self)
        dialog.grab_set()
        dialog.configure(fg_color=COLORS['bg_dark'])

        # Header
        ctk.CTkLabel(
            dialog,
            text=self.lang.get('select_harmonies'),
            font=ctk.CTkFont(family=FONT_FAMILY, size=14, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack(pady=15, padx=15, anchor='w')

        # Scrollable frame for checkboxes
        scroll_frame = ctk.CTkScrollableFrame(dialog, fg_color=COLORS['bg_secondary'])
        scroll_frame.pack(fill='both', expand=True, padx=15, pady=5)

        schemes = [
            ('complementary', self.lang.get('complementary_label')),
            ('analogous', self.lang.get('analogous_label')),
            ('triadic', self.lang.get('triadic_label')),
            ('monochromatic', self.lang.get('monochromatic')),
            ('split_complementary', self.lang.get('split_complementary')),
            ('square', self.lang.get('square')),
            ('tetradic', self.lang.get('tetradic')),
            ('double_complementary', self.lang.get('double_complementary')),
        ]

        scheme_vars = {}
        for scheme_key, scheme_label in schemes:
            var = ctk.BooleanVar(value=(scheme_key in self.selected_schemes))
            scheme_vars[scheme_key] = var
            cb = ctk.CTkCheckBox(
                scroll_frame,
                text=scheme_label,
                variable=var,
                fg_color=COLORS['accent'],
                hover_color=COLORS['accent_hover'],
                text_color=COLORS['text_primary']
            )
            cb.pack(anchor='w', pady=5, padx=10)
        
        # Custom harmonies
        try:
            from custom_harmony import CustomHarmonyManager
            manager = CustomHarmonyManager(self.file_handler)
            
            if manager.harmonies:
                sep = ctk.CTkFrame(scroll_frame, height=1, fg_color=COLORS['border'])
                sep.pack(fill='x', pady=10)
                
                ctk.CTkLabel(
                    scroll_frame,
                    text=self.lang.get('custom_harmonies'),
                    font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
                    text_color=COLORS['text_primary']
                ).pack(anchor='w', pady=5, padx=10)
                
                for i, harmony in enumerate(manager.harmonies):
                    harmony_name = harmony.get('name', self.lang.get('custom_harmony_numbered').format(i=i + 1))
                    scheme_key = f'custom_{i}'
                    var = ctk.BooleanVar(value=(scheme_key in self.selected_schemes))
                    scheme_vars[scheme_key] = var
                    cb = ctk.CTkCheckBox(
                        scroll_frame,
                        text=harmony_name,
                        variable=var,
                        fg_color=COLORS['accent'],
                        hover_color=COLORS['accent_hover'],
                        text_color=COLORS['text_primary']
                    )
                    cb.pack(anchor='w', pady=5, padx=10)
        except ImportError:
            pass

        # Buttons
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=15, fill='x', padx=15)

        def apply_selection():
            self.selected_schemes = [key for key, var in scheme_vars.items() if var.get()]
            if not self.selected_schemes:
                messagebox.showwarning(self.lang.get('warning'), self.lang.get('msg_select_harmony_required'))
                return
            dialog.destroy()
            self.generate()

        ModernButton(btn_frame, text=self.lang.get('ok'), command=apply_selection, width=100).pack(side='left', padx=5)
        ModernSecondaryButton(btn_frame, text=self.lang.get('cancel'), command=dialog.destroy, width=100).pack(side='left', padx=5)

    # ============== Settings ==============
    def open_settings(self):
        """Open settings dialog"""
        dialog = ctk.CTkToplevel(self)
        set_window_icon(dialog)
        dialog.title(self.lang.get('dialog_settings'))
        dialog.geometry("550x650")
        dialog.transient(self)
        dialog.grab_set()
        dialog.configure(fg_color=COLORS['bg_dark'])

        # Scrollable content
        scroll = ctk.CTkScrollableFrame(dialog, fg_color=COLORS['bg_secondary'])
        scroll.pack(fill='both', expand=True, padx=15, pady=15)

        # Language settings
        ctk.CTkLabel(
            scroll,
            text=self.lang.get('settings_language_section'),
            font=ctk.CTkFont(family=FONT_FAMILY, size=14, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack(anchor='w', pady=(10, 10))
        
        current_lang = self.config_manager.get('language', 'ko')
        lang_var = ctk.StringVar(value='���국�E�' if current_lang == 'ko' else 'English')
        
        lang_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        lang_frame.pack(fill='x', padx=10, pady=5)
        
        ctk.CTkLabel(lang_frame, text=self.lang.get('language_label'), text_color=COLORS['text_secondary']).pack(side='left')
        lang_combo = ctk.CTkComboBox(
            lang_frame,
            values=['���국�E�', 'English'],
            variable=lang_var,
            fg_color=COLORS['bg_card'],
            button_color=COLORS['accent'],
            button_hover_color=COLORS['accent_hover']
        )
        lang_combo.pack(side='left', padx=10)

        # Auto-save settings
        sep1 = ctk.CTkFrame(scroll, height=1, fg_color=COLORS['border'])
        sep1.pack(fill='x', pady=15)
        
        ctk.CTkLabel(
            scroll,
            text=self.lang.get('settings_autosave_section'),
            font=ctk.CTkFont(family=FONT_FAMILY, size=14, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack(anchor='w', pady=(0, 10))
        
        auto_save_var = ctk.BooleanVar(value=self.config_manager.get('auto_save_enabled', True))
        ctk.CTkCheckBox(
            scroll,
            text=self.lang.get('settings_autosave_enable'),
            variable=auto_save_var,
            fg_color=COLORS['accent'],
            hover_color=COLORS['accent_hover'],
            text_color=COLORS['text_primary']
        ).pack(anchor='w', padx=10)
        
        interval_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        interval_frame.pack(fill='x', padx=10, pady=10)
        
        ctk.CTkLabel(interval_frame, text=self.lang.get('settings_autosave_interval'), text_color=COLORS['text_secondary']).pack(side='left')
        interval_var = ctk.IntVar(value=self.config_manager.get('auto_save_interval', 300))
        interval_entry = ctk.CTkEntry(interval_frame, textvariable=interval_var, width=80, fg_color=COLORS['bg_card'])
        interval_entry.pack(side='left', padx=10)
        ctk.CTkLabel(interval_frame, text="sec", text_color=COLORS['text_muted']).pack(side='left')

        # UI settings
        sep2 = ctk.CTkFrame(scroll, height=1, fg_color=COLORS['border'])
        sep2.pack(fill='x', pady=15)
        
        ctk.CTkLabel(
            scroll,
            text=self.lang.get('settings_ui_section'),
            font=ctk.CTkFont(family=FONT_FAMILY, size=14, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack(anchor='w', pady=(0, 10))
        
        window_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        window_frame.pack(fill='x', padx=10, pady=5)
        
        ctk.CTkLabel(window_frame, text=self.lang.get('settings_window_size'), text_color=COLORS['text_secondary']).pack(side='left')
        width_var = ctk.IntVar(value=self.config_manager.get('window_width', 1100))
        height_var = ctk.IntVar(value=self.config_manager.get('window_height', 700))
        ctk.CTkEntry(window_frame, textvariable=width_var, width=70, fg_color=COLORS['bg_card']).pack(side='left', padx=5)
        ctk.CTkLabel(window_frame, text="x", text_color=COLORS['text_muted']).pack(side='left')
        ctk.CTkEntry(window_frame, textvariable=height_var, width=70, fg_color=COLORS['bg_card']).pack(side='left', padx=5)

        recent_colors_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        recent_colors_frame.pack(fill='x', padx=10, pady=10)
        
        ctk.CTkLabel(recent_colors_frame, text=self.lang.get('settings_recent_colors'), text_color=COLORS['text_secondary']).pack(side='left')
        max_recent_colors_var = ctk.IntVar(value=self.config_manager.get('max_recent_colors', 50))
        ctk.CTkEntry(recent_colors_frame, textvariable=max_recent_colors_var, width=70, fg_color=COLORS['bg_card']).pack(side='left', padx=10)

        # Button frame
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=15, padx=15, fill='x')

        def save_settings():
            new_lang = 'ko' if lang_var.get() == '���국�E�' else 'en'
            self.config_manager.set('language', new_lang)
            self.config_manager.set('auto_save_enabled', auto_save_var.get())
            self.config_manager.set('auto_save_interval', interval_var.get())
            self.config_manager.set('window_width', width_var.get())
            self.config_manager.set('window_height', height_var.get())
            self.config_manager.set('max_recent_colors', max(1, min(100, max_recent_colors_var.get())))
            
            if self.config_manager.save_config():
                messagebox.showinfo(self.lang.get('settings_saved_title'), self.lang.get('settings_saved'))
                self.log_action("Settings saved")
                
                self.auto_save_enabled = auto_save_var.get()
                self.auto_save_interval = interval_var.get() * 1000
                if self.auto_save_enabled:
                    self.stop_auto_save()
                    self.start_auto_save()
                else:
                    self.stop_auto_save()

                self.max_recent_colors = max(1, min(100, max_recent_colors_var.get()))
                if len(self.recent_colors) > self.max_recent_colors:
                    self.recent_colors = self.recent_colors[:self.max_recent_colors]
                    self.config_manager.set('recent_colors', self.recent_colors)
                    self.config_manager.save_config()
                self.update_recent_colors_display()
                
                dialog.destroy()
            else:
                messagebox.showerror(self.lang.get('settings_save_failed_title'), self.lang.get('settings_save_failed'))

        ModernButton(btn_frame, text=self.lang.get('button_save'), command=save_settings, width=100).pack(side='left', padx=5)
        ModernSecondaryButton(btn_frame, text=self.lang.get('button_cancel'), command=dialog.destroy, width=100).pack(side='left', padx=5)
        ModernSecondaryButton(btn_frame, text=self.lang.get('reset_to_defaults'), command=self.reset_settings, width=150).pack(side='right', padx=5)

    def reset_settings(self):
        """Reset settings to default"""
        response = messagebox.askyesno(self.lang.get('reset_settings_title'), self.lang.get('msg_reset_settings_confirm'))
        if response:
            self.config_manager.reset_to_defaults()
            messagebox.showinfo(self.lang.get('reset_done_title'), self.lang.get('msg_settings_reset_done'))
            self.log_action("Settings reset to defaults")

    # ============== File Operations ==============
    def new_pgf(self):
        """Create new workspace"""
        if self.is_modified:
            response = messagebox.askyesnocancel(self.lang.get('save_prompt_title'), self.lang.get('msg_save_changes_prompt'))
            if response is None:
                return
            elif response:
                saved = self.save_pgf()
                if not saved:
                    return
        
        self.saved_palettes = [{'name': self.lang.get('new_palette_numbered').format(i=1), 'colors': []}]
        self.selected_schemes = ['complementary', 'analogous', 'triadic', 'monochromatic']
        self.source_type.set('hex')
        self.hex_entry.set('#3498db')
        self.current_palettes = []
        self._saved_counter = 1
        self._saved_selected = 0
        self.current_file = None
        
        self._update_color_swatch('#3498db')
        self.on_source_change()
        self.render_saved_list()
        self.clear_palette_display()
        
        self.is_modified = False
        self.update_title()
        self.log_action("Created new workspace")

    def save_pgf(self):
        """Save workspace"""
        if self.current_file:
            return self._save_to_file(self.current_file)
        else:
            try:
                path = filedialog.asksaveasfilename(
                    title=self.lang.get('dialog_save_pgf'),
                    initialdir=os.getcwd(),
                    defaultextension='.pgf',
                    filetypes=[('PGF file', '*.pgf')]
                )
                if not path:
                    return False
                
                result = self._save_to_file(path)
                if result:
                    self.log_action(f"Saved new workspace: {path}")
                return result
            except Exception as e:
                messagebox.showerror(self.lang.get('save_error_title'), self.lang.get('msg_save_failed').format(error=str(e)))
                return False

    def save_pgf_as(self):
        """Save As"""
        try:
            if not self.current_file:
                return False
            
            path = filedialog.asksaveasfilename(
                title=self.lang.get('dialog_save_as'),
                initialdir=os.getcwd(),
                defaultextension='.pgf',
                filetypes=[('PGF file', '*.pgf')]
            )
            if not path:
                return False
            
            result = self._save_to_file(path)
            if result:
                self.log_action(f"Saved workspace as: {path}")
            return result
        except Exception as e:
            messagebox.showerror(self.lang.get('save_error_title'), self.lang.get('msg_save_failed').format(error=str(e)))
            return False

    def _save_to_file(self, path):
        """Save workspace to file"""
        try:
            import json
            
            if not path:
                raise ValueError(self.lang.get('msg_no_save_path'))
            
            directory = os.path.dirname(path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            
            workspace_data = {
                'saved_palettes': self.saved_palettes or [],
                'selected_schemes': self.selected_schemes or [],
                'source_type': self.source_type.get() if hasattr(self, 'source_type') else 'hex',
                'hex_entry': self.hex_entry.get() if hasattr(self, 'hex_entry') else '#3498db',
                'current_palettes': getattr(self, 'current_palettes', []),
                'saved_counter': self._saved_counter,
                'saved_selected': self._saved_selected,
                'version': '1.0'
            }
            
            data_json = json.dumps(workspace_data, ensure_ascii=False)
            encrypted = self._encrypt_aes(data_json)
            
            temp_path = path + '.tmp'
            try:
                with open(temp_path, 'wb') as f:
                    f.write(encrypted)
                
                if os.path.exists(path):
                    backup_path = path + '.bak'
                    if os.path.exists(backup_path):
                        os.remove(backup_path)
                    os.rename(path, backup_path)
                
                os.rename(temp_path, path)
                
                backup_path = path + '.bak'
                if os.path.exists(backup_path):
                    try:
                        os.remove(backup_path)
                    except Exception:
                        pass
                        
            except Exception as write_error:
                if os.path.exists(temp_path):
                    try:
                        os.remove(temp_path)
                    except Exception:
                        pass
                raise write_error
            
            self.current_file = path
            self.is_modified = False
            self.update_title()
            
            self.add_recent_file(path)
            messagebox.showinfo(self.lang.get('saved_title'), self.lang.get('msg_workspace_saved').format(path=path))
            return True
            
        except Exception as e:
            messagebox.showerror(self.lang.get('save_error_title'), self.lang.get('msg_save_failed').format(error=str(e)))
            return False

    def load_pgf(self):
        """Load workspace"""
        try:
            path = filedialog.askopenfilename(
                title=self.lang.get('dialog_open_pgf'),
                initialdir=os.getcwd(),
                filetypes=[('PGF file', '*.pgf')]
            )
            if not path:
                return
            
            self._load_pgf_from_path(path)
        except Exception as e:
            messagebox.showerror(self.lang.get('load_error_title'), self.lang.get('msg_load_failed').format(error=str(e)))
    
    def _load_pgf_from_path(self, path):
        """Load workspace from specific path"""
        import json
        import base64
        
        with open(path, 'rb') as f:
            file_data = f.read()
        
        try:
            data_json = self._decrypt_aes(file_data)
            workspace_data = json.loads(data_json)
        except Exception:
            try:
                data_json = base64.b64decode(file_data).decode('utf-8')
                workspace_data = json.loads(data_json)
            except Exception as e2:
                raise Exception(f"Failed to decrypt file: {str(e2)}")
        
        self.saved_palettes = workspace_data.get('saved_palettes', [])
        self.selected_schemes = workspace_data.get('selected_schemes', ['complementary', 'analogous', 'triadic', 'monochromatic'])
        self.source_type.set(workspace_data.get('source_type', 'hex'))
        self.hex_entry.set(workspace_data.get('hex_entry', '#3498db'))
        self.current_palettes = workspace_data.get('current_palettes', [])
        self._saved_counter = workspace_data.get('saved_counter', 0)
        self._saved_selected = workspace_data.get('saved_selected', None)
        
        self._update_color_swatch(self.hex_entry.get())
        self.on_source_change()
        self.render_saved_list()
        
        if self.current_palettes:
            self.clear_palette_display()
            source_type = self.source_type.get()
            if source_type == 'hex' and self.current_palettes:
                self.display_single_palette(self.current_palettes[0])
            elif source_type == 'image' and self.current_palettes:
                self.display_multiple_palettes(self.current_palettes)
        
        self.current_file = path
        self.is_modified = False
        self.update_title()
        
        self.add_recent_file(path)
        messagebox.showinfo(self.lang.get('loaded_title'), self.lang.get('msg_workspace_loaded').format(path=path))
        self.log_action(f"Loaded workspace: {path}")

    # ============== Encryption ==============
    def _get_encryption_key(self):
        """Generate encryption key"""
        passphrase = "ColorPaletteGenerator2025SecretKey"
        key = hashlib.sha256(passphrase.encode()).digest()
        import base64
        return base64.urlsafe_b64encode(key)
    
    def _encrypt_aes(self, data):
        """Encrypt data"""
        key = self._get_encryption_key()
        f = Fernet(key)
        return f.encrypt(data.encode('utf-8'))
    
    def _decrypt_aes(self, encrypted_data):
        """Decrypt data"""
        key = self._get_encryption_key()
        f = Fernet(key)
        return f.decrypt(encrypted_data).decode('utf-8')

    # ============== Recent Files ==============
    def get_temp_dir(self):
        """Get temp directory"""
        import sys
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(__file__)
        
        temp_dir = os.path.join(base_dir, 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        return temp_dir
    
    def get_recent_files_path(self):
        """Get recent files path"""
        return os.path.join(self.get_temp_dir(), 'recent.dat')
    
    def load_recent_files(self):
        """Load recent files"""
        try:
            import json
            
            path = self.get_recent_files_path()
            if not os.path.exists(path):
                return []
            
            with open(path, 'rb') as f:
                encrypted = f.read()
            
            data = self._decrypt_aes(encrypted)
            recent_files = json.loads(data)
            
            return [f for f in recent_files if os.path.exists(f)]
        except Exception:
            return []
    
    def save_recent_files(self, recent_files):
        """Save recent files"""
        try:
            import json
            
            data = json.dumps(recent_files)
            encrypted = self._encrypt_aes(data)
            
            path = self.get_recent_files_path()
            with open(path, 'wb') as f:
                f.write(encrypted)
        except Exception:
            pass
    
    def add_recent_file(self, filepath):
        """Add to recent files"""
        recent_files = self.load_recent_files()
        
        if filepath in recent_files:
            recent_files.remove(filepath)
        
        recent_files.insert(0, filepath)
        recent_files = recent_files[:10]
        
        self.save_recent_files(recent_files)
    
    def load_recent_file(self, filepath):
        """Load recent file"""
        if not os.path.exists(filepath):
            messagebox.showerror(self.lang.get('error'), self.lang.get('msg_file_not_found_path').format(path=filepath))
            return
        
        try:
            self._load_pgf_from_path(filepath)
        except Exception as e:
            messagebox.showerror(self.lang.get('load_error_title'), self.lang.get('msg_load_failed').format(error=str(e)))

    # ============== Utility Functions ==============
    def update_title(self):
        """Update window title"""
        base_title = self.lang.get('title')
        if self.current_file:
            filename = os.path.basename(self.current_file)
            title = f"{base_title} - {filename}"
        else:
            title = f"{base_title} - {self.lang.get('untitled')}"
        
        if self.is_modified:
            title += " *"
        
        self.title(title)
        self.update_menu_states()
    
    def update_menu_states(self):
        """Update button states"""
        try:
            if hasattr(self, 'btn_delete'):
                if len(self.saved_palettes) <= 1 or self._saved_selected is None:
                    self.btn_delete.configure(state='disabled')
                else:
                    self.btn_delete.configure(state='normal')
        except Exception:
            pass

    def mark_modified(self):
        """Mark workspace as modified"""
        if not self.is_modified:
            self.is_modified = True
            self.update_title()

    def _cleanup_stale_tooltips(self, event=None):
        """Remove all stale tooltips"""
        if hasattr(self, 'active_tooltips'):
            for tooltip in self.active_tooltips[:]:
                try:
                    if tooltip and tooltip.winfo_exists():
                        tooltip.destroy()
                except Exception:
                    pass
            self.active_tooltips.clear()

    def create_tooltip(self, widget, text):
        """Create tooltip with delayed show and proper after_cancel - main.py style"""
        tooltip_window = [None]
        show_after_id = [None]
        
        def destroy_tooltip():
            if tooltip_window[0] is not None:
                try:
                    if tooltip_window[0] in self.active_tooltips:
                        self.active_tooltips.remove(tooltip_window[0])
                    tooltip_window[0].destroy()
                except Exception:
                    pass
                tooltip_window[0] = None
        
        def show_tooltip(x_root, y_root):
            destroy_tooltip()
            tip = ctk.CTkToplevel(self)
            tip.wm_overrideredirect(True)
            try:
                tip.wm_attributes('-topmost', True)
            except Exception:
                pass
            tip.wm_geometry(f"+{x_root + 10}+{y_root + 10}")
            tip.configure(fg_color=COLORS['bg_card'])
            
            label = ctk.CTkLabel(
                tip,
                text=text,
                font=ctk.CTkFont(family=FONT_FAMILY, size=10),
                text_color=COLORS['text_primary']
            )
            label.pack(padx=8, pady=4)
            tooltip_window[0] = tip
            self.active_tooltips.append(tip)
        
        def on_enter(e):
            if show_after_id[0] is not None:
                try:
                    widget.after_cancel(show_after_id[0])
                except Exception:
                    pass
                show_after_id[0] = None
            
            show_after_id[0] = widget.after(120, lambda: show_tooltip(e.x_root, e.y_root))
        
        def on_leave(e):
            if show_after_id[0] is not None:
                try:
                    widget.after_cancel(show_after_id[0])
                except Exception:
                    pass
                show_after_id[0] = None
            destroy_tooltip()
        
        def on_motion(e):
            if tooltip_window[0] is not None:
                try:
                    tooltip_window[0].wm_geometry(f"+{e.x_root + 10}+{e.y_root + 10}")
                except Exception:
                    pass
        
        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)
        widget.bind('<Motion>', on_motion)

    def setup_logging(self):
        """Setup logging"""
        import sys
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(__file__)
        
        temp_dir = os.path.join(base_dir, 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        log_file = os.path.join(temp_dir, 'app.log')
        
        logger = logging.getLogger()
        logger.handlers.clear()
        logger.setLevel(logging.INFO)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        
        self.logger = logger
        self.logger.info("="*50)
        self.logger.info("Logging system initialized")
    
    def _init_preset_palettes_async(self):
        """Initialize preset palettes in background"""
        try:
            preset_file = os.path.join('data', 'preset_palettes.dat')
            if os.path.exists(preset_file):
                return
            
            logging.info("Preset palettes not found. Generating in background...")
            
            import threading
            
            def generate_presets():
                try:
                    from preset_generator import PresetPaletteGenerator
                    generator = PresetPaletteGenerator()
                    palettes = generator.generate_all_palettes(count=1200)
                    generator.save_palettes(self.file_handler, 'preset_palettes.dat')
                    logging.info(f"Successfully generated {len(palettes)} preset palettes")
                except Exception as e:
                    logging.error(f"Failed to generate preset palettes: {e}")
            
            thread = threading.Thread(target=generate_presets, daemon=True)
            thread.start()
            
        except Exception as e:
            logging.error(f"Error initializing preset palettes: {e}")
    
    def log_action(self, action):
        """Log an action"""
        try:
            if hasattr(self, 'logger'):
                self.logger.info(action)
        except Exception:
            pass
    
    def bind_shortcuts(self):
        """Setup keyboard shortcuts"""
        self.bind('<Control-s>', lambda e: self.save_pgf())
        self.bind('<Control-Shift-S>', lambda e: self.save_pgf_as())
        self.bind('<Control-n>', lambda e: self.new_pgf())
        self.bind('<Control-o>', lambda e: self.load_pgf())
        self.bind('<Delete>', lambda e: self.remove_saved_palette())
        self.bind('<F5>', lambda e: self.generate())
        self.log_action("Keyboard shortcuts enabled")
    
    def setup_drag_drop(self):
        """Setup drag and drop"""
        try:
            def on_drop(event):
                files = self.tk.splitlist(event.data)
                if files:
                    file_path = files[0]
                    if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp')):
                        self.image_path = file_path
                        self.source_type.set('image')
                        self.on_source_change()
                        self.log_action(f"Image dropped: {os.path.basename(file_path)}")
                    elif file_path.lower().endswith('.pgf'):
                        self._load_pgf_from_path(file_path)
            
            self.drop_target_register('DND_Files')
            self.dnd_bind('<<Drop>>', on_drop)
        except Exception:
            pass
    
    def start_auto_save(self):
        """Start auto-save timer"""
        if self.auto_save_enabled and self.is_modified and self.current_file:
            try:
                self._save_to_file(self.current_file)
                self.log_action("Auto-saved workspace")
            except Exception as e:
                self.log_action(f"Auto-save failed: {str(e)}")
        
        if self.auto_save_enabled:
            self.auto_save_timer = self.after(self.auto_save_interval, self.start_auto_save)
    
    def stop_auto_save(self):
        """Stop auto-save timer"""
        if self.auto_save_timer:
            self.after_cancel(self.auto_save_timer)
            self.auto_save_timer = None
    
    def on_closing(self):
        """Handle window close"""
        self.stop_auto_save()
        
        if self.is_modified:
            response = messagebox.askyesnocancel(
                self.lang.get('save_prompt_title'),
                self.lang.get('msg_save_changes_prompt'),
            )
            if response is None:
                return
            elif response:
                saved = self.save_pgf()
                if not saved:
                    return
        
        self.log_action("Application closed")
        self.destroy()

    # ============== Stub methods for features to be implemented ==============
    def rename_palette(self, idx):
        """Rename palette"""
        try:
            entry = self.saved_palettes[idx]
            old_name = entry['name']
            
            dialog = ctk.CTkInputDialog(
                text=f"{self.lang.get('new_name')}:",
                title=self.lang.get('rename')
            )
            new_name = dialog.get_input()
            
            if new_name:
                self.saved_palettes[idx]['name'] = new_name
                self.render_saved_list()
                self.mark_modified()
                self.log_action(f"Renamed palette: {old_name} -> {new_name}")
        except Exception as e:
            messagebox.showerror(self.lang.get('error'), str(e))

    def open_palette_editor(self, idx):
        """Open palette editor dialog with full functionality"""
        if idx is None or idx >= len(self.saved_palettes):
            return
        
        entry = self.saved_palettes[idx]
        
        dialog = ctk.CTkToplevel(self)
        set_window_icon(dialog)
        dialog.title(self.lang.get('palette_editor_title').format(name=entry['name']))
        dialog.geometry("600x500")
        dialog.transient(self)
        dialog.grab_set()
        dialog.configure(fg_color=COLORS['bg_dark'])
        
        # Header
        header_frame = ctk.CTkFrame(dialog, fg_color=COLORS['bg_secondary'], height=50)
        header_frame.pack(fill='x', padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            header_frame,
            text=f"🎨 {entry['name']}",
            font=ctk.CTkFont(family=FONT_FAMILY, size=16, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack(side='left', padx=15, pady=10)
        
        color_count_label = ctk.CTkLabel(
            header_frame,
            text=self.lang.get('colors_count').format(count=len(entry['colors'])),
            font=ctk.CTkFont(family=FONT_FAMILY, size=11),
            text_color=COLORS['text_secondary']
        )
        color_count_label.pack(side='right', padx=15, pady=10)
        
        # Toolbar
        toolbar = ctk.CTkFrame(dialog, fg_color="transparent")
        toolbar.pack(fill='x', padx=15, pady=10)
        
        # Local copy of colors for editing
        edit_colors = entry['colors'].copy()
        selected_color_idx = [None]
        
        # Color list frame (create before refresh_color_list)
        color_list_frame = ctk.CTkScrollableFrame(dialog, fg_color=COLORS['bg_card'])
        color_list_frame.pack(fill='both', expand=True, padx=15, pady=10)
        
        def refresh_color_list():
            for widget in color_list_frame.winfo_children():
                widget.destroy()
            
            color_count_label.configure(text=self.lang.get('colors_count').format(count=len(edit_colors)))
            
            for i, color in enumerate(edit_colors):
                is_selected = selected_color_idx[0] == i
                
                color_row = ctk.CTkFrame(
                    color_list_frame,
                    fg_color=COLORS['accent'] if is_selected else COLORS['bg_secondary'],
                    corner_radius=6,
                    height=45
                )
                color_row.pack(fill='x', pady=2)
                color_row.pack_propagate(False)
                
                # Color swatch
                swatch = ctk.CTkFrame(
                    color_row,
                    width=40,
                    height=35,
                    corner_radius=4,
                    fg_color=color
                )
                swatch.pack(side='left', padx=10, pady=5)
                swatch.pack_propagate(False)
                
                # Color info
                info_frame = ctk.CTkFrame(color_row, fg_color="transparent")
                info_frame.pack(side='left', fill='both', expand=True, padx=10)
                
                hex_lbl = ctk.CTkLabel(
                    info_frame,
                    text=color.upper(),
                    font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
                    text_color=COLORS['text_primary']
                )
                hex_lbl.pack(anchor='w')
                
                try:
                    rgb = self.generator.hex_to_rgb(color)
                    rgb_lbl = ctk.CTkLabel(
                        info_frame,
                        text=f"RGB({rgb[0]}, {rgb[1]}, {rgb[2]})",
                        font=ctk.CTkFont(family=FONT_FAMILY, size=10),
                        text_color=COLORS['text_secondary']
                    )
                    rgb_lbl.pack(anchor='w')
                except Exception:
                    pass
                
                # Select on click
                def make_select(color_idx):
                    def handler(e=None):
                        selected_color_idx[0] = color_idx
                        refresh_color_list()
                    return handler
                
                for w in [color_row, swatch, info_frame, hex_lbl]:
                    w.bind('<Button-1>', make_select(i))
                    try:
                        w.configure(cursor='hand2')
                    except Exception:
                        pass
        
        # Add color button
        def add_color():
            color_result = colorchooser.askcolor(title=self.lang.get('add_color_title'))
            if color_result[1]:
                edit_colors.append(color_result[1])
                refresh_color_list()
        
        ModernButton(toolbar, text=f"➕ {self.lang.get('add_color')}", command=add_color, width=100).pack(side='left', padx=2)
        
        # Edit color button
        def edit_selected_color():
            if selected_color_idx[0] is None:
                messagebox.showinfo(self.lang.get('selection_required'), self.lang.get('select_color_first'))
                return
            current_color = edit_colors[selected_color_idx[0]]
            color_result = colorchooser.askcolor(color=current_color, title=self.lang.get('edit_color_title'))
            if color_result[1]:
                edit_colors[selected_color_idx[0]] = color_result[1]
                refresh_color_list()
        
        ModernSecondaryButton(toolbar, text=f"✏️ {self.lang.get('edit')}", command=edit_selected_color, width=80).pack(side='left', padx=2)
        
        # Delete color button
        def delete_selected_color():
            if selected_color_idx[0] is None:
                messagebox.showinfo(self.lang.get('selection_required'), self.lang.get('select_color_first'))
                return
            del edit_colors[selected_color_idx[0]]
            selected_color_idx[0] = None
            refresh_color_list()
        
        ModernSecondaryButton(toolbar, text=f"🗑️ {self.lang.get('delete')}", command=delete_selected_color, width=80).pack(side='left', padx=2)
        
        # Move buttons
        def move_up():
            if selected_color_idx[0] is None or selected_color_idx[0] == 0:
                return
            i = selected_color_idx[0]
            edit_colors[i], edit_colors[i-1] = edit_colors[i-1], edit_colors[i]
            selected_color_idx[0] = i - 1
            refresh_color_list()
        
        def move_down():
            if selected_color_idx[0] is None or selected_color_idx[0] >= len(edit_colors) - 1:
                return
            i = selected_color_idx[0]
            edit_colors[i], edit_colors[i+1] = edit_colors[i+1], edit_colors[i]
            selected_color_idx[0] = i + 1
            refresh_color_list()
        
        ModernIconButton(toolbar, text="\u2b06\ufe0f", command=move_up, width=36).pack(side='left', padx=2)
        ModernIconButton(toolbar, text="\u2b07\ufe0f", command=move_down, width=36).pack(side='left', padx=2)
        
        # Sort buttons
        sort_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        sort_frame.pack(side='right')
        
        def sort_by_hue():
            def get_hue(hex_color):
                rgb = self.generator.hex_to_rgb(hex_color)
                h, s, v = colorsys.rgb_to_hsv(rgb[0]/255, rgb[1]/255, rgb[2]/255)
                return h
            edit_colors.sort(key=get_hue)
            refresh_color_list()
        
        def sort_by_saturation():
            def get_saturation(hex_color):
                rgb = self.generator.hex_to_rgb(hex_color)
                h, s, v = colorsys.rgb_to_hsv(rgb[0]/255, rgb[1]/255, rgb[2]/255)
                return s
            edit_colors.sort(key=get_saturation, reverse=True)
            refresh_color_list()
        
        def sort_by_value():
            def get_value(hex_color):
                rgb = self.generator.hex_to_rgb(hex_color)
                return 0.299*rgb[0] + 0.587*rgb[1] + 0.114*rgb[2]
            edit_colors.sort(key=get_value)
            refresh_color_list()
        
        ModernSecondaryButton(sort_frame, text=self.lang.get('sort_by_hue'), command=sort_by_hue, width=70).pack(side='left', padx=2)
        ModernSecondaryButton(sort_frame, text=self.lang.get('sort_by_saturation'), command=sort_by_saturation, width=70).pack(side='left', padx=2)
        ModernSecondaryButton(sort_frame, text=self.lang.get('sort_by_luminance'), command=sort_by_value, width=70).pack(side='left', padx=2)
        
        refresh_color_list()
        
        # Bottom buttons
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(fill='x', padx=15, pady=15)
        
        def save_changes():
            entry['colors'] = edit_colors.copy()
            self.render_saved_list()
            self.mark_modified()
            self.log_action(f"Updated palette: {entry['name']}")
            dialog.destroy()
        
        ModernButton(btn_frame, text=self.lang.get('button_save'), command=save_changes, width=100).pack(side='left', padx=5)
        ModernSecondaryButton(btn_frame, text=self.lang.get('button_cancel'), command=dialog.destroy, width=100).pack(side='left', padx=5)

    def save_palette_file(self, idx):
        """Save palette file"""
        try:
            entry = self.saved_palettes[idx]
            filename = filedialog.asksaveasfilename(
                defaultextension='.mps',
                filetypes=[(self.lang.get('my_palette_file'), '*.mps'), (self.lang.get('all_files'), '*.*')],
                initialfile=entry['name']
            )
            if filename:
                import json
                import base64
                data = json.dumps({'name': entry['name'], 'colors': entry['colors']})
                encoded = base64.b64encode(data.encode('utf-8')).decode('utf-8')
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(encoded)
                
                self.file_handler.add_palette_metadata(entry['name'], entry['colors'], filename)
                self.log_action(f"Saved palette to MPS: {entry['name']}")
        except Exception as e:
            messagebox.showerror(self.lang.get('save_error_title'), self.lang.get('msg_save_failed').format(error=str(e)))

    def toggle_palette_view(self, idx):
        """Toggle palette view mode"""
        try:
            entry = self.saved_palettes[idx]
            current_mode = entry.get('view_mode', 'rgb')
            entry['view_mode'] = 'value' if current_mode == 'rgb' else 'rgb'
            self.render_saved_list()
        except Exception as e:
            messagebox.showerror(self.lang.get('error'), str(e))

    def export_palette_txt(self, idx):
        """Export palette to TXT"""
        try:
            entry = self.saved_palettes[idx]
            colors = entry.get('colors', [])
            if not colors:
                messagebox.showinfo(self.lang.get('export_title'), self.lang.get('msg_palette_has_no_colors'))
                return
            
            filename = filedialog.asksaveasfilename(
                defaultextension='.txt',
                filetypes=[(self.lang.get('text_file'), '*.txt'), (self.lang.get('all_files'), '*.*')],
                initialfile=f"{entry['name']}.txt"
            )
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"Palette: {entry['name']}\n")
                    f.write(f"Colors: {len(colors)}\n\n")
                    for i, color in enumerate(colors, 1):
                        f.write(f"{i}. {color}\n")
                messagebox.showinfo(self.lang.get('saved_title'), f"Exported to {filename}")
        except Exception as e:
            messagebox.showerror(self.lang.get('error'), str(e))

    def export_palette_png(self, idx):
        """Export palette to PNG"""
        try:
            entry = self.saved_palettes[idx]
            colors = entry.get('colors', [])
            if not colors:
                messagebox.showinfo(self.lang.get('export_title'), self.lang.get('msg_palette_has_no_colors'))
                return
            
            filename = filedialog.asksaveasfilename(
                defaultextension='.png',
                filetypes=[(self.lang.get('png_image'), '*.png'), (self.lang.get('all_files'), '*.*')],
                initialfile=f"{entry['name']}.png"
            )
            if filename:
                color_width = 100
                img_width = color_width * len(colors)
                img_height = 100
                
                img = Image.new('RGB', (img_width, img_height))
                draw = ImageDraw.Draw(img)
                
                for i, color in enumerate(colors):
                    x0 = i * color_width
                    x1 = x0 + color_width
                    draw.rectangle([x0, 0, x1, img_height], fill=color)
                
                img.save(filename)
                messagebox.showinfo(self.lang.get('saved_title'), f"Exported to {filename}")
        except Exception as e:
            messagebox.showerror(self.lang.get('error'), str(e))

    def open_color_adjuster(self):
        """Open color adjuster dialog for the selected palette"""
        if self._saved_selected is None:
            messagebox.showinfo(self.lang.get('selection_required'), self.lang.get('select_palette_to_adjust'))
            return
        
        if not COLOR_ADJUSTER_AVAILABLE:
            messagebox.showwarning(self.lang.get('warning'), self.lang.get('msg_color_adjust_unavailable'))
            return
        
        entry = self.saved_palettes[self._saved_selected]
        colors = entry.get('colors', [])
        
        if not colors:
            messagebox.showinfo(self.lang.get('info'), self.lang.get('msg_palette_has_no_colors'))
            return
        
        dialog = ctk.CTkToplevel(self)
        set_window_icon(dialog)
        dialog.title(self.lang.get('color_adjuster_title'))
        dialog.geometry("500x400")
        dialog.transient(self)
        dialog.grab_set()
        dialog.configure(fg_color=COLORS['bg_dark'])
        
        # Header
        ctk.CTkLabel(
            dialog,
            text=f"🎨 {self.lang.get('color_adjuster_title')} - {entry['name']}",
            font=ctk.CTkFont(family=FONT_FAMILY, size=14, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack(pady=15, padx=15, anchor='w')
        
        # Preview frame
        preview_frame = ctk.CTkFrame(dialog, fg_color=COLORS['bg_card'], height=60)
        preview_frame.pack(fill='x', padx=15, pady=10)
        preview_frame.pack_propagate(False)
        
        preview_colors = colors.copy()
        
        def update_preview():
            for widget in preview_frame.winfo_children():
                widget.destroy()
            for color in preview_colors:
                swatch = ctk.CTkFrame(
                    preview_frame,
                    fg_color=color,
                    corner_radius=4
                )
                swatch.pack(side='left', fill='both', expand=True, padx=2, pady=5)
        
        update_preview()
        
        # Contrast slider
        contrast_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        contrast_frame.pack(fill='x', padx=15, pady=10)
        
        ctk.CTkLabel(
            contrast_frame,
            text=self.lang.get('contrast'),
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            text_color=COLORS['text_primary']
        ).pack(anchor='w')
        
        contrast_var = ctk.DoubleVar(value=0)
        contrast_slider = ctk.CTkSlider(
            contrast_frame,
            from_=-1.0,
            to=1.0,
            variable=contrast_var,
            fg_color=COLORS['bg_secondary'],
            progress_color=COLORS['accent'],
            button_color=COLORS['accent_light']
        )
        contrast_slider.pack(fill='x', pady=5)
        
        contrast_value_label = ctk.CTkLabel(
            contrast_frame,
            text="0%",
            font=ctk.CTkFont(family=FONT_FAMILY, size=10),
            text_color=COLORS['text_secondary']
        )
        contrast_value_label.pack(anchor='e')
        
        # Warmth slider
        warmth_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        warmth_frame.pack(fill='x', padx=15, pady=10)
        
        ctk.CTkLabel(
            warmth_frame,
            text=f"{self.lang.get('warmth')} {self.lang.get('warmth_hint')}",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            text_color=COLORS['text_primary']
        ).pack(anchor='w')
        
        warmth_var = ctk.DoubleVar(value=0)
        warmth_slider = ctk.CTkSlider(
            warmth_frame,
            from_=-1.0,
            to=1.0,
            variable=warmth_var,
            fg_color=COLORS['bg_secondary'],
            progress_color=COLORS['accent'],
            button_color=COLORS['accent_light']
        )
        warmth_slider.pack(fill='x', pady=5)
        
        warmth_value_label = ctk.CTkLabel(
            warmth_frame,
            text="0%",
            font=ctk.CTkFont(family=FONT_FAMILY, size=10),
            text_color=COLORS['text_secondary']
        )
        warmth_value_label.pack(anchor='e')
        
        def on_slider_change(*args):
            nonlocal preview_colors
            contrast = contrast_var.get()
            warmth = warmth_var.get()
            
            contrast_value_label.configure(text=f"{int(contrast * 100)}%")
            warmth_value_label.configure(text=f"{int(warmth * 100)}%")
            
            adjusted = []
            for color in colors:
                try:
                    rgb = self.generator.hex_to_rgb(color)
                    if apply_contrast and contrast != 0:
                        rgb = apply_contrast(rgb, contrast)
                    if apply_warmth and warmth != 0:
                        rgb = apply_warmth(rgb, warmth)
                    adjusted.append(self.generator.rgb_to_hex(rgb))
                except Exception:
                    adjusted.append(color)
            
            preview_colors = adjusted
            update_preview()
        
        contrast_var.trace_add('write', on_slider_change)
        warmth_var.trace_add('write', on_slider_change)
        
        # Buttons
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(fill='x', padx=15, pady=20)
        
        def apply_changes():
            entry['colors'] = preview_colors.copy()
            self.render_saved_list()
            self.mark_modified()
            self.log_action(f"Applied color adjustments to: {entry['name']}")
            dialog.destroy()
        
        def reset_sliders():
            contrast_var.set(0)
            warmth_var.set(0)
        
        ModernButton(btn_frame, text=self.lang.get('apply'), command=apply_changes, width=100).pack(side='left', padx=5)
        ModernSecondaryButton(btn_frame, text=self.lang.get('reset'), command=reset_sliders, width=100).pack(side='left', padx=5)
        ModernSecondaryButton(btn_frame, text=self.lang.get('button_cancel'), command=dialog.destroy, width=100).pack(side='left', padx=5)

    def apply_palette_to_image(self):
        """Apply palette to image - opens the Image Recolorer dialog"""
        if not self.saved_palettes or all(len(p.get('colors', [])) == 0 for p in self.saved_palettes):
            messagebox.showinfo(self.lang.get('info'), self.lang.get('msg_no_valid_colors'))
            return
        
        dialog = ctk.CTkToplevel(self)
        set_window_icon(dialog)
        dialog.title(self.lang.get('dialog_apply_palette'))
        dialog.geometry("900x650")
        dialog.transient(self)
        dialog.grab_set()
        dialog.configure(fg_color=COLORS['bg_dark'])
        
        # State
        current_image_path = [None]
        current_preview = [None]
        recolorer = ImageRecolorer()
        
        # Left panel - Controls
        left_panel = ctk.CTkFrame(dialog, fg_color=COLORS['bg_secondary'], width=280)
        left_panel.pack(side='left', fill='y', padx=0, pady=0)
        left_panel.pack_propagate(False)
        
        # Palette selection
        ctk.CTkLabel(
            left_panel,
            text=self.lang.get('recolor_select_palette'),
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack(anchor='w', padx=15, pady=(15, 5))
        
        # Palette list
        palette_names = [p['name'] for p in self.saved_palettes if p.get('colors')]
        if not palette_names:
            palette_names = ['No palettes available']
        
        selected_palette_var = ctk.StringVar(value=palette_names[0] if palette_names else '')
        palette_combo = ctk.CTkComboBox(
            left_panel,
            values=palette_names,
            variable=selected_palette_var,
            fg_color=COLORS['bg_card'],
            button_color=COLORS['accent'],
            button_hover_color=COLORS['accent_hover'],
            width=250
        )
        palette_combo.pack(padx=15, pady=5)
        
        # Palette preview
        palette_preview_frame = ctk.CTkFrame(left_panel, fg_color=COLORS['bg_card'], height=40)
        palette_preview_frame.pack(fill='x', padx=15, pady=10)
        palette_preview_frame.pack_propagate(False)
        
        def update_palette_preview(*args):
            for widget in palette_preview_frame.winfo_children():
                widget.destroy()
            
            name = selected_palette_var.get()
            for p in self.saved_palettes:
                if p['name'] == name:
                    colors = p.get('colors', [])[:10]
                    if colors:
                        # Use Canvas for precise width calculation
                        canvas = tk.Canvas(
                            palette_preview_frame,
                            height=40,
                            bg=COLORS['bg_card'],
                            highlightthickness=0
                        )
                        canvas.pack(fill='both', expand=True)
                        
                        def draw_preview():
                            canvas.delete('all')
                            canvas.update_idletasks()
                            canvas_width = canvas.winfo_width()
                            if canvas_width <= 1:
                                canvas_width = 400
                            
                            box_width = float(canvas_width) / float(len(colors))
                            for i, color in enumerate(colors):
                                x1 = int(i * box_width)
                                x2 = int((i + 1) * box_width)
                                canvas.create_rectangle(x1, 0, x2, 40, fill=color, outline='')
                        
                        canvas.after(50, draw_preview)
                    break
        
        selected_palette_var.trace_add('write', update_palette_preview)
        update_palette_preview()
        
        # Separator
        ctk.CTkFrame(left_panel, height=1, fg_color=COLORS['border']).pack(fill='x', padx=15, pady=15)
        
        # Load image button
        def load_image():
            path = filedialog.askopenfilename(
                title=self.lang.get('dialog_select_image_recolor'),
                filetypes=[
                    (self.lang.get('image_files'), "*.png;*.jpg;*.jpeg;*.bmp;*.gif"),
                    (self.lang.get('all_files'), "*.*"),
                ]
            )
            if path:
                current_image_path[0] = path
                try:
                    img = Image.open(path)
                    # Resize for preview
                    max_size = (500, 400)
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)
                    photo = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
                    image_label.configure(image=photo, text="")
                    image_label.image = photo
                    
                    # Show filename
                    file_label.configure(text=os.path.basename(path))
                except Exception as e:
                    messagebox.showerror(self.lang.get('error'), self.lang.get('msg_recolor_load_image_failed').format(error=str(e)))
        
        ModernButton(
            left_panel,
            text=f"📷 {self.lang.get('recolor_load_image')}",
            command=load_image,
            width=250
        ).pack(padx=15, pady=5)
        
        file_label = ctk.CTkLabel(
            left_panel,
            text=self.lang.get('no_file_selected'),
            font=ctk.CTkFont(family=FONT_FAMILY, size=10),
            text_color=COLORS['text_muted']
        )
        file_label.pack(anchor='w', padx=15)
        
        # Apply button
        def apply_recolor():
            if not current_image_path[0]:
                messagebox.showinfo(self.lang.get('info'), self.lang.get('msg_select_image_first'))
                return
            
            name = selected_palette_var.get()
            colors = []
            for p in self.saved_palettes:
                if p['name'] == name:
                    colors = p.get('colors', [])
                    break
            
            if not colors:
                messagebox.showinfo(self.lang.get('info'), self.lang.get('msg_palette_has_no_colors'))
                return
            
            try:
                result_img = recolorer.apply_palette_to_image(current_image_path[0], colors)
                current_preview[0] = result_img
                
                # Show preview
                preview = result_img.copy()
                max_size = (500, 400)
                preview.thumbnail(max_size, Image.Resampling.LANCZOS)
                photo = ctk.CTkImage(light_image=preview, dark_image=preview, size=preview.size)
                image_label.configure(image=photo, text="")
                image_label.image = photo
                
                self.log_action(f"Applied palette to image: {os.path.basename(current_image_path[0])}")
            except Exception as e:
                messagebox.showerror(self.lang.get('error'), self.lang.get('msg_recolor_preview_failed').format(error=str(e)))
        
        ModernButton(
            left_panel,
            text=f"🎨 {self.lang.get('apply')}",
            command=apply_recolor,
            width=250
        ).pack(padx=15, pady=15)
        
        # Save button
        def save_result():
            if not current_preview[0]:
                messagebox.showinfo(self.lang.get('info'), self.lang.get('msg_no_preview'))
                return
            
            save_path = filedialog.asksaveasfilename(
                title=self.lang.get('dialog_save_recolored'),
                defaultextension='.png',
                filetypes=[(self.lang.get('png_image'), '*.png'), (self.lang.get('all_files'), '*.*')]
            )
            if save_path:
                try:
                    current_preview[0].save(save_path)
                    messagebox.showinfo(self.lang.get('saved_title'), self.lang.get('msg_recolor_save_success').format(path=save_path))
                except Exception as e:
                    messagebox.showerror(self.lang.get('error'), self.lang.get('msg_recolor_save_failed').format(error=str(e)))
        
        ModernSecondaryButton(
            left_panel,
            text=f"💾 {self.lang.get('save_btn')}",
            command=save_result,
            width=250
        ).pack(padx=15, pady=5)
        
        # Close button
        ModernSecondaryButton(
            left_panel,
            text=self.lang.get('close_btn'),
            command=dialog.destroy,
            width=250
        ).pack(padx=15, pady=5)
        
        # Right panel - Image preview
        right_panel = ctk.CTkFrame(dialog, fg_color=COLORS['bg_card'])
        right_panel.pack(side='right', fill='both', expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(
            right_panel,
            text=self.lang.get('recolor_preview'),
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack(anchor='w', padx=15, pady=10)
        
        image_label = ctk.CTkLabel(
            right_panel,
            text=self.lang.get('no_image_label'),
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            text_color=COLORS['text_muted']
        )
        image_label.pack(expand=True, padx=20, pady=20)

    def open_custom_harmony(self):
        """Open custom harmony editor"""
        try:
            from custom_harmony import CustomHarmonyManager
            import colorsys
            from tkinter import colorchooser
            
            # Get current base color
            current_color = self.hex_entry.get() or '#FF0000'
            manager = CustomHarmonyManager(self.file_handler)
            
            dialog = ctk.CTkToplevel(self)
            set_window_icon(dialog)
            dialog.title(self.lang.get('dialog_custom_harmony'))
            dialog.geometry("1000x700")
            dialog.transient(self)
            dialog.grab_set()
            dialog.configure(fg_color=COLORS['bg_dark'])
            
            # State variables
            current_harmony_idx = [None]
            colors_list = []
            
            # Main layout
            main_content = ctk.CTkFrame(dialog, fg_color="transparent")
            main_content.pack(fill='both', expand=True, padx=15, pady=15)
            main_content.grid_columnconfigure(0, weight=1)
            main_content.grid_columnconfigure(1, weight=2)
            main_content.grid_rowconfigure(0, weight=1)
            
            # Left panel - Harmony list
            left_panel = ctk.CTkFrame(main_content, fg_color=COLORS['bg_card'], corner_radius=10)
            left_panel.grid(row=0, column=0, sticky='nsew', padx=(0, 10))
            
            ctk.CTkLabel(
                left_panel,
                text=self.lang.get('saved_harmonies'),
                font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
                text_color=COLORS['text_primary']
            ).pack(anchor='w', padx=15, pady=(15, 10))
            
            # Harmony listbox
            harmony_frame = ctk.CTkScrollableFrame(left_panel, fg_color=COLORS['bg_secondary'], height=400)
            harmony_frame.pack(fill='both', expand=True, padx=10, pady=5)
            
            harmony_buttons = []
            selected_harmony = [None]
            
            def load_harmony_list():
                for btn in harmony_buttons:
                    btn.destroy()
                harmony_buttons.clear()
                
                for i, harmony in enumerate(manager.harmonies):
                    def make_select(idx):
                        return lambda: on_harmony_select(idx)
                    
                    btn = ctk.CTkButton(
                        harmony_frame,
                        text=harmony.get('name', self.lang.get('unnamed')),
                        command=make_select(i),
                        fg_color=COLORS['bg_hover'],
                        hover_color=COLORS['accent'],
                        anchor='w',
                        height=32
                    )
                    btn.pack(fill='x', pady=2)
                    harmony_buttons.append(btn)
            
            def on_harmony_select(idx):
                selected_harmony[0] = idx
                current_harmony_idx[0] = idx
                harmony = manager.harmonies[idx]
                
                name_var.set(harmony.get('name', ''))
                colors_list.clear()
                colors_list.extend(harmony.get('colors', []))
                update_colors_display()
                update_preview()
                
                # Highlight selected
                for i, btn in enumerate(harmony_buttons):
                    if i == idx:
                        btn.configure(fg_color=COLORS['accent'])
                    else:
                        btn.configure(fg_color=COLORS['bg_hover'])
            
            # Harmony list buttons
            btn_toolbar = ctk.CTkFrame(left_panel, fg_color="transparent")
            btn_toolbar.pack(fill='x', padx=10, pady=10)
            
            def new_harmony():
                current_harmony_idx[0] = None
                name_var.set(self.lang.get('new_harmony'))
                colors_list.clear()
                update_colors_display()
                update_preview()
                for btn in harmony_buttons:
                    btn.configure(fg_color=COLORS['bg_hover'])
            
            def delete_harmony():
                if selected_harmony[0] is None:
                    messagebox.showwarning(self.lang.get('warning'), self.lang.get('custom_harmony_select_delete'))
                    return
                
                if messagebox.askyesno(self.lang.get('confirm'), self.lang.get('custom_harmony_confirm_delete')):
                    manager.delete_harmony(selected_harmony[0])
                    load_harmony_list()
                    new_harmony()
            
            ModernButton(btn_toolbar, text=self.lang.get('new_harmony'), command=new_harmony, height=32).pack(side='left', padx=2, expand=True, fill='x')
            ModernSecondaryButton(btn_toolbar, text=self.lang.get('delete_harmony'), command=delete_harmony, height=32).pack(side='left', padx=2, expand=True, fill='x')
            
            # Right panel - Editor
            right_panel = ctk.CTkFrame(main_content, fg_color=COLORS['bg_card'], corner_radius=10)
            right_panel.grid(row=0, column=1, sticky='nsew')
            
            # Name entry
            name_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
            name_frame.pack(fill='x', padx=15, pady=(15, 10))
            
            ctk.CTkLabel(
                name_frame,
                text=self.lang.get('harmony_name'),
                font=ctk.CTkFont(family=FONT_FAMILY, size=12),
                text_color=COLORS['text_secondary']
            ).pack(side='left')
            
            name_var = ctk.StringVar(value="")
            ctk.CTkEntry(
                name_frame,
                textvariable=name_var,
                width=300,
                fg_color=COLORS['bg_secondary'],
                border_width=0
            ).pack(side='left', padx=10)
            
            # Colors section
            colors_section = ctk.CTkFrame(right_panel, fg_color=COLORS['bg_secondary'], corner_radius=8)
            colors_section.pack(fill='both', expand=True, padx=15, pady=10)
            
            ctk.CTkLabel(
                colors_section,
                text=self.lang.get('colors'),
                font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
                text_color=COLORS['text_primary']
            ).pack(anchor='w', padx=10, pady=(10, 5))
            
            # Colors listbox
            colors_frame = ctk.CTkScrollableFrame(colors_section, fg_color=COLORS['bg_card'], height=200)
            colors_frame.pack(fill='both', expand=True, padx=10, pady=5)
            
            colors_labels = []
            
            def update_colors_display():
                for lbl in colors_labels:
                    lbl.destroy()
                colors_labels.clear()
                
                for i, color_data in enumerate(colors_list):
                    if color_data.get('type') == 'hsv':
                        h = color_data.get('h_offset', 0)
                        s = color_data.get('s_offset', 0)
                        v = color_data.get('v_offset', 0)
                        text = self.lang.get('custom_harmony_hsv_item').format(i=i + 1, h=h, s=s, v=v)
                    else:
                        hex_color = color_data.get('color', '#FFFFFF')
                        text = self.lang.get('custom_harmony_fixed_item').format(i=i + 1, hex=hex_color)
                    
                    lbl = ctk.CTkLabel(
                        colors_frame,
                        text=text,
                        font=ctk.CTkFont(family=FONT_FAMILY, size=11),
                        text_color=COLORS['text_primary'],
                        anchor='w'
                    )
                    lbl.pack(fill='x', pady=2)
                    colors_labels.append(lbl)
            
            # Color control buttons
            colors_btn_frame = ctk.CTkFrame(colors_section, fg_color="transparent")
            colors_btn_frame.pack(fill='x', padx=10, pady=10)
            
            def add_hsv_color():
                open_hsv_dialog(None, None)
            
            def add_fixed_color():
                color = colorchooser.askcolor(title=self.lang.get('add_fixed_color'))
                if color and color[1]:
                    colors_list.append({'type': 'fixed', 'color': color[1]})
                    update_colors_display()
                    update_preview()
            
            def open_hsv_dialog(edit_index, existing_data):
                is_edit = edit_index is not None
                hsv_dlg = ctk.CTkToplevel(dialog)
                set_window_icon(hsv_dlg)
                hsv_dlg.title(self.lang.get('edit') if is_edit else self.lang.get('add_hsv_color'))
                hsv_dlg.geometry('550x500')
                hsv_dlg.transient(dialog)
                hsv_dlg.grab_set()
                hsv_dlg.configure(fg_color=COLORS['bg_dark'])
                
                main = ctk.CTkFrame(hsv_dlg, fg_color=COLORS['bg_card'])
                main.pack(fill='both', expand=True, padx=20, pady=20)
                
                h_val = (existing_data or {}).get('h_offset', 0)
                s_val = (existing_data or {}).get('s_offset', 0)
                v_val = (existing_data or {}).get('v_offset', 0)
                
                h_var = ctk.DoubleVar(value=h_val)
                s_var = ctk.DoubleVar(value=s_val)
                v_var = ctk.DoubleVar(value=v_val)
                
                # Create sliders
                def create_slider(parent, label_text, var, min_val, max_val, unit):
                    frame = ctk.CTkFrame(parent, fg_color="transparent")
                    frame.pack(fill='x', pady=10)
                    
                    label_row = ctk.CTkFrame(frame, fg_color="transparent")
                    label_row.pack(fill='x', pady=(0, 5))
                    
                    ctk.CTkLabel(
                        label_row,
                        text=label_text,
                        font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
                        text_color=COLORS['text_primary']
                    ).pack(side='left')
                    
                    value_label = ctk.CTkLabel(
                        label_row,
                        text="",
                        font=ctk.CTkFont(family=FONT_FAMILY, size=11),
                        text_color=COLORS['text_secondary']
                    )
                    value_label.pack(side='right')
                    
                    slider = ctk.CTkSlider(
                        frame,
                        from_=min_val,
                        to=max_val,
                        variable=var,
                        button_color=COLORS['accent'],
                        button_hover_color=COLORS['accent_hover'],
                        progress_color=COLORS['accent']
                    )
                    slider.pack(fill='x')
                    
                    def update_label(*args):
                        if unit == '°':
                            value_label.configure(text=f"{var.get():.0f}{unit}")
                        else:
                            value_label.configure(text=f"{var.get():+.0f}{unit}")
                    
                    var.trace('w', update_label)
                    update_label()
                
                create_slider(main, self.lang.get('hue'), h_var, -180, 180, '°')
                create_slider(main, self.lang.get('saturation'), s_var, -100, 100, '%')
                create_slider(main, self.lang.get('value'), v_var, -100, 100, '%')
                
                # Preview
                ctk.CTkLabel(
                    main,
                    text=self.lang.get('preview'),
                    font=ctk.CTkFont(family=FONT_FAMILY, size=11),
                    text_color=COLORS['text_secondary']
                ).pack(anchor='w', pady=(15, 5))
                
                preview_container = ctk.CTkFrame(main, height=60, fg_color=COLORS['bg_secondary'])
                preview_container.pack(fill='x', pady=(0, 15))
                preview_container.pack_propagate(False)
                
                preview = tk.Canvas(preview_container, height=60, bg=COLORS['bg_secondary'], highlightthickness=0)
                preview.pack(fill='both', expand=True)
                
                def update_hsv_preview(*args):
                    try:
                        base_rgb = self.generator.hex_to_rgb(current_color)
                        base_h, base_s, base_v = colorsys.rgb_to_hsv(base_rgb[0] / 255, base_rgb[1] / 255, base_rgb[2] / 255)
                        
                        new_h = (base_h + h_var.get() / 360) % 1.0
                        new_s = max(0, min(1, base_s + s_var.get() / 100))
                        new_v = max(0, min(1, base_v + v_var.get() / 100))
                        
                        rgb = colorsys.hsv_to_rgb(new_h, new_s, new_v)
                        hex_color = self.generator.rgb_to_hex(tuple(int(c * 255) for c in rgb))
                        
                        preview.delete('all')
                        preview.update_idletasks()
                        canvas_width = preview.winfo_width() or 450
                        preview.create_rectangle(0, 0, canvas_width, 60, fill=hex_color, outline='')
                    except Exception:
                        pass
                
                for var in (h_var, s_var, v_var):
                    var.trace('w', update_hsv_preview)
                preview.after(50, update_hsv_preview)
                
                # Buttons
                btns = ctk.CTkFrame(main, fg_color="transparent")
                btns.pack(pady=(10, 0))
                
                def confirm():
                    color_data = {'type': 'hsv', 'h_offset': h_var.get(), 's_offset': s_var.get(), 'v_offset': v_var.get()}
                    if is_edit:
                        colors_list[edit_index] = color_data
                    else:
                        colors_list.append(color_data)
                    update_colors_display()
                    update_preview()
                    hsv_dlg.destroy()
                
                ModernButton(btns, text=self.lang.get('ok'), command=confirm, width=100).pack(side='left', padx=5)
                ModernSecondaryButton(btns, text=self.lang.get('button_cancel'), command=hsv_dlg.destroy, width=100).pack(side='left', padx=5)
            
            ModernSecondaryButton(colors_btn_frame, text=self.lang.get('add_hsv_color'), command=add_hsv_color, height=28).pack(side='left', padx=2)
            ModernSecondaryButton(colors_btn_frame, text=self.lang.get('add_fixed_color'), command=add_fixed_color, height=28).pack(side='left', padx=2)
            
            # Preview section
            preview_section = ctk.CTkFrame(right_panel, fg_color=COLORS['bg_secondary'], corner_radius=8, height=100)
            preview_section.pack(fill='x', padx=15, pady=(0, 10))
            preview_section.pack_propagate(False)
            
            ctk.CTkLabel(
                preview_section,
                text=self.lang.get('preview'),
                font=ctk.CTkFont(family=FONT_FAMILY, size=11),
                text_color=COLORS['text_secondary']
            ).pack(anchor='w', padx=10, pady=(10, 5))
            
            preview_canvas_frame = ctk.CTkFrame(preview_section, fg_color=COLORS['bg_card'])
            preview_canvas_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
            
            preview_canvas = tk.Canvas(preview_canvas_frame, height=60, bg=COLORS['bg_card'], highlightthickness=0)
            preview_canvas.pack(fill='both', expand=True)
            
            def update_preview():
                preview_canvas.delete('all')
                if not colors_list:
                    return
                
                try:
                    temp_harmony = {'name': 'Preview', 'colors': colors_list}
                    temp_manager = CustomHarmonyManager(self.file_handler)
                    temp_manager.harmonies = [temp_harmony]
                    colors = temp_manager.apply_harmony(current_color, 0)
                    
                    if not colors:
                        return
                    
                    preview_canvas.update_idletasks()
                    canvas_width = preview_canvas.winfo_width() or 600
                    box_width = float(canvas_width) / float(len(colors))
                    for i, color in enumerate(colors):
                        x1 = int(i * box_width)
                        x2 = int((i + 1) * box_width)
                        preview_canvas.create_rectangle(x1, 0, x2, 60, fill=color, outline='')
                except Exception:
                    pass
            
            # Bottom buttons
            bottom_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
            bottom_frame.pack(fill='x', padx=15, pady=(0, 15))
            
            def save_current_harmony():
                name = name_var.get().strip()
                if not name:
                    messagebox.showwarning(self.lang.get('warning'), self.lang.get('custom_harmony_name_required'))
                    return
                if not colors_list:
                    messagebox.showwarning(self.lang.get('warning'), self.lang.get('custom_harmony_color_required'))
                    return
                
                harmony_data = {'name': name, 'colors': colors_list.copy()}
                if current_harmony_idx[0] is not None:
                    manager.update_harmony(current_harmony_idx[0], harmony_data)
                else:
                    manager.add_harmony(harmony_data)
                
                load_harmony_list()
                messagebox.showinfo(self.lang.get('done'), self.lang.get('custom_harmony_saved'))
            
            ModernButton(bottom_frame, text=self.lang.get('button_save'), command=save_current_harmony, width=120).pack(side='left', padx=5)
            ModernSecondaryButton(bottom_frame, text=self.lang.get('button_close'), command=dialog.destroy, width=120).pack(side='right', padx=5)
            
            # Initialize
            load_harmony_list()
            
        except ImportError:
            messagebox.showerror(self.lang.get('error'), self.lang.get('custom_harmony_module_missing'))
        except Exception as e:
            messagebox.showerror(self.lang.get('error'), self.lang.get('custom_harmony_open_failed').format(error=str(e)))

    def open_ai_settings(self):
        """Open AI settings dialog"""
        try:
            from ai_color_recommender import AISettings
            
            dialog = ctk.CTkToplevel(self)
            set_window_icon(dialog)
            dialog.title(self.lang.get('dialog_ai_settings'))
            dialog.geometry("500x400")
            dialog.transient(self)
            dialog.grab_set()
            dialog.configure(fg_color=COLORS['bg_dark'])
            
            settings = AISettings.load_settings(self.file_handler)
            
            # Header
            ctk.CTkLabel(
                dialog,
                text=f"� {self.lang.get('settings_api')}",
                font=ctk.CTkFont(family=FONT_FAMILY, size=16, weight="bold"),
                text_color=COLORS['text_primary']
            ).pack(anchor='w', padx=15, pady=15)
            
            # Content
            content = ctk.CTkFrame(dialog, fg_color=COLORS['bg_card'])
            content.pack(fill='both', expand=True, padx=15, pady=5)
            
            # API Key
            ctk.CTkLabel(
                content,
                text=self.lang.get('ai_api_key_label'),
                font=ctk.CTkFont(family=FONT_FAMILY, size=12),
                text_color=COLORS['text_primary']
            ).pack(anchor='w', padx=15, pady=(15, 5))
            
            api_key_var = ctk.StringVar(value=settings.get('api_key', ''))
            api_key_entry = ctk.CTkEntry(
                content,
                textvariable=api_key_var,
                width=400,
                fg_color=COLORS['bg_secondary'],
                show='*'
            )
            api_key_entry.pack(padx=15, pady=5)
            
            # Help text
            ctk.CTkLabel(
                content,
                text=self.lang.get('ai_api_help'),
                font=ctk.CTkFont(family=FONT_FAMILY, size=10),
                text_color=COLORS['text_muted'],
                wraplength=400
            ).pack(anchor='w', padx=15, pady=5)
            
            # Number of colors per palette
            ctk.CTkLabel(
                content,
                text=self.lang.get('ai_colors_per_palette'),
                font=ctk.CTkFont(family=FONT_FAMILY, size=12),
                text_color=COLORS['text_primary']
            ).pack(anchor='w', padx=15, pady=(15, 5))
            
            num_colors_var = ctk.IntVar(value=settings.get('num_colors', 5))
            num_colors_slider = ctk.CTkSlider(
                content,
                from_=3,
                to=10,
                number_of_steps=7,
                variable=num_colors_var,
                fg_color=COLORS['bg_secondary'],
                progress_color=COLORS['accent']
            )
            num_colors_slider.pack(fill='x', padx=15, pady=5)
            
            num_colors_label = ctk.CTkLabel(
                content,
                text=str(num_colors_var.get()),
                font=ctk.CTkFont(family=FONT_FAMILY, size=11),
                text_color=COLORS['text_secondary']
            )
            num_colors_label.pack(anchor='e', padx=15)
            
            def update_label(*args):
                num_colors_label.configure(text=str(int(num_colors_var.get())))
            num_colors_var.trace_add('write', update_label)
            
            # Keywords
            ctk.CTkLabel(
                content,
                text=self.lang.get('ai_keywords_label'),
                font=ctk.CTkFont(family=FONT_FAMILY, size=12),
                text_color=COLORS['text_primary']
            ).pack(anchor='w', padx=15, pady=(15, 5))
            
            keywords_var = ctk.StringVar(value=settings.get('keywords', ''))
            keywords_entry = ctk.CTkEntry(
                content,
                textvariable=keywords_var,
                width=400,
                fg_color=COLORS['bg_secondary'],
                placeholder_text=self.lang.get('ai_keywords_example')
            )
            keywords_entry.pack(padx=15, pady=5)
            
            # Test button
            def test_api():
                api_key = api_key_var.get()
                if not api_key:
                    messagebox.showwarning(self.lang.get('warning'), self.lang.get('ai_recommender_api_key_not_set'))
                    return
                
                try:
                    from ai_color_recommender import AIColorRecommender
                    recommender = AIColorRecommender(api_key, lang=self.lang)
                    result = recommender.test_api_key()
                    if result:
                        messagebox.showinfo(self.lang.get('success'), self.lang.get('ai_api_test_success'))
                    else:
                        messagebox.showerror(self.lang.get('error'), self.lang.get('ai_api_invalid_key'))
                except Exception as e:
                    messagebox.showerror(self.lang.get('error'), self.lang.get('ai_api_test_failed').format(error=str(e)))
            
            ModernSecondaryButton(content, text=self.lang.get('ai_test_api'), command=test_api, width=150).pack(anchor='w', padx=15, pady=15)
            
            # Buttons
            btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
            btn_frame.pack(fill='x', padx=15, pady=15)
            
            def save_settings():
                new_settings = {
                    'api_key': api_key_var.get(),
                    'num_colors': int(num_colors_var.get()),
                    'keywords': keywords_var.get()
                }
                AISettings.save_settings(self.file_handler, new_settings)
                self.ai_recommender = None  # Reset recommender
                self.log_action("AI settings saved")
                dialog.destroy()
            
            ModernButton(btn_frame, text=self.lang.get('button_save'), command=save_settings, width=100).pack(side='left', padx=5)
            ModernSecondaryButton(btn_frame, text=self.lang.get('button_cancel'), command=dialog.destroy, width=100).pack(side='left', padx=5)
            
        except ImportError:
            messagebox.showerror(self.lang.get('error'), self.lang.get('ai_module_missing'))
        except Exception as e:
            messagebox.showerror(self.lang.get('error'), self.lang.get('ai_settings_open_failed').format(error=str(e)))

    def open_preset_palettes(self):
        """Open preset palettes browser"""
        try:
            from preset_generator import PresetPaletteGenerator
            
            dialog = ctk.CTkToplevel(self)
            set_window_icon(dialog)
            dialog.title(self.lang.get('dialog_preset_palettes'))
            dialog.geometry("800x600")
            dialog.transient(self)
            dialog.grab_set()
            dialog.configure(fg_color=COLORS['bg_dark'])
            
            # Load preset palettes using FileHandler
            presets = []
            try:
                presets = PresetPaletteGenerator.load_palettes(self.file_handler, 'preset_palettes.dat')
            except Exception:
                presets = []
            
            # If no presets found, try generating
            if not presets:
                try:
                    generator = PresetPaletteGenerator()
                    presets = generator.generate_all_palettes(count=100)
                    generator.save_palettes(self.file_handler, 'preset_palettes.dat')
                except Exception:
                    presets = []
            
            # Header
            header = ctk.CTkFrame(dialog, fg_color=COLORS['bg_secondary'], height=60)
            header.pack(fill='x')
            header.pack_propagate(False)
            
            ctk.CTkLabel(
                header,
                text=f"🎨 {self.lang.get('preset_palettes')}",
                font=ctk.CTkFont(family=FONT_FAMILY, size=16, weight="bold"),
                text_color=COLORS['text_primary']
            ).pack(side='left', padx=15, pady=15)
            
            # Filter section
            filter_frame = ctk.CTkFrame(dialog, fg_color="transparent")
            filter_frame.pack(fill='x', padx=15, pady=10)
            
            ctk.CTkLabel(
                filter_frame,
                text=self.lang.get('preset_filter'),
                font=ctk.CTkFont(family=FONT_FAMILY, size=12),
                text_color=COLORS['text_primary']
            ).pack(side='left')
            
            # Get unique tags
            all_tags = set()
            for p in presets:
                tags = p.get('tags', [])
                if isinstance(tags, list):
                    all_tags.update(tags)
            
            tag_list = [self.lang.get('preset_all')] + sorted(list(all_tags))
            
            filter_var = ctk.StringVar(value=self.lang.get('preset_all'))
            filter_combo = ctk.CTkComboBox(
                filter_frame,
                values=tag_list,
                variable=filter_var,
                fg_color=COLORS['bg_card'],
                button_color=COLORS['accent'],
                width=150
            )
            filter_combo.pack(side='left', padx=10)
            
            # Count label
            count_label = ctk.CTkLabel(
                filter_frame,
                text=self.lang.get('preset_count').format(current=len(presets), total=len(presets)),
                font=ctk.CTkFont(family=FONT_FAMILY, size=11),
                text_color=COLORS['text_secondary']
            )
            count_label.pack(side='right')
            
            # Palette grid
            palette_scroll = ctk.CTkScrollableFrame(dialog, fg_color=COLORS['bg_card'])
            palette_scroll.pack(fill='both', expand=True, padx=15, pady=10)
            
            displayed_palettes = []
            
            def display_palettes(filter_tag=None):
                nonlocal displayed_palettes
                
                for widget in palette_scroll.winfo_children():
                    widget.destroy()
                
                if filter_tag and filter_tag != self.lang.get('preset_all'):
                    displayed_palettes = [p for p in presets if filter_tag in p.get('tags', [])]
                else:
                    displayed_palettes = presets
                
                count_label.configure(
                    text=self.lang.get('preset_count').format(current=len(displayed_palettes), total=len(presets))
                )
                
                for i, preset in enumerate(displayed_palettes[:100]):  # Limit display for performance
                    palette_card = ctk.CTkFrame(
                        palette_scroll,
                        fg_color=COLORS['bg_secondary'],
                        corner_radius=8
                    )
                    palette_card.pack(fill='x', pady=4, padx=5)
                    
                    # Name and tags
                    info_frame = ctk.CTkFrame(palette_card, fg_color="transparent")
                    info_frame.pack(fill='x', padx=10, pady=(8, 5))
                    
                    name = preset.get('name', f'Preset {i+1}')
                    ctk.CTkLabel(
                        info_frame,
                        text=name,
                        font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"),
                        text_color=COLORS['text_primary']
                    ).pack(side='left')
                    
                    tags = preset.get('tags', [])
                    if tags:
                        ctk.CTkLabel(
                            info_frame,
                            text=self.lang.get('preset_tags_format').format(tags=', '.join(tags[:3])),
                            font=ctk.CTkFont(family=FONT_FAMILY, size=9),
                            text_color=COLORS['text_muted']
                        ).pack(side='right')
                    
                    # Color bar with Canvas for variable width ratio
                    colors = preset.get('colors', [])
                    if colors:
                        bar_container = ctk.CTkFrame(palette_card, height=30, fg_color="transparent")
                        bar_container.pack(fill='x', padx=10, pady=(0, 5))
                        bar_container.pack_propagate(False)
                        
                        display_colors = colors[:10]
                        
                        # Use Canvas for precise width calculation
                        canvas = tk.Canvas(
                            bar_container,
                            height=30,
                            bg=COLORS['bg_secondary'],
                            highlightthickness=0
                        )
                        canvas.pack(fill='both', expand=True)
                        
                        # Draw palette bar with variable width ratio
                        def draw_preset_bar(c=canvas, cols=display_colors):
                            c.delete('all')
                            c.update_idletasks()
                            canvas_width = c.winfo_width()
                            if canvas_width <= 1:
                                canvas_width = 700
                            
                            box_width = float(canvas_width) / float(len(cols))
                            for idx, color in enumerate(cols):
                                x1 = int(idx * box_width)
                                x2 = int((idx + 1) * box_width)
                                c.create_rectangle(x1, 0, x2, 30, fill=color, outline='')
                        
                        canvas.after(50, lambda: draw_preset_bar(canvas, display_colors))
                    
                    # Use button
                    def make_use(p):
                        def use_preset():
                            colors = p.get('colors', [])
                            name = p.get('name', 'Preset')
                            if colors:
                                new_entry = {'name': name, 'colors': colors.copy()}
                                self.saved_palettes.append(new_entry)
                                self._saved_selected = len(self.saved_palettes) - 1
                                self.render_saved_list()
                                self.mark_modified()
                                messagebox.showinfo(
                                    self.lang.get('preset_added_title'),
                                    self.lang.get('preset_added_msg').format(name=name)
                                )
                                self.log_action(f"Added preset palette: {name}")
                        return use_preset
                    
                    use_btn = ModernSecondaryButton(
                        palette_card,
                        text=self.lang.get('preset_use'),
                        command=make_use(preset),
                        width=60,
                        height=28
                    )
                    use_btn.pack(side='right', padx=10, pady=8)
            
            def on_filter_change(*args):
                display_palettes(filter_var.get())
            
            filter_var.trace_add('write', on_filter_change)
            
            display_palettes()
            
            # Close button
            ModernSecondaryButton(dialog, text=self.lang.get('close_btn'), command=dialog.destroy, width=100).pack(pady=15)
            
        except ImportError:
            messagebox.showerror(self.lang.get('error'), self.lang.get('preset_module_missing'))
        except Exception as e:
            messagebox.showerror(self.lang.get('error'), self.lang.get('preset_open_failed').format(error=str(e)))

    def _show_palette_selection_dialog(self, metadata):
        """Show palette selection dialog for loading palettes"""
        dialog = ctk.CTkToplevel(self)
        set_window_icon(dialog)
        dialog.title(self.lang.get('dialog_open_mps'))
        dialog.geometry("500x400")
        dialog.transient(self)
        dialog.grab_set()
        dialog.configure(fg_color=COLORS['bg_dark'])
        
        # Header
        ctk.CTkLabel(
            dialog,
            text=self.lang.get('saved_palettes_list'),
            font=ctk.CTkFont(family=FONT_FAMILY, size=14, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack(anchor='w', padx=15, pady=15)
        
        # Palette list
        list_frame = ctk.CTkScrollableFrame(dialog, fg_color=COLORS['bg_card'])
        list_frame.pack(fill='both', expand=True, padx=15, pady=5)
        
        selected_file = [None]
        
        for item in metadata:
            name = item.get('name', 'Unknown')
            filepath = item.get('filepath', '')
            colors = item.get('colors', [])
            
            palette_btn = ctk.CTkFrame(list_frame, fg_color=COLORS['bg_secondary'], corner_radius=6)
            palette_btn.pack(fill='x', pady=3)
            
            # Name
            ctk.CTkLabel(
                palette_btn,
                text=name,
                font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"),
                text_color=COLORS['text_primary']
            ).pack(anchor='w', padx=10, pady=(8, 2))
            
            # Color preview
            if colors:
                bar = ctk.CTkFrame(palette_btn, height=20, fg_color="transparent")
                bar.pack(fill='x', padx=10, pady=(0, 8))
                bar.pack_propagate(False)
                
                for c in colors[:8]:
                    swatch = ctk.CTkFrame(bar, fg_color=c, corner_radius=3)
                    swatch.pack(side='left', fill='both', expand=True, padx=1)
            
            # Click to select
            def make_select(fp):
                def handler(e=None):
                    selected_file[0] = fp
                    load_selected()
                return handler
            
            palette_btn.bind('<Button-1>', make_select(filepath))
            palette_btn.configure(cursor='hand2')
        
        def load_selected():
            if selected_file[0]:
                try:
                    self._load_palette_from_file(selected_file[0])
                    dialog.destroy()
                except Exception as e:
                    messagebox.showerror(self.lang.get('error'), str(e))
        
        # Buttons
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(fill='x', padx=15, pady=15)
        
        def browse_file():
            dialog.destroy()
            filename = filedialog.askopenfilename(
                title=self.lang.get('dialog_open_mps'),
                filetypes=[(self.lang.get('my_palette_file'), '*.mps'), (self.lang.get('all_files'), '*.*')]
            )
            if filename:
                self._load_palette_from_file(filename)
        
        ModernSecondaryButton(btn_frame, text=self.lang.get('browse_other_file'), command=browse_file, width=150).pack(side='left', padx=5)
        ModernSecondaryButton(btn_frame, text=self.lang.get('button_cancel'), command=dialog.destroy, width=100).pack(side='right', padx=5)


if __name__ == "__main__":
    app = PaletteApp()
    app.mainloop()
