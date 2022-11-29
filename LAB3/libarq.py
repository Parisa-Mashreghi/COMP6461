class libarq():
    def __init__(self, router=('localhost', 3000), sequence=0):
        self.count_max = 20
        self.address = None
        self.router = router
        self.sequence = sequence

    def bind(self, address):
        self.address = address

    def listen(self, count):
        self.count_max = count

