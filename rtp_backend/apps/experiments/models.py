from rtp_backend import db

class ProcessVariable(db.Model):
    pv_string = db.Column(db.String(100), primary_key=True)
    experiment_short_id = db.Column(db.String(100), db.ForeignKey('experiment.short_id'), nullable=False)
    
    def __repr__(self) -> str:
        return self.pv_string
    
class Experiment(db.Model):
    short_id = db.Column(db.String(100), primary_key=True)
    process_variables = db.relationship('ProcessVariable', backref='experiment', lazy=True)
    user_ids = db.Column(db.Text(length=36), db.ForeignKey('user.user_id'),
        nullable=False)
