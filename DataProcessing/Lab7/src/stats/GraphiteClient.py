import graphyte

class GraphyteSingleton:
    def __init__(self) -> None:
        graphyte.init('graphite', prefix='myapp')
    
    def read_attempt(self, cahche_name: str):
        graphyte.send(f"cache{cahche_name}_read_attempt", 1)
    
    def read_successful(self, cahche_name: str):
        graphyte.send(f"cache{cahche_name}_read_success", 1)
            
    def write_attempt(self, cahche_name: str):
        graphyte.send(f"cache{cahche_name}_write_attempt", 1)
    
    def write_successful(self, cahche_name: str):
        graphyte.send(f"cache{cahche_name}_write_success", 1)
    
    def write_context_get_time(self, time):
        graphyte.send(self.write_context_get_time.__name__, time)
    
Stats = GraphyteSingleton()