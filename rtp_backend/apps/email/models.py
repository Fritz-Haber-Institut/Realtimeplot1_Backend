from rtp_backend import db


class Subscription(db.Model):
    user_id = db.Column(
        "user_id", db.Text(length=36), db.ForeignKey("user.user_id"), primary_key=True
    )
    pv_string = db.Column(
        "pv_string",
        db.String(100),
        db.ForeignKey("process_variable.pv_string"),
        primary_key=True,
    )
    email = db.Column(db.String(100), nullable=False, primary_key=True)
    threshold_min = db.Column(db.Integer, nullable=False)
    threshold_max = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "pv_string": self.pv_string,
            "email": self.email,
            "threshold_min": int(self.threshold_min) if self.threshold_min else None,
            "threshold_max": int(self.threshold_max) if self.threshold_max else None,
        }
