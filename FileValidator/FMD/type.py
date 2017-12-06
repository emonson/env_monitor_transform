from pyrsistent import PRecord, field

class Validate(PRecord):
    #allows us to inherit all the PRecord methods
    validate_number = field(mandatory=True, factory=int, 
                            invariant=lambda x: (x <= 10, 'Number exceeds range'))
    validate_string = field(factory=str, 
                            invariant=lambda x: (len(x) <= 20, 'Too many characters'))
