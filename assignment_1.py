import time
import random

def read_gragh_file(fileName):
    graph = {}
    num_vertices = 0
    num_edges = 0

    with open(fileName, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('c'):
                continue

            parts = line.split()

            if parts[0] == 'p':
                num_vertices = int(parts[2])
                num_edges = int(parts[3])
                graph = {i: [] for i in range(1, num_vertices+1)}

            elif parts[0] == 'e':
                u = int(parts[1])
                v = int(parts[2])
                graph[u].append(v)
                graph[v].append(u)

    return graph, num_vertices, num_edges


def createExtGraph(graph : dict, v_count : int) -> dict:
    tmp_graph = {}

    for item in graph.keys():
        tmp_graph[item] = [i for i in range(1, v_count+1) if i not in graph[item] and i != item]

    return tmp_graph


def largest_first_coloring(graph : dict):
    sorted_vertices = sorted(graph.keys(), key=lambda v: len(graph[v]), reverse=True)
    print(sorted_vertices)

    colors = {}
    available_colors = list(range(len(graph)))

    for vertex in sorted_vertices:
        used_colors = set()
        for neighbor in graph[vertex]:
            if neighbor in colors:
                used_colors.add(colors[neighbor])

        for color in available_colors:
            if color not in used_colors:
                colors[vertex] = color
                break

    return colors, len(set(colors.values()))


def swaps_same_degree_vertices(graph : dict, vertices : list, max_degree : int) -> list:
    if vertices:
        count_max_vertices = 0
        i_swaps = 0

        while i_swaps < len(vertices) and len(graph[vertices[i_swaps]]) == max_degree:
            if len(vertices) != 1:
                count_max_vertices += 1
                i_swaps += 1
            else:
                return vertices

        swaps = vertices[:i_swaps]

        ext_vertices = vertices[i_swaps:]

        random.shuffle(swaps)

        vertices = swaps + ext_vertices

        return vertices, count_max_vertices
    else:
        return []


def largest_first_cliques(graph : dict) -> list:
    vertices = list(graph.keys())

    cliques = []
    clique = []
    count_cliques = 0

    while vertices:
        vertices.sort(key=lambda x: len([v for v in graph[x] if v in vertices]), reverse=True)

        clique = []
        best_vertex = vertices[0]
        candidates_per_clique = [x for x in graph[best_vertex] if x in vertices]
        clique.append(best_vertex)

        while candidates_per_clique:

            best_vertex_per_clique = candidates_per_clique[0]
            clique.append(best_vertex_per_clique)
            candidates_per_clique = [x for x in candidates_per_clique if x in graph[best_vertex_per_clique]]

        cliques.append(clique)
        count_cliques += 1 
        vertices = [item for item in vertices if item not in clique]

    return cliques, count_cliques


def min_degree_clique(graph : dict) -> list:
    vertices = list(graph.keys())    

    cliques = []
    count_cliques = 0
    
    while vertices:

        vertices_per_clique = vertices.copy()

        while vertices_per_clique:
            is_clique = vertices_per_clique

            if check_clique(graph, is_clique):
                cliques.append(is_clique)
                count_cliques += 1
                vertices = [item for item in vertices if item not in is_clique]
                break
            else:
                min_vertex = find_vertex_w_min_degree(vertices_per_clique)
                vertices_per_clique.remove(min_vertex)

    return cliques, count_cliques
        

def check_clique(graph : dict, vertices : list) -> bool:
    for i in range(len(vertices)):
        for j in range(i+1, len(vertices)):
            if vertices[j] not in graph[vertices[i]]:
                return False
    return True


def check_coloring(graph: dict, coloring: list) -> bool:
    for color in coloring:
        for i, vertex1 in enumerate(color):
            for vertex2 in color[i+1:]: 
                if vertex2 in graph[vertex1]:
                    return False, color
    return True


def recursive_largest_first(graph: dict) -> list:
    """
    RLF алгоритм раскраски графа
    Возвращает список клик (раскраску)
    """
    coloring = []
    uncolored = set(graph.keys())
    
    while uncolored:
        # Шаг 1: Инициализация для нового цвета
        current_color_class = []
        available = uncolored.copy()
        
        # Множество вершин, смежных с уже выбранными в этом классе
        adjacent_to_current = set()
        
        while available:
            # Шаг 2: Выбор вершины с максимальным числом конфликтов в доступных
            best_vertex = None
            max_conflicts = -1
            
            for vertex in available:
                # Считаем количество соседей в доступных вершинах
                conflicts = len([n for n in graph[vertex] if n in available])
                
                if conflicts > max_conflicts:
                    max_conflicts = conflicts
                    best_vertex = vertex
                elif conflicts == max_conflicts:
                    # Tie-breaker: общая степень вершины
                    if len(graph[vertex]) > len(graph[best_vertex]):
                        best_vertex = vertex
            
            if best_vertex is None:
                break
                
            # Шаг 3: Добавляем вершину в текущий цвет
            current_color_class.append(best_vertex)
            available.remove(best_vertex)
            
            # Шаг 4: Обновляем множество смежных вершин
            adjacent_to_current.update(graph[best_vertex])
            
            # Шаг 5: Удаляем все смежные вершины из доступных
            available = available - adjacent_to_current
        
        # Добавляем построенный класс в раскраску
        coloring.append(current_color_class)
        uncolored = uncolored - set(current_color_class)
    
    return coloring


def find_vertex_w_min_degree(vertices : list) -> int:

    min_vertex = 0

    vertices.sort(key=lambda x: len([n for n in graph[x] if n in vertices]), reverse=True)

    min_vertex = vertices[-1]

    return min_vertex


def min_degree_first_clique_2(graph: dict) -> list:
    cliques = []
    
    # Создаем рабочие копии
    working_graph = {k: set(v) for k, v in graph.items()}
    vertices_and_degrees_origin = {v: len(neighbors) for v, neighbors in working_graph.items()}

    while vertices_and_degrees_origin:
        # Создаем копии для текущей итерации
        current_graph = {k: v.copy() for k, v in working_graph.items()}
        vertices_and_degrees = vertices_and_degrees_origin.copy()
        
        clique_found = False
        
        while vertices_and_degrees and not clique_found:
            
            # Находим вершину с минимальной степенью
            min_vertex = min(vertices_and_degrees, key=vertices_and_degrees.get)
            
            # Сохраняем соседей ДО изменений
            neighbors_of_min = current_graph[min_vertex].copy()
            
            # Удаляем min_vertex из графа и обновляем соседей
            for neighbor in neighbors_of_min:
                if neighbor in vertices_and_degrees:
                    vertices_and_degrees[neighbor] -= 1
                    current_graph[neighbor].discard(min_vertex)
            
            # Удаляем саму вершину
            del vertices_and_degrees[min_vertex]
            del current_graph[min_vertex]
            
            
            # Проверяем, является ли текущий набор кликой
            current_vertices = list(vertices_and_degrees.keys())
            
            if current_vertices and check_clique(current_graph, current_vertices):
                cliques.append(current_vertices.copy())
                # Удаляем вершины клики из origin
                for vertex in current_vertices:
                    if vertex in vertices_and_degrees_origin:
                        del vertices_and_degrees_origin[vertex]
                clique_found = True
        
        # Если клика не найдена в этой итерации, прерываем цикл
        if not clique_found:
            break
    
    return cliques



if __name__ == '__main__':

    graphs = ['myciel3.col',
                'myciel7.col',
                'school1.col',
                'school1_nsh.col',
                'anna.col',
                'miles1000.col',
                'miles1500.col',
                'le450_5a.col',
                'le450_15b.col',
                'queen11_11.col']
    
    reses = []
    
    results = {'name' : reses}

    for name in graphs:
        ext_graph = {}    

        start_t = time.time()

        graph, V, E = read_gragh_file(name)
        
        ext_graph = createExtGraph(graph, V)

        colors = largest_first_cliques(ext_graph)[0]

        count_of_colors = len(colors)

        end_t = time.time()

        execute_time = end_t - start_t

        reses.append(name)
        reses.append(execute_time)
        reses.append(count_of_colors)

        results[name] = reses

    
    print(reses)
    