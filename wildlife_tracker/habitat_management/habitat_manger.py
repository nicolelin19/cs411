from typing import Optional, List, Any
from wildlife_tracker.animal_management.animal import Animal
from wildlife_tracker.habitat_management.habitat import Habitat

class HabitatManager:
    def __init__ (self):
        self.habitats: dict[int, Habitat] = {}

    def update_habitat_details(self, **kwargs: dict[str: Any]) -> None:
        pass

    def assign_animals_to_habitat(self, animals: List[Animal]) -> None:
        pass

    def get_animals_in_habitat(self) -> List[Animal]:
        pass

    def get_habitat_details(self) -> dict:
        pass

    def create_habitat(habitat_id: int, geographic_area: str, size: int, environment_type: str) -> Habitat:
        pass

    def remove_habitat(habitat_id: int) -> None:
        pass

    def get_habitats_by_geographic_area(geographic_area: str) -> List[Habitat]:
        pass

    def get_habitats_by_size(size: int) -> List[Habitat]:
        pass

    def get_habitats_by_type(environment_type: str) -> List[Habitat]:
        pass

    
    
    

