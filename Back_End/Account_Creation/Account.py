class Account:
    username = None
    password = None
    email = None
    id = None
    
    # Constructor
    def init(self, username, password, email, id):
        self.username = username
        self.password = password
        self.email = email
        self.ID = id
        
    # Getters & Setters
    def get_username(self):
        return self.username
    
    def get_password(self):
        return self.password
    
    def get_id(self):
        return self.id
    
    def get_email(self):
        return self.email
    
    def set_username(self, username):
        self.username = username
    
    def set_password(self, password):
        self.password = password
    
    def set_id(self, id):
        self.id = id
    
    def set_email(self, email):
        self.email = email