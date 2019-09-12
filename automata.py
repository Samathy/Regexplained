import graphviz

class State:

    def __init__(self, name, style="solid", color="black"):
        self.name = name
        self.style = style
        self.color = color
        self.rank = ""
        
        self.rendered = False
        
    def set_style(self, style):
        self.style = style

    def __eq__(self, other):
        if self.name == other:
            return True
        else:
            return False
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return self.name

    def render(self, graph):
        graph.node(self.name, style=self.style, color=self.color)


class automata:

    def __init__(self, state_names, alphabet, start_state, final_states, graph_args={}):
        self.alphabet = alphabet
        self.start_state = start_state
        self.final_states = final_states
        self.edges = list()
        self.states = list()
        self.graph = None
        self.graph_args = graph_args
        
      
        for state_name in state_names:
            style= None
            if state_name == start_state:
                self.states.append(State("", style="invis"))
                style = "bold"
                self.edges.append(["", state_name, ""])
            if state_name in final_states:
                style = "dashed"
              
            self.states.append(State(state_name, style = style))

        return
    
    def __remove_invisible(self):
        new_states = list()
        new_edges = list()
        
        for state in self.states:
            if state.style == "invis" or state.name == "":
                continue
            else:
                new_states.append(state)
        for edge in self.edges:
            if edge[0] == "":
                continue
            else:
                new_edges.append(edge)
        self.states = new_states
        self.edges = new_edges

    
    
    def __rename_states(self, name_postfix):
        renamed_states = list()
        renamed_edges = list()
        renamed_final_states = list()
            
        for s in self.states:
            if len(s.name) <= 0:
                break
            renamed_states.append(str(s)+str(name_postfix))
        for e in self.edges:
            if len(e[0]) <= 0:
                renamed_edges.append([e[0], e[1]+str(name_postfix), e[2]])

            renamed_edges.append([e[0]+str(name_postfix), e[1]+str(name_postfix), e[2]])
        for s in self.final_states:
            renamed_final_states.append(s+str(name_postfix))
                
             
        self.states = renamed_states
        self.edges = renamed_edges
        self.final_states = renamed_final_states
        self.start_state = self.start_state+str(name_postfix)
        
    def __copy(self):
        a = automata([str(s) for s in self.states[1:]], self.alphabet, self.start_state, self.final_states)
        a.edges = self.edges
        return a
    
    def from_union(automatons):
        
        new_states = list()
        new_edges = list()
        new_final_states = list()
        
        copied_automatons = list()
        
        for a in automatons:
            copied_automatons.append(a.__copy())
            
            
        i = 0
        for a in copied_automatons:
            a.__remove_invisible()
            a.__rename_states(i)
            
            new_states += a.states
            new_edges += a.edges
            new_final_states += a.final_states
            i = i+1
                   
        new_states.append("start")
                
        for a in copied_automatons:
            new_edges.append(["start", a.start_state, "ε"])
        
        new_automaton = automata(new_states, automatons[0].alphabet, "start", new_final_states)
        new_automaton.edges = new_automaton.edges + new_edges

        return new_automaton
    
    def from_concat(automatons):
        copied_automatons = list()
        
        for a in automatons:
            copied_automatons.append(a.__copy())
        
        i = 0
        for a in copied_automatons:
            a.__remove_invisible()
            a.__rename_states(i)
            i+=1

        first_automaton = copied_automatons[0]
        
        
        new_states = list()
        new_edges = list()
        new_final_states = list()
        
        for a in copied_automatons:
            new_states += a.states
            new_edges += a.edges

        new_final_states = copied_automatons[-1].final_states

            
        
        new_automaton = automata(new_states, copied_automatons[0], copied_automatons[0].start_state, new_final_states)
        
        new_automaton.edges = new_edges
            
        for i in range(len(copied_automatons)):
            last_a = copied_automatons[i]
            if i != len(copied_automatons)-1:
                next_a = copied_automatons[i+1]
            else:
                break
            for state in last_a.final_states:
                pass
                new_automaton.edge(state, next_a.start_state, "ε")
            
        return new_automaton
    
    def from_star(automaton):
        copied_automaton = automaton.__copy()
        
        copied_automaton.__remove_invisible()
        
        for state in copied_automaton.final_states:
            copied_automaton.edge(state, copied_automaton.start_state, "ε")
        
        copied_automaton.states[0].style = "solid"  
        copied_automaton.states.append(State("start"))
        copied_automaton.edge("start", copied_automaton.start_state, "ε")
        copied_automaton.start_state = "start"
        
        
        return copied_automaton
        
        
    def _check_start_end(self):
        for state in self.states:
            if state.name == "":
                continue
            if state.name == self.start_state:
                state.style = "bold" 
            if state.name in self.final_states:
                state.style = "dashed"
        return
            

    def edge(self, source, dest, rule):
        self.edges.append([source, dest, "  "+rule])
        if source not in self.states:
            self.states.append(State(source))
            self._check_start_end()
        if dest not in self.states:
            self.states.append(State(dest))
            self._check_start_end()
        return
    
    def _repr_svg_(self):
        self.graph = graphviz.Digraph()

        for key in self.graph_args.keys():
            self.graph.graph_attr[key] = self.graph_args[key]
        
        self._check_start_end() # Update if we changed/added the start/end states since making this obeject
        
        for state in self.states:
            state.render(self.graph)

        for e in self.edges:
            self.graph.edge(e[0], e[1], label=e[2])

        return self.graph._repr_svg_()
