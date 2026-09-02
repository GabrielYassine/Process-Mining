class PetriNet():

    def __init__(self):
        self.places = []
        self.transitions = []
        self.relations = []
        
    def add_place(self, id):
        self.places.append(
            {
                "id": id, 
                "tokens": 0
            }
        )

    def add_transition(self, name, id):
        self.transitions.append(
                {
                    "name": name, 
                    "id": id
                }
            )

    def get_from_id(self, id):
        if id > 0:
            for place in self.places:
                if place["id"] == id:
                    return place
        else:
            for transition in self.transitions:
                if transition["id"] == id:
                    return transition

    def add_edge(self, source_id, target_id):
        self.relations.append(
            {
                "source": self.get_from_id(source_id), 
                "target": self.get_from_id(target_id)
            }
        )
        return self

    def get_tokens(self, place_id):
        for place in self.places:
            if place["id"] == place_id:
                return place["tokens"]

                
    def is_enabled(self, transition_id):
        for edge in self.relations:
            if edge["target"]["id"] == transition_id:
                if edge["source"]["tokens"] < 1:
                    return False
        return True


    def add_marking(self, place_id):
        for place in self.places:
            if place["id"] == place_id:
                place["tokens"] += 1
            

    def fire_transition(self, transition_id):
        for edge in self.relations:
            if edge["source"]["id"] == transition_id:
                edge["target"]["tokens"] += 1
            elif edge["target"]["id"] == transition_id:
                edge["source"]["tokens"] -= 1