
from __future__ import annotations
from dataclasses import dataclass
from abc import ABC
import random
from typing import List, Tuple

# === Type chart (bem simples) ===
# Apenas alguns tipos para fins didáticos
TYPES = ("Normal", "Fire", "Water", "Grass", "Electric")

TYPE_CHART = {
    ("Fire", "Grass"): 2.0,
    ("Fire", "Water"): 0.5,
    ("Fire", "Fire"): 0.5,
    ("Water", "Fire"): 2.0,
    ("Water", "Grass"): 0.5,
    ("Water", "Water"): 0.5,
    ("Grass", "Water"): 2.0,
    ("Grass", "Fire"): 0.5,
    ("Grass", "Grass"): 0.5,
    ("Electric", "Water"): 2.0,
    ("Electric", "Grass"): 0.5,
    ("Electric", "Electric"): 0.5,
}

def effectiveness(attack_type: str, defend_type: str) -> float:
    return TYPE_CHART.get((attack_type, defend_type), 1.0)

@dataclass
class Move:
    name: str
    type: str
    power: int
    max_pp: int
    pp: int = None

    def __post_init__(self):
        if self.type not in TYPES:
            raise ValueError(f"Tipo inválido: {self.type}")
        if self.pp is None:
            self.pp = self.max_pp

    def can_use(self) -> bool:
        return self.pp > 0

    def use(self, attacker: 'Pokemon', defender: 'Pokemon') -> Tuple[int, float, bool]:
        if not self.can_use():
            raise RuntimeError(f"Sem PP para {self.name}")
        self.pp -= 1

        # STAB (Same Type Attack Bonus)
        stab = 1.5 if self.type == attacker.type else 1.0

        # Efetividade
        eff = effectiveness(self.type, defender.type)

        # Variância para não ficar determinístico
        variance = random.uniform(0.85, 1.0)

        # Fórmula de dano didática (não oficial)
        base = (attacker.attack / defender.defense) * self.power
        damage = int(base * stab * eff * variance)
        damage = max(1, damage)  # sempre pelo menos 1
        defender.take_damage(damage)
        return damage, eff, stab > 1.0

class Pokemon(ABC):
    def __init__(self, name: str, type_: str, max_hp: int, attack: int, defense: int, speed: int, moves: List[Move]):
        if type_ not in TYPES:
            raise ValueError(f"Tipo inválido: {type_}")
        self.name = name
        self.type = type_
        self.max_hp = max_hp
        self.hp = max_hp
        self.attack = attack
        self.defense = defense
        self.speed = speed
        self.moves = moves

    def is_fainted(self) -> bool:
        return self.hp <= 0

    def take_damage(self, amount: int) -> None:
        self.hp = max(0, self.hp - amount)

    def choose_move(self, idx: int) -> Move:
        if idx < 0 or idx >= len(self.moves):
            raise IndexError("Índice de golpe inválido")
        return self.moves[idx]

    def __str__(self) -> str:
        bar_len = 20
        filled = int((self.hp / self.max_hp) * bar_len) if self.max_hp > 0 else 0
        bar = "█" * filled + " " * (bar_len - filled)
        return f"{self.name} [{self.type}] HP: {self.hp}/{self.max_hp} |{bar}|"

# === Alguns Pokémon prontos ===
class Charmander(Pokemon):
    def __init__(self, apelido: str = "Charmander"):
        moves = [
            Move("Scratch", "Normal", power=40, max_pp=35),
            Move("Ember", "Fire", power=40, max_pp=25),
            Move("Fire Fang", "Fire", power=65, max_pp=15),
            Move("Bite", "Normal", power=60, max_pp=25),
        ]
        super().__init__(apelido, "Fire", max_hp=120, attack=60, defense=50, speed=65, moves=moves)

class Squirtle(Pokemon):
    def __init__(self, apelido: str = "Squirtle"):
        moves = [
            Move("Tackle", "Normal", power=40, max_pp=35),
            Move("Water Gun", "Water", power=40, max_pp=25),
            Move("Bubble", "Water", power=40, max_pp=30),
            Move("Bite", "Normal", power=60, max_pp=25),
        ]
        super().__init__(apelido, "Water", max_hp=130, attack=50, defense=65, speed=43, moves=moves)

class Bulbasaur(Pokemon):
    def __init__(self, apelido: str = "Bulbasaur"):
        moves = [
            Move("Tackle", "Normal", power=40, max_pp=35),
            Move("Vine Whip", "Grass", power=45, max_pp=25),
            Move("Razor Leaf", "Grass", power=55, max_pp=25),
            Move("Headbutt", "Normal", power=70, max_pp=15),
        ]
        super().__init__(apelido, "Grass", max_hp=125, attack=55, defense=60, speed=45, moves=moves)

class Pikachu(Pokemon):
    def __init__(self, apelido: str = "Pikachu"):
        moves = [
            Move("Quick Attack", "Normal", power=40, max_pp=30),
            Move("Thunder Shock", "Electric", power=40, max_pp=30),
            Move("Spark", "Electric", power=65, max_pp=20),
            Move("Slam", "Normal", power=80, max_pp=10),
        ]
        super().__init__(apelido, "Electric", max_hp=110, attack=55, defense=40, speed=90, moves=moves)

class Eevee(Pokemon):
    def __init__(self, apelido: str = "Eevee"):
        moves = [
            Move("Quick Attack", "Normal", power=40, max_pp=30),
            Move("Swift", "Normal", power=60, max_pp=20),
            Move("Bite", "Normal", power=60, max_pp=25),
            Move("Double-Edge", "Normal", power=90, max_pp=10),
        ]
        super().__init__(apelido, "Normal", max_hp=118, attack=60, defense=55, speed=55, moves=moves)

# Conveniência para catálogo
POKEDEX = {
    "Charmander": Charmander,
    "Squirtle": Squirtle,
    "Bulbasaur": Bulbasaur,
    "Pikachu": Pikachu,
    "Eevee": Eevee,
}
