class User:

    def __init__(self, request):
        self.email = request.get('email')
        self.password = request.get('password')
        self.ssn = request.get('ssn')
        self.first_name = request.get('first_name')
        self.middle_name = request.get('middle_name')
        self.last_name = request.get('last_name')
        self.address_line_1 = request.get('address_line_1')
        self.address_line_2 = request.get('address_line_2')
        self.city = request.get('city')
        self.state = request.get('state')
        self.zipcode = request.get('zipcode')
        self.address_mismatch = 0
        
        self.fields_map = request.copy()
        self.fields_map.pop('email', None)
        self.fields_map.pop('password', None)
