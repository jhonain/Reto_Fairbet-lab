import hashlib
from .models import RegistroAuditoria

def _calcular_hash(hash_anterior, payload):
    base = (hash_anterior + payload).encode('utf-8')
    return hashlib.sha256(base).hexdigest()

def registrar_auditoria(evento, payload):
    ultimo = RegistroAuditoria.objects.order_by('fecha_creacion').last()
    hash_anterior = ultimo.hash_actual if ultimo else ''
    hash_actual = _calcular_hash(hash_anterior, payload)
    return RegistroAuditoria.objects.create(evento=evento, payload=payload, hash_anterior=hash_anterior, hash_actual=hash_actual)

def verificar_integridad():
    hash_anterior = ''
    for registro in RegistroAuditoria.objects.order_by('fecha_creacion'):
        esperado = _calcular_hash(hash_anterior, registro.payload)
        if registro.hash_actual != esperado:
            return (False, f'Cadena rota en el registro {registro.id}')
        hash_anterior = registro.hash_actual
    return (True, 'La cadena de auditoría es íntegra.')
