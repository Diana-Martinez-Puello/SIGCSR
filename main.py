import logging
from abc import ABC, abstractmethod

# Configuracion del sistema de registros logs
logging.basicConfig(
    filename='sistema_errores.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# manejo avanzado de exepciones
class SistemaError(Exception):
    pass

class DatosInvalidosError(SistemaError):
   pass

class OperacionNoPermitidaError(SistemaError):
    pass

class ServicioNoDisponibleError(SistemaError):
    pass

# Entidades base y clases abstractas 
class EntidadGeneral(ABC):
    @abstractmethod
    def validar_estado(self):
        pass

class Cliente(EntidadGeneral):
     def __init__(self, identificacion, nombre, correo):
        self.__identificacion = identificacion
        self.__nombre = nombre
        self.__correo = correo
        self.validar_estado()

    # Getters para acceder de forma segura
    def get_identificacion(self):
        return self.__identificacion

    def get_nombre(self):
        return self.__nombre

    def validar_estado(self):
        if not self.__identificacion or not self.__nombre or "@" not in self.__correo:
            raise DatosInvalidosError(f"Datos de cliente inválidos: {self.__nombre}")
            
    def __str__(self):
        return f"{self.__nombre} (ID: {self.__identificacion})"

class Servicio(EntidadGeneral):
    def __init__(self, codigo, nombre, tarifa_base):
        self._codigo = codigo
        self._nombre = nombre
        self._tarifa_base = tarifa_base
        self.validar_estado()
     

    def validar_estado(self):
        if self._tarifa_base < 0:
            raise DatosInvalidosError

    @abstractmethod
    def calcular_costo(self, cantidad):
        pass

    @abstractmethod
    def obtener_descripcion(self):
        pass

# POLIMORFISMO
class ReservaSalas(Servicio):
    def __init__(self, codigo, nombre, tarifa_base, capacidad):
        super().__init__(codigo, nombre, tarifa_base)
        self.capacidad = capacidad

    def calcular_costo(self, horas):
        return self._tarifa_base * horas

    def obtener_descripcion(self):
        return f"Sala '{self._nombre}' para {self.capacidad} personas."

class AlquilerEquipos(Servicio):
    def __init__(self, codigo, nombre, tarifa_base, requiere_seguro):
        super().__init__(codigo, nombre, tarifa_base)
        self.requiere_seguro = requiere_seguro

    def calcular_costo(self, dias):
        costo = self._tarifa_base * dias
        if self.requiere_seguro:
            costo += 50.0  # Cargo fijo por seguro
        return costo

    def obtener_descripcion(self):
        seguro = "con seguro" if self.requiere_seguro else "sin seguro"
        return f"Equipo '{self._nombre}' ({seguro})."

class AsesoriaEspecializada(Servicio):
    def __init__(self, codigo, nombre, tarifa_base, area_experiencia):
        super().__init__(codigo, nombre, tarifa_base)
        self.area_experiencia = area_experiencia

    def calcular_costo(self, sesiones):
        # 10% de descuento si se contratan más de 3 sesiones
        costo = self._tarifa_base * sesiones
        if sesiones > 3:
            costo *= 0.9 
        return costo

    def obtener_descripcion(self):
        return f"Asesoría en {self.area_experiencia} - {self._nombre}."

# Gestion de reservas y metodos sobrecargados
class Reserva:
    def __init__(self, id_reserva, cliente, servicio, duracion):
        if not isinstance(cliente, Cliente):
            raise DatosInvalidosError("El cliente proporcionado no es válido.")
        if not isinstance(servicio, Servicio):
            raise ServicioNoDisponibleError("El servicio proporcionado no es válido.")
            
        self.id_reserva = id_reserva
        self.cliente = cliente
        self.servicio = servicio
        self.duracion = duracion
        self.estado = "Pendiente"
        
   
    def calcular_total(self, aplicar_impuesto=False, porcentaje_descuento=0.0):
       try:
            subtotal = self.servicio.calcular_costo(self.duracion)
            if porcentaje_descuento > 0:
                subtotal -= subtotal * (porcentaje_descuento / 100)
            if aplicar_impuesto:
                subtotal *= 1.19  # 19% IVA
            return round(subtotal, 2)
        except Exception as e:
            # Encadenamiento de excepciones
            raise OperacionNoPermitidaError("Fallo al calcular el total") from e

    def confirmar(self):
        if self.estado == "Confirmada":
            raise OperacionNoPermitidaError("La reserva ya esta confirmada.")
        self.estado = "Confirmada"
        print(f"Reserva {self.id_reserva} confirmada para {self.cliente.get_nombre()}.")

    def cancelar(self):
        if self.estado == "Cancelada":
            raise OperacionNoPermitidaError("La reserva ya fue cancelada")
        self.estado = "Cancelada"
        print(f"Reserva {self.id_reserva} ha sido cancelada.")


# 10 OPERACIONES
def ejecutar_simulacion():
    print("- INICIANDO SIMULACIÓN DE SOFTWARE FJ -\n")
    
    # Operación valida: Crear Cliente
    try:
        c1 = Cliente("1001", "Diana Martinez", "diana123@gmail.com")
        print("Cliente valido creado.")
    except Exception as e:
        logging.error(e)

    # Operación invalida: Cliente con datos faltantes
    try:
        c2 = Cliente("", "Carolina Puello", "caro.com")
    except DatosInvalidosError as e:
        logging.error(f"Operación 2 fallida: {e}")
        print(f"Error manejado correctamente: {e}")
    else:
        print("2. Cliente creado exitosamente")
    finally:
        print("   -> Bloque finally: Finalizando intento de registro de cliente 2.")

    # Operación valida: Crear Servicio de Salas
    s_sala = ReservaSalas("S01", "Sala VIP", 100.0, 15)
    print("Servicio de Sala creado.")

    # Operación valida: Crear Servicio de Equipos
    s_equipo = AlquilerEquipos("E01", "Proyector 4K", 30.0, True)
    print("Servicio de Equipo creado.")

    # Operación valida: Crear Servicio de Asesoria
    s_asesoria = AsesoriaEspecializada("A01", "Consultoría DB", 200.0, "Bases de Datos")
    print("Servicio de Asesoria creado.")

    # Operación invalida: Servicio con tarifa negativa
    try:
        s_invalido = ReservaSalas("S02", "Sala Rota", -50.0, 5)
    except DatosInvalidosError as e:
        logging.error(f"Operación 6 fallida: {e}")
        print(f"Error capturado al crear servicio: {e}")

    # Operación valida: Reserva exitosa y confirmación
    try:
        r1 = Reserva("R-001", c1, s_sala, 4)
        r1.confirmar()
        print(f"Reserva exitosa. Total con impuestos: ${r1.calcular_total(aplicar_impuesto=True)}")
    except Exception as e:
        logging.error(e)

    # Operación invalida: Intentar confirmar una reserva ya confirmada
    try:
        r1.confirmar()
    except OperacionNoPermitidaError as e:
        logging.error(f"Operación 8 fallida: {e}")
        print(f"Prevencion de doble confirmación: {e}")

    # Operación invalida: Reserva con servicio nulo/invalido
    try:
        r_falla = Reserva("R-002", c1, None, 2)
    except ServicioNoDisponibleError as e:
        logging.error(f"Operación 9 fallida: {e}")
        print(f"9. Error al crear reserva sin servicio: {e}")

    # Operación valida: Cancelación de reserva
    try:
        r2 = Reserva("R-003", c1, s_asesoria, 5)
        print(f"Reserva de asesoría creada (Total con descuento: ${r2.calcular_total(porcentaje_descuento=15)})")
        r2.cancelar()
    except Exception as e:
        logging.error(e)

    print("\n-SIMULACION FINALIZADA.")

if __name__ == "__main__":
    ejecutar_simulacion()
