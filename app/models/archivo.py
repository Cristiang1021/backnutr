from ..factory import db
from datetime import datetime


class Archivo(db.Model):
    __tablename__ = 'archivos'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    nombre = db.Column(db.String(255), nullable=False)
    contenido = db.Column(db.LargeBinary, nullable=True)
    fecha_creacion = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, usuario_id, nombre, contenido=None):
        self.usuario_id = usuario_id
        self.nombre = nombre
        self.contenido = contenido
        self.fecha_creacion = datetime.utcnow()

    def __repr__(self):
        return f'<Archivo {self.nombre}>'