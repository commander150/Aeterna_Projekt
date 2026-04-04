class CombatResolver:
    def __init__(self, simulation):
        self.simulation = simulation

    def resolve_attack_phase(self, tamado, vedo):
        return self.simulation.harc_fazis(tamado, vedo)
