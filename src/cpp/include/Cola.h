#ifndef COLA_H
#define COLA_H

#include <string>
#include <iostream>

// =====================================================================
// TDA COLA (Queue - FIFO) para la Ingesta de Datos (Scraping, PDF, CSV)
// Implementación manual basada en Nodos enlazados (Sin std::queue)
// =====================================================================

struct TareaIngesta {
    std::string tipo_fuente; // "URL_GRUPLAC", "URL_CVLAC", "ARCHIVO_PDF", "ARCHIVO_CSV"
    std::string ruta_o_url;  // URL de MinCiencias o ruta en disco
    std::string descripcion; // Breve descripción o alias de la tarea
};

struct NodoCola {
    TareaIngesta tarea;
    NodoCola* siguiente;

    NodoCola(const TareaIngesta& t, NodoCola* sig = nullptr)
        : tarea(t), siguiente(sig) {}
};

class Cola {
private:
    NodoCola* primero; // Frente de la cola (por donde se desencola)
    NodoCola* ultimo;  // Final de la cola (por donde se encola)
    int cantidad;

public:
    Cola() : primero(nullptr), ultimo(nullptr), cantidad(0) {}

    ~Cola() {
        liberar();
    }

    // Insertar al final de la cola (FIFO) - O(1)
    void encolar(const std::string& tipo, const std::string& ruta, const std::string& desc = "") {
        TareaIngesta t{tipo, ruta, desc};
        NodoCola* nuevo = new NodoCola(t);
        if (estaVacia()) {
            primero = ultimo = nuevo;
        } else {
            ultimo->siguiente = nuevo;
            ultimo = nuevo;
        }
        cantidad++;
    }

    // Extraer desde el frente de la cola - O(1)
    bool desencolar(TareaIngesta& salida) {
        if (estaVacia()) {
            return false;
        }
        NodoCola* temp = primero;
        salida = temp->tarea;
        primero = primero->siguiente;
        if (primero == nullptr) {
            ultimo = nullptr;
        }
        delete temp;
        cantidad--;
        return true;
    }

    // Consultar el elemento al frente sin extraerlo
    bool frente(TareaIngesta& salida) const {
        if (estaVacia()) return false;
        salida = primero->tarea;
        return true;
    }

    bool estaVacia() const {
        return primero == nullptr;
    }

    int tamano() const {
        return cantidad;
    }

    // Liberar toda la memoria
    void liberar() {
        while (primero != nullptr) {
            NodoCola* temp = primero;
            primero = primero->siguiente;
            delete temp;
        }
        ultimo = nullptr;
        cantidad = 0;
    }
};

#endif // COLA_H
