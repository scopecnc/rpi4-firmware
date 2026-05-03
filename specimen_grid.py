"""
Specimen Grid Management for Automated Mineral Display
Handles tray configuration, position calculations, and specimen cycling
"""

import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class SpecimenPosition:
    """Position and metadata for a single specimen"""
    row: int
    col: int
    mineral_name: str
    location: str
    collector: str
    x_offset_mm: float  # Relative offset from nominal grid position
    y_offset_mm: float  # Relative offset from nominal grid position
    focus_mm: float     # Absolute Z position (focus height)
    zoom_mm: float      # Absolute F position (zoom ring)
    
    def __str__(self):
        return f"[{self.row},{self.col}] {self.mineral_name} from {self.location} (collected by {self.collector})"


class SpecimenGrid:
    """Manages specimen grid positioning and tray configuration"""
    
    # Grid physical constants
    GRID_COLS = 7
    GRID_ROWS = 4
    BOX_WIDTH_MM = 39.0   # mm spacing between box centers
    BOX_HEIGHT_MM = 43.0  # mm spacing between box centers (from CAD model)
    GRID_START_X = 19.5   # mm - center of box [0,0]
    GRID_START_Y = 22.5   # mm - center of box [0,0]
    
    # Soft limits (from protocol spec)
    LIMIT_X_MIN = 0.0
    LIMIT_X_MAX = 270.0
    LIMIT_Y_MIN = 0.0
    LIMIT_Y_MAX = 155.0
    LIMIT_Z_MIN = 0.0
    LIMIT_Z_MAX = 30.0
    # F (zoom) has no limit per spec
    
    def __init__(self, tray_config_path: str):
        """
        Initialize grid from tray configuration file
        
        Args:
            tray_config_path: Path to JSON tray configuration
        """
        self.tray_config_path = tray_config_path
        self.specimens: List[SpecimenPosition] = []
        self.current_position: Optional[Dict[str, float]] = None
        self._load_config()
    
    def _load_config(self):
        """Load and validate tray configuration from JSON"""
        try:
            with open(self.tray_config_path, 'r') as f:
                config = json.load(f)
            
            self.specimens = []
            
            # Handle empty or missing 'specimens' key
            if 'specimens' not in config:
                print(f"[Grid] WARNING: No 'specimens' key in config file {self.tray_config_path}")
                print(f"[Grid] Loaded 0 specimens - system will home and stay idle")
                return
            
            for spec_data in config['specimens']:
                specimen = SpecimenPosition(
                    row=spec_data['row'],
                    col=spec_data['col'],
                    mineral_name=spec_data['mineral_name'],
                    location=spec_data['location'],
                    collector=spec_data['collector'],
                    x_offset_mm=spec_data['x_offset_mm'],
                    y_offset_mm=spec_data['y_offset_mm'],
                    focus_mm=spec_data['focus_mm'],
                    zoom_mm=spec_data['zoom_mm']
                )
                self.specimens.append(specimen)
            
            if len(self.specimens) == 0:
                print(f"[Grid] WARNING: Loaded 0 specimens from {self.tray_config_path}")
                print(f"[Grid] System will home and stay idle (no auto-cycle)")
            else:
                print(f"[Grid] Loaded {len(self.specimens)} specimens from {self.tray_config_path}")
            
        except FileNotFoundError:
            print(f"[Grid] ERROR: Tray config file not found: {self.tray_config_path}")
            raise
        except json.JSONDecodeError as e:
            print(f"[Grid] ERROR: Invalid JSON in tray config: {e}")
            raise
        except KeyError as e:
            print(f"[Grid] ERROR: Missing required field in tray config: {e}")
            raise
    
    def calculate_position(self, specimen: SpecimenPosition) -> Tuple[float, float, float, float]:
        """
        Calculate absolute X,Y,Z,F position for a specimen
        
        Args:
            specimen: Specimen position data
            
        Returns:
            Tuple of (x, y, z, f) in mm
        """
        # Calculate nominal grid position
        nominal_x = self.GRID_START_X + (specimen.col * self.BOX_WIDTH_MM)
        nominal_y = self.GRID_START_Y + (specimen.row * self.BOX_HEIGHT_MM)
        
        # Apply offsets
        actual_x = nominal_x + specimen.x_offset_mm
        actual_y = nominal_y + specimen.y_offset_mm
        
        # Z and F are absolute
        actual_z = specimen.focus_mm
        actual_f = specimen.zoom_mm
        
        return actual_x, actual_y, actual_z, actual_f
    
    def validate_position(self, x: float, y: float, z: float, f: float) -> Tuple[bool, str]:
        """
        Validate position against soft limits
        
        Args:
            x, y, z, f: Position in mm
            
        Returns:
            Tuple of (valid, error_message)
        """
        if x < self.LIMIT_X_MIN or x > self.LIMIT_X_MAX:
            return False, f"X={x:.2f}mm exceeds limits [{self.LIMIT_X_MIN}-{self.LIMIT_X_MAX}mm]"
        
        if y < self.LIMIT_Y_MIN or y > self.LIMIT_Y_MAX:
            return False, f"Y={y:.2f}mm exceeds limits [{self.LIMIT_Y_MIN}-{self.LIMIT_Y_MAX}mm]"
        
        if z < self.LIMIT_Z_MIN or z > self.LIMIT_Z_MAX:
            return False, f"Focus={z:.2f}mm exceeds limits [{self.LIMIT_Z_MIN}-{self.LIMIT_Z_MAX}mm]"
        
        # F has no limit per spec
        
        return True, ""
    
    def update_current_position(self, x: float, y: float, z: float, f: float):
        """
        Update tracked current position
        
        Args:
            x, y, z, f: Current position in mm
        """
        self.current_position = {'x': x, 'y': y, 'z': z, 'f': f}
    
    def get_specimens(self) -> List[SpecimenPosition]:
        """Get list of all specimens"""
        return self.specimens
    
    def get_specimen_count(self) -> int:
        """Get total number of specimens"""
        return len(self.specimens)


def create_example_tray_config(filename: str = "mindatnh_tray1.json"):
    """
    Create an example tray configuration file
    
    Args:
        filename: Output filename
    """
    specimens = []
    
    # Generate 28 specimens (7 cols x 4 rows)
    mineral_names = [
        "Quartz", "Pyrite", "Galena", "Fluorite", "Calcite", "Beryl", "Topaz",
        "Garnet", "Tourmaline", "Amethyst", "Citrine", "Malachite", "Azurite", "Chrysocolla",
        "Hematite", "Magnetite", "Sphalerite", "Chalcopyrite", "Bornite", "Rhodochrosite", "Smithsonite",
        "Celestite", "Barite", "Gypsum", "Halite", "Stibnite", "Realgar", "Orpiment"
    ]
    
    locations = [
        "Colorado", "Peru", "Mexico", "China", "Brazil", "Russia", "Australia",
        "Madagascar", "Pakistan", "Afghanistan", "Morocco", "Namibia", "South Africa", "Germany"
    ]
    
    collectors = [
        "John Smith", "Jane Doe", "Bob Johnson", "Alice Williams", "Charlie Brown"
    ]
    
    idx = 0
    for row in range(4):
        for col in range(7):
            if idx < len(mineral_names):
                # Small random-looking offsets within ±2mm
                x_offset = ((row + col) % 5 - 2) * 0.5  # -1.0 to +1.0mm
                y_offset = ((row * col) % 5 - 2) * 0.5  # -1.0 to +1.0mm
                
                # Focus varies by specimen height (5-20mm)
                focus = 8.0 + (idx % 10)  # 8-18mm
                
                # Zoom varies slightly (0-10mm range)
                zoom = 2.0 + (idx % 8)  # 2-10mm
                
                specimen = {
                    "row": row,
                    "col": col,
                    "mineral_name": mineral_names[idx],
                    "location": locations[idx % len(locations)],
                    "collector": collectors[idx % len(collectors)],
                    "x_offset_mm": round(x_offset, 2),
                    "y_offset_mm": round(y_offset, 2),
                    "focus_mm": round(focus, 2),
                    "zoom_mm": round(zoom, 2)
                }
                specimens.append(specimen)
                idx += 1
    
    config = {"specimens": specimens}
    
    with open(filename, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"[Grid] Created example tray config: {filename}")
    print(f"[Grid] Contains {len(specimens)} specimens")


if __name__ == "__main__":
    # Create example config when run directly
    create_example_tray_config()
    
    # Test loading it
    grid = SpecimenGrid("mindatnh_tray1.json")
    print(f"\nLoaded {grid.get_specimen_count()} specimens:")
    for spec in grid.get_specimens()[:3]:  # Show first 3
        x, y, z, f = grid.calculate_position(spec)
        print(f"  {spec}")
        print(f"    Position: X={x:.2f} Y={y:.2f} Focus={z:.2f} Zoom={f:.2f}")
        valid, msg = grid.validate_position(x, y, z, f)
        print(f"    Valid: {valid} {msg if not valid else ''}")
