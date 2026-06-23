class PhaseRunner:
    def __init__(self, simulation):
        self.simulation = simulation

    def run_play_phase(self, jatekos):
        return self.simulation.kijatszas_fazis(jatekos)
