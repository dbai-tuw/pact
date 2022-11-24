

class Operation:
    """
    Operation specification:
    Expects the initial existence of a basic edge rel with name BASERELNAME and attributes
    's' and 't' that store the two vertices of each edge.
    In the directed case 's' is interpreted as the source and 't' as the target of the arc.
    Each operation specifies a name for it's output relation and it is expected than an execution engine
    maintains these names in such a way that later Operations can refer to them.

    RENAME: Rename relation A as in `renamer`

    JOIN: Join A and B on attributes in list `key`

    SEMIJOIN: Compute the semi-join of B into A on attributes in list `key`

    COUNT_EXT: Count how many extensions each assignment in A of attributes `key` has (downwards in the TD)

    SUM_COUNT: ADD DOC

    PROJECT: project A to attributes in key
    """
    JOIN, SEMIJOIN, RENAME, COUNT_EXT, SUM_COUNT, PROJECT = range(6)
    BASERELNAME = '_edge_base'

    def __init__(self, kind, new_name,
                 A=None, B=None, key=None, rename_key=None):
        self.kind = kind
        self.new_name = new_name
        self.A = A
        self.B = B
        self.key = key
        self.rename_key = rename_key

    def __repr__(self):
        if self.kind == Operation.JOIN:
            return f'{self.new_name} = {self.A} ⨝ {self.B} (on {self.key})'
        elif self.kind == Operation.SEMIJOIN:
            return f'{self.new_name} = {self.A} ⋉ {self.B} (on {self.key})'
        elif self.kind == Operation.COUNT_EXT:
            return f'{self.new_name} = Count extensions of {self.key} in {self.A}'
        elif self.kind == Operation.SUM_COUNT:
            return f'{self.new_name} = Merge count from {self.B}({self.key}) into {self.A}'
        elif self.kind == Operation.RENAME:
            a, b = self.rename_key['s'], self.rename_key['t']
            return f'⍴: {self.A} -> {self.new_name}({a}, {b})'
        elif self.kind == Operation.PROJECT:
            return f'{self.new_name} = project {self.A} to {self.key}'
