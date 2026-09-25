#ifndef PILA_H
#define PILA_H

#include <string>
#include <iostream>

// =====================================================================
// TDA PILA (Stack - LIFO) para el Historial de Acciones y Función Deshacer
// Implementación manual basada en Nodos enlazados (Sin std::stack)
// =====================================================================

struct AccionHistorial {
    std::string tipo_operacion; // "CREAR", "MODIFICAR", "DESACTIVAR", "ELIMINAR"
    std::string tipo_entidad;   // "GRUPO", "INVESTIGADOR", "PRODUCTO"
    std::string id_registro;    // Clave primaria del registro afectado
    std::string detalle_previo; // Estado anterior para reversión (ej. "activo=1")
};

struct NodoPila {
    AccionHistorial accion;
    NodoPila* siguiente;

    NodoPila(const AccionHistorial& acc, NodoPila* sig = nullptr)
        : accion(acc), siguiente(sig) {}
};

class Pila {
private:
    NodoPila* cima;
    int cantidad;

public:
    Pila() : cima(nullptr), cantidad(0) {}

    ~Pila() {
        liberar();
    }

    // Insertar acción en el tope de la pila (LIFO) - O(1)
    void push(const std::string& op, const std::string& entidad,
              const std::string& id, const std::string& detalle = "") {
        AccionHistorial acc{op, entidad, id, detalle};
        NodoPila* nuevo = new NodoPila(acc, cima);
        cima = nuevo;
        cantidad++;
    }

    // Extraer la última acción realizada - O(1)
    bool pop(AccionHistorial& salida) {
        if (estaVacia()) {
            return false;
        }
        NodoPila* temp = cima;
        salida = temp->accion;
        cima = cima->siguiente;
        delete temp;
        cantidad--;
        return true;
    }

    // Consultar el tope sin extraerlo
    bool top(AccionHistorial& salida) const {
        if (estaVacia()) return false;
        salida = cima->accion;
        return true;
    }

    bool estaVacia() const {
        return cima == nullptr;
    }

    int tamano() const {
        return cantidad;
    }

    // Liberar toda la memoria asignada
    void liberar() {
        while (cima != nullptr) {
            NodoPila* temp = cima;
            cima = cima->siguiente;
            delete temp;
        }
        cantidad = 0;
    }
};

#endif // PILA_H
