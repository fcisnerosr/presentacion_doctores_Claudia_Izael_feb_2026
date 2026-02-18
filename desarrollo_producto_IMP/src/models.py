"""
Modelos de Datos - Etapa 2: Parsing y Extracción
Procesador de Fatiga SACS v1.0

Define las estructuras de datos para elementos de fatiga.
"""

from dataclasses import dataclass
from typing import Optional
import numpy as np


@dataclass
class FatigueElement:
    """
    Representa un elemento estructural con datos de fatiga.
    
    Attributes:
        joint: Identificador del nodo/junta (ej: "0003")
        member: Identificador del miembro (ej: "802L 0005", "0002-501L")
        grup: Identificador del grupo (ej: "16A", "DL9")
        damages: Array de 8 valores de daño circunferenciales
                 [TOP, TOP-LEFT, LEFT, BOT-LEFT, BOT, BOT-RIGHT, RIGHT, TOP-RIGHT]
    """
    joint: str
    member: str
    grup: str
    damages: np.ndarray
    
    def __post_init__(self):
        """Validación después de inicialización."""
        if not isinstance(self.damages, np.ndarray):
            self.damages = np.array(self.damages, dtype=np.float64)
        
        if len(self.damages) != 8:
            raise ValueError(f"Se esperan 8 valores de daño, se recibieron {len(self.damages)}")
    
    @property
    def unique_key(self) -> str:
        """
        Genera clave única para identificar el elemento.
        
        Returns:
            String en formato "JOINT_MEMBER_GRUP"
        """
        return f"{self.joint}_{self.member}_{self.grup}"
    
    @property
    def max_damage(self) -> float:
        """
        Retorna el valor máximo de daño entre las 8 posiciones.
        
        Returns:
            float: Máximo daño
        """
        return float(self.damages.max())
    
    @property
    def critical_location(self) -> str:
        """
        Determina la ubicación crítica (con mayor daño).
        
        Returns:
            str: Ubicación con mayor daño (TOP, TOP-LEFT, etc.)
        """
        locations = ['TOP', 'TOP-LEFT', 'LEFT', 'BOT-LEFT', 
                     'BOT', 'BOT-RIGHT', 'RIGHT', 'TOP-RIGHT']
        return locations[int(self.damages.argmax())]
    
    def to_dict(self) -> dict:
        """
        Convierte el elemento a diccionario.
        
        Returns:
            dict: Representación en diccionario
        """
        return {
            'JOINT': self.joint,
            'MEMBER': self.member,
            'GRUP': self.grup,
            'TOP': self.damages[0],
            'TOP-LEFT': self.damages[1],
            'LEFT': self.damages[2],
            'BOT-LEFT': self.damages[3],
            'BOT': self.damages[4],
            'BOT-RIGHT': self.damages[5],
            'RIGHT': self.damages[6],
            'TOP-RIGHT': self.damages[7],
            'MAX_DAMAGE': self.max_damage,
            'CRITICAL_LOCATION': self.critical_location,
            'UNIQUE_KEY': self.unique_key
        }
    
    def __repr__(self) -> str:
        """Representación string del elemento."""
        return (f"FatigueElement(joint='{self.joint}', member='{self.member}', "
                f"grup='{self.grup}', max_damage={self.max_damage:.2e})")


@dataclass
class ParseResult:
    """
    Resultado del parsing de un archivo SACS FTG.
    
    Attributes:
        elements: Diccionario de elementos {unique_key: FatigueElement}
        total_elements: Número total de elementos parseados
        errors: Lista de errores encontrados durante el parsing
        warnings: Lista de advertencias
    """
    elements: dict
    total_elements: int
    errors: list
    warnings: list
    
    def get_element(self, key: str) -> Optional[FatigueElement]:
        """
        Obtiene un elemento por su clave única.
        
        Args:
            key: Clave única del elemento
            
        Returns:
            FatigueElement o None si no existe
        """
        return self.elements.get(key)
    
    def get_summary(self) -> dict:
        """
        Genera resumen del resultado del parsing.
        
        Returns:
            dict: Resumen con estadísticas
        """
        if not self.elements:
            return {
                'total_elements': 0,
                'max_damage_overall': 0.0,
                'errors_count': len(self.errors),
                'warnings_count': len(self.warnings)
            }
        
        # Encontrar elemento con mayor daño
        max_elem = max(self.elements.values(), key=lambda e: e.max_damage)
        
        return {
            'total_elements': self.total_elements,
            'max_damage_overall': max_elem.max_damage,
            'critical_element': max_elem.unique_key,
            'critical_location': max_elem.critical_location,
            'errors_count': len(self.errors),
            'warnings_count': len(self.warnings)
        }
    
    def __repr__(self) -> str:
        """Representación string del resultado."""
        return (f"ParseResult(elements={self.total_elements}, "
                f"errors={len(self.errors)}, warnings={len(self.warnings)})")
