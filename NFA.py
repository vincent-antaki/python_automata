import warnings
from DFA import DFA

class NFA:
    """This class represents a non-deterministic finite automaton."""

    def __init__(self, states, alphabet, delta, start, accepts, epsilon='epi'):
        """The inputs to the class are as follows:
         - states: An iterable containing the states of the DFA. States must be immutable. None is not a valid state.
         - alphabet: An iterable containing the symbols in the DFA's alphabet. Symbols must be immutable. No need to put epsilon in alphabet.
         - delta: A complete function from [states]x[alphabets]->{None | [states] | set([states])}.
         - start: The state at which the DFA begins operation.
         - accepts: A list containing the "accepting" or "final" states of the NFA.
         - epsilon : a immutable representing the epsilon transitions symbol

        Making delta a function rather than a transition table makes it much easier to define certain NFAs.
        If you want to use a transition table, you can just do this:
         delta = lambda q,c: set(transition_table[q][c])
        One caveat is that the function should not depend on the value of 'states' or 'accepts', since
        these may be modified during minimization.

        Finally, the names of states and inputs should be hashable. This generally means strings, numbers,
        or tuples of hashables.
        """
        self.states = set(states)
        if hasattr(start,'__iter__'):
            self.start = set(start)
        else :
            self.start = set([start])
        self.delta = delta
        self.accepts = set(accepts)
        self.alphabet = set(alphabet)
        self.current_state = self.start
        self.EPSILON=epsilon
        self.alphabet.add(self.EPSILON)

        self._perform_eps_closure()

        if len(self.start) is not 1:
            warnings.warn("Your NFA has more than one initial state. ")

#
# Administrative functions:
#

    def pretty_print(self):
        """Displays all information about the NFA in an easy-to-read way. Not
        actually that easy to read if it has too many states.
        """
        print("")
        print("This DFA has %s states" % len(self.states))
        print("States:", self.states)
        print("Alphabet:", self.alphabet)
        print("Starting state:", self.start)
        print("Accepting states:", self.accepts)
        print("Transition function:")
        print("\t","\t".join(map(str, sorted(self.states))))
        for c in self.alphabet:
            results = map(lambda x: self.delta(x, c), sorted(self.states))
            print(c, "\t", "\t".join(map(str, results)))
        print("Current state:", self.current_state)
        print("Currently accepting:", self.status())
        print("")

    def validate(self):
        """Checks that:
        (1) The accepting-state set is a subset of the state set.
        (2) The start-state is a member of the state set.
        (3) The current-state is a member of the state set.
        (4) Every transition returns a set of members of the state set.
        """
        assert set(self.accepts).issubset(set(self.states))
        assert self.start in self.states
        assert self.current_state in self.states
        for state in self.states:
            for char in self.alphabet:
                a = self.delta(state,char)
                if hasattr(a,'__iter__'):
                    assert a <= self.states
                else:
                    assert a in self.states

    def copy(self):
        """Returns a copy of the DFA. No data is shared with the original."""
        return NFA(self.states, self.alphabet, self.delta, self.start, self.accepts)

#
# Simulating execution:
#
    def step(self,char):
        """Updates the NFA's current state(s) based on a single character of input."""
        if char not in self.alphabet:
            return None

        self.current_state = self.input(char)

        self._perform_eps_closure()

    def input(self, char):
        """Calculate the states resulting on a single character of input based on current state."""
        if char not in self.alphabet:
            return None
        else :
#            self.current_state = self.delta(self.current_state, char)
            a = set()
            for x in [self.delta(i,char) for i in self.current_state]:
                if hasattr(x,'__iter__'):
                    a.update(x)
                elif x is not None :
                    a.add(x)
        return a



    def _perform_eps_closure(self):
        """Update the NFA's current state based on all epsilon transition you can take from any member of current_state"""
        self.current_state.update(self.input(self.EPSILON))

    def input_sequence(self, char_sequence):
        """Updates the DFA's current state based on an iterable of inputs."""
        for char in char_sequence:
            self.step(char)

    def status(self):
        """Indicates whether one of the NFA's current state is accepting."""
        return any([i in self.accepts for i in self.current_state])

    def reset(self):
        """Returns the NFA to the starting state."""
        self.current_state = self.start
        self._perform_eps_closure()

    def recognizes(self, char_sequence):
        """Indicates whether the NFA accepts a given string."""
        state_save = self.current_state
        self.reset()
        self.input_sequence(char_sequence)
        valid = self.status()
        self.current_state = state_save
        return valid

    def build_DFA_from_NFA(self):
        saved_state = self.current_state
        self.reset()
        delta = {}
        dfa_states = []
        to_explore_queue = [frozenset(self.current_state)]
        while(len(to_explore_queue) != 0):
            e = to_explore_queue.pop(0)
            delta[e] = dict()
            for a in self.alphabet :
                self.current_state = e
                self.step(a)
                entry = frozenset(self.current_state)
                delta[e][a] = entry
                if (entry not in to_explore_queue and entry not in dfa_states) :
#                if not( any(self.current_state == i for i in to_explore_queue) or any(self.current_state == i for i in dfa_states)):
                    to_explore_queue.append(entry)
            dfa_states.append(e)

        #   Calculate accept
        accept = filter(lambda x: len(self.accepts & x ) > 0,dfa_states)

        return DFA(dfa_states, self.alphabet, lambda x,y : delta[x][y], dfa_states[0], accept)

