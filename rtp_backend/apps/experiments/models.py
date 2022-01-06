from rtp_backend import db


class ProcessVariables(db.Model):
    pv_string = db.Column(db.String(100), primary_key=True)
    
    def __repr__(self) -> str:
        return self.pv_string
