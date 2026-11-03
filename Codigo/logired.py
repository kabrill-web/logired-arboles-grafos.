"""
Sistema inteligente de rutas de distribución - LogiRed Colombia S.A.S.
Estructuras dinámicas no lineales: árbol n-ario (jerarquía) y grafo ponderado (rutas).

Autores: Jason Alfredo Castro Navarro y Karen Nayibe Abril Lozada
Asignatura: CDD-Estructura de Datos_G1_2026-3A - UCentral Virtual

Ejecución:
    python logired.py            -> menú interactivo
    python logired.py --pruebas  -> pruebas de la Fase 4
"""

import sys
import heapq
from collections import deque


# ===========================================================================
# PARTE 1. ÁRBOL JERÁRQUICO DE CENTROS DE DISTRIBUCIÓN
# ===========================================================================
class NodoCentro:
    """
    Nodo del árbol. Cada centro guarda sus datos y la lista de centros
    que dependen de él (sus hijos).
    - codigo: identificador del centro (ej. "CD01").
    - ciudad: nombre de la ciudad.
    - hijos: lista de NodoCentro. Se usa lista y no 'izquierdo/derecho'
      porque un centro puede tener más de dos dependientes
      (Bogotá tiene tres: Medellín, Cali y Barranquilla).
    """

    def __init__(self, codigo, ciudad):
        self.codigo = codigo
        self.ciudad = ciudad
        self.hijos = []

    def es_hoja(self):
        return len(self.hijos) == 0

    def __str__(self):
        return f"{self.codigo} - {self.ciudad}"


class ArbolCentros:
    """Árbol n-ario: una raíz (sede principal) y centros que dependen de otros."""

    def __init__(self):
        self.raiz = None

    # ----------------------------------------------------------- insertar --
    def insertar(self, codigo, ciudad, codigo_padre=None):
        """
        Inserta un centro como hijo de 'codigo_padre'.
        Si el árbol está vacío, el centro se vuelve la raíz.
        Devuelve True si se insertó y False si hubo un problema.
        """
        if self.buscar(codigo) is not None:
            print(f"  [!] El código {codigo} ya existe. No se insertó.")
            return False

        nuevo = NodoCentro(codigo, ciudad)

        if self.raiz is None:               # primer centro -> raíz
            self.raiz = nuevo
            return True

        padre = self.buscar(codigo_padre)
        if padre is None:
            print(f"  [!] No existe el centro padre {codigo_padre}. No se insertó.")
            return False

        padre.hijos.append(nuevo)           # se enlaza como nuevo dependiente
        return True

    # ------------------------------------------------------------- buscar --
    def buscar(self, dato):
        """
        Busca por código o por nombre de ciudad (sin importar mayúsculas).
        Usa recorrido en anchura: revisa nivel por nivel desde la raíz.
        Complejidad O(n) en el peor caso, porque el árbol no está ordenado.
        """
        if self.raiz is None or dato is None:
            return None
        dato = str(dato).strip().lower()
        cola = deque([self.raiz])
        while cola:
            actual = cola.popleft()
            if actual.codigo.lower() == dato or actual.ciudad.lower() == dato:
                return actual
            cola.extend(actual.hijos)
        return None

    def buscar_padre(self, codigo):
        """Devuelve el nodo padre de un centro (None si es la raíz o no existe)."""
        if self.raiz is None:
            return None
        cola = deque([self.raiz])
        while cola:
            actual = cola.popleft()
            for hijo in actual.hijos:
                if hijo.codigo == codigo:
                    return actual
                cola.append(hijo)
        return None

    def nivel(self, codigo):
        """Profundidad del centro: la raíz está en el nivel 0."""
        n = 0
        padre = self.buscar_padre(codigo)
        while padre is not None:
            n += 1
            padre = self.buscar_padre(padre.codigo)
        return n

    # ---------------------------------------------------------- recorridos --
    def preorden(self):
        """Raíz -> hijos (de izquierda a derecha). Muestra la cadena de mando."""
        resultado = []

        def visitar(nodo):
            if nodo is None:
                return
            resultado.append(nodo.ciudad)       # 1. primero el nodo
            for hijo in nodo.hijos:             # 2. luego cada subárbol
                visitar(hijo)

        visitar(self.raiz)
        return resultado

    def postorden(self):
        """Hijos -> raíz. Útil para consolidar información de abajo hacia arriba."""
        resultado = []

        def visitar(nodo):
            if nodo is None:
                return
            for hijo in nodo.hijos:             # 1. primero los subárboles
                visitar(hijo)
            resultado.append(nodo.ciudad)       # 2. al final el nodo

        visitar(self.raiz)
        return resultado

    def anchura(self):
        """Nivel por nivel con una cola (FIFO). Muestra los niveles de la jerarquía."""
        resultado = []
        if self.raiz is None:
            return resultado
        cola = deque([self.raiz])
        while cola:
            actual = cola.popleft()
            resultado.append(actual.ciudad)
            cola.extend(actual.hijos)           # los hijos esperan su turno
        return resultado

    # ------------------------------------------------------------- contar --
    def contar_nodos(self, nodo="inicio"):
        """Cuenta recursivamente: 1 (el nodo) + lo que haya en cada subárbol."""
        if nodo == "inicio":
            nodo = self.raiz
        if nodo is None:
            return 0
        return 1 + sum(self.contar_nodos(h) for h in nodo.hijos)

    def clasificar_nodos(self):
        """Devuelve (raíz, internos, hojas) para el análisis del diseño."""
        internos, hojas = [], []
        if self.raiz is None:
            return None, internos, hojas
        cola = deque([self.raiz])
        while cola:
            actual = cola.popleft()
            if actual is not self.raiz:
                (hojas if actual.es_hoja() else internos).append(actual.ciudad)
            cola.extend(actual.hijos)
        return self.raiz.ciudad, internos, hojas

    def altura(self, nodo="inicio"):
        """Número de niveles del árbol (un árbol de un solo nodo tiene altura 1)."""
        if nodo == "inicio":
            nodo = self.raiz
        if nodo is None:
            return 0
        return 1 + max((self.altura(h) for h in nodo.hijos), default=0)

    # ------------------------------------------------------------ mostrar --
    def mostrar(self):
        """Dibuja el árbol en la consola con ramas, como en la guía."""
        if self.raiz is None:
            print("  (árbol vacío)")
            return
        print(f"  {self.raiz}")

        def dibujar(nodo, prefijo):
            for i, hijo in enumerate(nodo.hijos):
                ultimo = i == len(nodo.hijos) - 1
                print(f"  {prefijo}{'└── ' if ultimo else '├── '}{hijo}")
                dibujar(hijo, prefijo + ("    " if ultimo else "│   "))

        dibujar(self.raiz, "")


# ===========================================================================
# PARTE 2. GRAFO PONDERADO DE CONEXIONES LOGÍSTICAS
# ===========================================================================
class GrafoRutas:
    """
    Grafo no dirigido y ponderado, guardado como LISTA DE ADYACENCIA:
        { "Bogotá": {"Medellín": 415, "Cali": 460, ...}, ... }
    - Vértices: ciudades.
    - Aristas: carreteras con su distancia en km (el peso).
    Es no dirigido porque una vía se puede recorrer en los dos sentidos.
    Se eligió lista de adyacencia (y no matriz) porque la red es dispersa:
    cada ciudad se conecta con pocas otras, así se ahorra memoria.
    """

    def __init__(self):
        self.adyacencia = {}

    def agregar_ciudad(self, ciudad):
        if ciudad not in self.adyacencia:
            self.adyacencia[ciudad] = {}

    def agregar_conexion(self, origen, destino, distancia):
        """Agrega la arista en los dos sentidos. Valida que la distancia sea positiva."""
        if origen == destino:
            print("  [!] Origen y destino no pueden ser la misma ciudad.")
            return False
        if distancia <= 0:
            print("  [!] La distancia debe ser mayor que cero.")
            return False
        self.agregar_ciudad(origen)
        self.agregar_ciudad(destino)
        self.adyacencia[origen][destino] = distancia
        self.adyacencia[destino][origen] = distancia
        return True

    def ciudades_conectadas(self, ciudad):
        """Vecinos directos de una ciudad con su distancia."""
        return dict(self.adyacencia.get(ciudad, {}))

    def numero_aristas(self):
        return sum(len(v) for v in self.adyacencia.values()) // 2

    def aristas(self):
        """Lista cada conexión una sola vez (sin repetir A-B y B-A)."""
        vistas, lista = set(), []
        for origen, vecinos in self.adyacencia.items():
            for destino, km in vecinos.items():
                clave = frozenset((origen, destino))
                if clave not in vistas:
                    vistas.add(clave)
                    lista.append((origen, destino, km))
        return lista

    def mostrar(self):
        """Muestra la lista de adyacencia."""
        for ciudad, vecinos in self.adyacencia.items():
            texto = ", ".join(f"{v} ({km} km)" for v, km in vecinos.items())
            print(f"  {ciudad:<13} -> {texto}")

    # ------------------------------------------------- rutas disponibles --
    def rutas_disponibles(self, origen, destino):
        """
        Encuentra TODAS las rutas simples (sin repetir ciudades) entre dos
        ciudades con búsqueda en profundidad (DFS) y backtracking.
        Devuelve una lista de (distancia_total, [ciudades]) ordenada de menor a mayor.
        """
        if origen not in self.adyacencia or destino not in self.adyacencia:
            return []
        rutas = []

        def dfs(actual, camino, km):
            if actual == destino:
                rutas.append((km, list(camino)))
                return
            for vecino, peso in self.adyacencia[actual].items():
                if vecino not in camino:          # evita ciclos
                    camino.append(vecino)
                    dfs(vecino, camino, km + peso)
                    camino.pop()                  # backtracking

        dfs(origen, [origen], 0)
        return sorted(rutas)

    # ----------------------------------------------------------- Dijkstra --
    def dijkstra(self, origen, destino):
        """
        Ruta de menor distancia con el algoritmo de Dijkstra.
        - distancia: mejor distancia conocida desde el origen a cada ciudad.
        - anterior: de qué ciudad se llegó, para reconstruir el camino.
        - cola de prioridad (heapq): siempre saca la ciudad más cercana pendiente.
        Complejidad O((V + E) log V).
        Devuelve (distancia_total, [ciudades]) o (inf, []) si no hay camino.
        """
        if origen not in self.adyacencia or destino not in self.adyacencia:
            return float("inf"), []

        distancia = {c: float("inf") for c in self.adyacencia}
        anterior = {c: None for c in self.adyacencia}
        distancia[origen] = 0
        cola = [(0, origen)]
        visitados = set()

        while cola:
            dist_actual, actual = heapq.heappop(cola)
            if actual in visitados:            # ya tenía una distancia mejor
                continue
            visitados.add(actual)
            if actual == destino:              # se puede parar al llegar
                break
            for vecino, peso in self.adyacencia[actual].items():
                nueva = dist_actual + peso
                if nueva < distancia[vecino]:  # relajación de la arista
                    distancia[vecino] = nueva
                    anterior[vecino] = actual
                    heapq.heappush(cola, (nueva, vecino))

        if distancia[destino] == float("inf"):
            return float("inf"), []

        camino, paso = [], destino              # se reconstruye de atrás hacia adelante
        while paso is not None:
            camino.append(paso)
            paso = anterior[paso]
        return distancia[destino], camino[::-1]


# ===========================================================================
# PARTE 3. SISTEMA: une el árbol y el grafo
# ===========================================================================
class SistemaLogiRed:
    def __init__(self):
        self.arbol = ArbolCentros()
        self.grafo = GrafoRutas()

    def nombre_ciudad(self, dato):
        """Permite escribir el código (CD02) o el nombre (Medellín)."""
        nodo = self.arbol.buscar(dato)
        if nodo:
            return nodo.ciudad
        for ciudad in self.grafo.adyacencia:
            if ciudad.lower() == str(dato).strip().lower():
                return ciudad
        return None

    def cargar_datos_iniciales(self):
        """Datos suministrados en la guía."""
        jerarquia = [
            ("CD01", "Bogotá", None),
            ("CD02", "Medellín", "CD01"),
            ("CD06", "Pereira", "CD02"),
            ("CD05", "Bucaramanga", "CD02"),
            ("CD03", "Cali", "CD01"),
            ("CD04", "Barranquilla", "CD01"),
            ("CD07", "Cartagena", "CD04"),
        ]
        for codigo, ciudad, padre in jerarquia:
            self.arbol.insertar(codigo, ciudad, padre)

        conexiones = [
            ("Bogotá", "Medellín", 415), ("Bogotá", "Cali", 460),
            ("Bogotá", "Bucaramanga", 397), ("Medellín", "Pereira", 214),
            ("Medellín", "Cartagena", 643), ("Cali", "Pereira", 210),
            ("Barranquilla", "Cartagena", 120), ("Bucaramanga", "Barranquilla", 535),
            ("Cartagena", "Cali", 1180),
        ]
        for o, d, km in conexiones:
            self.grafo.agregar_conexion(o, d, km)

    # ---------------------------------------------------- salidas comunes --
    def imprimir_recorridos(self):
        print(f"  Preorden : {' -> '.join(self.arbol.preorden())}")
        print(f"  Postorden: {' -> '.join(self.arbol.postorden())}")
        print(f"  Anchura  : {' -> '.join(self.arbol.anchura())}")

    def imprimir_resumen_arbol(self):
        raiz, internos, hojas = self.arbol.clasificar_nodos()
        print(f"  Raíz          : {raiz}")
        print(f"  Nodos internos: {', '.join(internos)}")
        print(f"  Hojas         : {', '.join(hojas)}")
        print(f"  Total de nodos: {self.arbol.contar_nodos()}   |   Altura: {self.arbol.altura()} niveles")

    def imprimir_consulta(self, dato):
        nodo = self.arbol.buscar(dato)
        if nodo is None:
            print(f"  Buscar '{dato}': no existe en la jerarquía.")
            return
        padre = self.arbol.buscar_padre(nodo.codigo)
        hijos = ", ".join(h.ciudad for h in nodo.hijos) or "ninguno (hoja)"
        vecinos = self.grafo.ciudades_conectadas(nodo.ciudad)
        conex = ", ".join(f"{v} ({km} km)" for v, km in vecinos.items()) or "sin conexiones"
        print(f"  Buscar '{dato}': {nodo}")
        print(f"     Depende de : {padre if padre else '(es la raíz)'}   |   Nivel: {self.arbol.nivel(nodo.codigo)}")
        print(f"     Dependientes: {hijos}")
        print(f"     Conexiones  : {conex}")

    def imprimir_rutas(self, origen, destino, max_rutas=None):
        rutas = self.grafo.rutas_disponibles(origen, destino)
        print(f"  Rutas disponibles {origen} -> {destino}: {len(rutas)}")
        for i, (km, camino) in enumerate(rutas[:max_rutas] if max_rutas else rutas, 1):
            print(f"    {i:>2}. {' -> '.join(camino)}  = {km} km")
        if max_rutas and len(rutas) > max_rutas:
            resto = len(rutas) - max_rutas
            print(f"    ... y {resto} {'ruta más larga' if resto == 1 else 'rutas más largas'}")
        km, camino = self.grafo.dijkstra(origen, destino)
        if camino:
            print(f"  Dijkstra (menor distancia): {' -> '.join(camino)} = {km} km")
        else:
            print("  Dijkstra: no hay camino entre esas ciudades.")


# ===========================================================================
# PRUEBAS DE LA FASE 4
# ===========================================================================
def linea(titulo):
    print("\n" + "=" * 74)
    print(f" {titulo}")
    print("=" * 74)


def ejecutar_pruebas():
    s = SistemaLogiRed()
    s.cargar_datos_iniciales()

    linea("ESTADO INICIAL - Árbol jerárquico y grafo de la guía")
    s.arbol.mostrar()
    print()
    s.imprimir_resumen_arbol()
    print(f"\n  Grafo: {len(s.grafo.adyacencia)} vértices y {s.grafo.numero_aristas()} aristas")
    s.grafo.mostrar()

    linea("PRUEBA 1 - Insertar Manizales (CD08) y Santa Marta (CD09)")
    print("  Criterio: cada centro depende del centro existente con el que tiene")
    print("  conexión logística directa (el más cercano en la red de la guía).")
    s.arbol.insertar("CD08", "Manizales", "CD06")
    print("  [OK] CD08 Manizales insertado como hijo de CD06 Pereira (52 km)")
    s.arbol.insertar("CD09", "Santa Marta", "CD07")
    print("  [OK] CD09 Santa Marta insertado como hijo de CD07 Cartagena (240 km)")
    s.grafo.agregar_conexion("Pereira", "Manizales", 52)
    s.grafo.agregar_conexion("Cartagena", "Santa Marta", 240)
    print("  [OK] Conexiones agregadas: Pereira-Manizales (52 km), Cartagena-Santa Marta (240 km)")
    print("\n  Validaciones:")
    s.arbol.insertar("CD08", "Manizales", "CD06")
    s.arbol.insertar("CD10", "Tunja", "CD99")
    s.grafo.agregar_conexion("Cali", "Cali", 10)
    print()
    s.arbol.mostrar()

    linea("PRUEBA 2 - Consulta de centros")
    for dato in ["CD08", "Santa Marta", "medellín", "CD01", "CD15"]:
        s.imprimir_consulta(dato)
    print(f"\n  Total de nodos: {s.arbol.contar_nodos()}")

    linea("PRUEBA 3 - Recorridos del árbol actualizado")
    s.imprimir_recorridos()
    print()
    s.imprimir_resumen_arbol()

    linea("PRUEBA 4 - Grafo actualizado (lista de adyacencia)")
    print(f"  {len(s.grafo.adyacencia)} vértices y {s.grafo.numero_aristas()} aristas\n")
    s.grafo.mostrar()

    linea("PRUEBA 5 - Análisis de rutas con Dijkstra")
    for o, d in [("Bogotá", "Cartagena"), ("Bogotá", "Manizales"),
                 ("Cali", "Barranquilla"), ("Bogotá", "Santa Marta")]:
        s.imprimir_rutas(o, d, max_rutas=4)
        print()


# ===========================================================================
# MENÚ INTERACTIVO
# ===========================================================================
def pedir(texto):
    return input(f"  {texto}").strip()


def menu():
    s = SistemaLogiRed()
    s.cargar_datos_iniciales()
    opciones = """
  ================= LogiRed Colombia S.A.S. =================
   ÁRBOL (jerarquía)              GRAFO (rutas)
   1. Mostrar árbol               6. Mostrar grafo
   2. Insertar centro             7. Agregar conexión
   3. Buscar centro               8. Ciudades conectadas
   4. Recorridos                  9. Rutas disponibles + Dijkstra
   5. Contar nodos
   0. Salir
  ============================================================"""
    while True:
        print(opciones)
        op = pedir("Opción: ")
        if op == "1":
            s.arbol.mostrar()
        elif op == "2":
            codigo = pedir("Código (ej. CD10): ").upper()
            ciudad = pedir("Ciudad: ")
            padre = pedir("Código del centro padre: ").upper()
            if s.arbol.insertar(codigo, ciudad, padre):
                print(f"  [OK] {codigo} {ciudad} insertado bajo {padre}.")
        elif op == "3":
            s.imprimir_consulta(pedir("Código o ciudad: "))
        elif op == "4":
            s.imprimir_recorridos()
        elif op == "5":
            s.imprimir_resumen_arbol()
        elif op == "6":
            s.grafo.mostrar()
        elif op == "7":
            o = s.nombre_ciudad(pedir("Origen: ")) or "?"
            d = s.nombre_ciudad(pedir("Destino: ")) or "?"
            try:
                km = int(pedir("Distancia (km): "))
            except ValueError:
                print("  [!] La distancia debe ser un número entero.")
                continue
            if "?" in (o, d):
                print("  [!] Las dos ciudades deben existir en la jerarquía o en la red.")
            elif s.grafo.agregar_conexion(o, d, km):
                print(f"  [OK] Conexión {o} - {d} ({km} km) agregada.")
        elif op == "8":
            c = s.nombre_ciudad(pedir("Ciudad: "))
            vecinos = s.grafo.ciudades_conectadas(c) if c else {}
            if vecinos:
                for v, km in vecinos.items():
                    print(f"   - {v}: {km} km")
            else:
                print("  [!] Ciudad sin conexiones o inexistente.")
        elif op == "9":
            o = s.nombre_ciudad(pedir("Origen: "))
            d = s.nombre_ciudad(pedir("Destino: "))
            if o and d:
                s.imprimir_rutas(o, d)
            else:
                print("  [!] Ciudad no encontrada.")
        elif op == "0":
            print("  Hasta luego.")
            break
        else:
            print("  [!] Opción no válida.")


if __name__ == "__main__":
    if "--pruebas" in sys.argv:
        ejecutar_pruebas()
    else:
        menu()
