from typing import Any, Optional

class Animal:

    def __init__(self,
                age: Optional[int],
                animal_id: int,
                health_status: Optional[str] = None,
    ) -> None:
        self.age = age
        self.animal_id = animal_id
        self.health_status = health_status
    pass

