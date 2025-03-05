from App.database import db

class Config(db.Model):
    __tablename__ = 'config'
    
    id = db.Column(db.Integer, primary_key=True)
    semester = db.Column(db.Integer, nullable=False, default=1)
    
    def __init__(self, semester=1):
        self.semester = semester
    
    def to_json(self):
        return {
            'id': self.id,
            'semester': self.semester
        }
    
    @staticmethod
    def get_current_semester():
        config = Config.query.first()
        return config.semester if config else 1
    
    @staticmethod
    def set_semester(semester):
        config = Config.query.first()
        if config:
            config.semester = semester
        else:
            config = Config(semester=semester)
            db.session.add(config)
        db.session.commit()
        return config 