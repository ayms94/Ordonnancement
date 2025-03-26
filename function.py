# -*- coding: utf-8 -*-
"""
fonctions.py
------------
Ce fichier contient toutes les fonctions nécessaires pour :
 - Lire et stocker les tâches depuis un fichier .txt
 - Afficher le tableau de contraintes
 - Construire et afficher la matrice d’adjacence
 - Vérifier la présence d’arcs négatifs
 - Détecter la présence d’un circuit (via un tri topologique ou élimination des points d’entrée)
 - Calculer les rangs des tâches
 - Calculer les dates au plus tôt et au plus tard
 - Calculer les marges
 - Identifier et afficher les chemins critiques

Auteur : Votre équipe
Année : 2024/2025
"""

from prettytable import PrettyTable
import collections

def read_constraints_from_file(filename):
    """
    Lit un fichier .txt dont chaque ligne a le format :
        numéro_tâche durée [prédécesseur1 prédécesseur2 ...]
    Renvoie une liste de tuples : [(task_id, duration, [preds]), ...].
    """
    tasks = []
    with open(filename, 'r') as file:
        for line in file:
            parts = line.strip().split()
            if len(parts) >= 2:
                t_id = int(parts[0])
                dur = int(parts[1])
                preds = [int(x) for x in parts[2:]] if len(parts) > 2 else []
                tasks.append((t_id, dur, preds))
    return tasks

def count_vertices(tasks):
    """
    Calcule le nombre total de sommets (tâches + 2 sommets fictifs α et ω).
    """
    return len(tasks) + 2

def count_arcs(tasks):
    """
    Calcule le nombre total d’arcs :
     - arcs issus des prédécesseurs vers chaque tâche
     - arcs depuis α pour les tâches sans prédécesseurs
     - arcs vers ω pour les tâches sans successeurs
    """
    arcs = 0
    all_tasks = set()
    has_preds = set()

    for (t_id, _, preds) in tasks:
        all_tasks.add(t_id)
        if preds:
            arcs += len(preds)  # un arc par prédécesseur
            has_preds.update(preds)
        else:
            # Si pas de prédécesseur, alors arc depuis α
            arcs += 1

    # Les tâches sans successeurs
    tasks_with_succ = set()
    for (t_id, _, preds) in tasks:
        for p in preds:
            tasks_with_succ.add(p)
    tasks_no_succ = all_tasks - tasks_with_succ
    # Chacune de ces tâches a un arc vers ω
    arcs += len(tasks_no_succ)

    return arcs

def show_constraints_overview(tasks):
    """
    Affiche un tableau récapitulatif (tâche, durée, prédécesseurs) et
    indique le nombre de sommets et d’arcs.
    """
    nb_sommets = count_vertices(tasks)
    nb_arcs = count_arcs(tasks)
    print(f"Le tableau de contraintes contient :")
    print(f" - {nb_sommets} sommets (y compris α=0 et ω={nb_sommets-1})")
    print(f" - {nb_arcs} arcs")

    table = PrettyTable()
    table.field_names = ["Tâche", "Durée", "Prédécesseurs"]
    for (t_id, dur, preds) in tasks:
        preds_str = ", ".join(str(p) for p in preds) if preds else "Aucun"
        table.add_row([f"{t_id}", f"{dur}", preds_str])
    print("\nTableau de contraintes :")
    print(table)

def show_arcs(tasks):
    """
    Affiche la liste des arcs sous forme :
       0 -> Tâche = 0
       Pred -> Tâche = durée_pred
       Tâche -> ω = durée_tâche
    pour illustrer la création du graphe d’ordonnancement.
    """
    all_tasks = set(t[0] for t in tasks)
    # Récupération de l'ID du sommet ω
    omega = max(all_tasks) + 1

    print("\n* Création du graphe d’ordonnancement :")
    # Arcs depuis α ou depuis un prédécesseur
    for (t_id, dur, preds) in tasks:
        if not preds:
            # Arc depuis α (0)
            print(f"0 -> {t_id} = 0")
        else:
            # Arc depuis chaque prédécesseur
            for p in preds:
                # durée du prédécesseur = tasks[p - 1][1] si p démarre à 1
                # Vérification d'index : p - 1 si p commence à 1
                pred_duration = next((d for (tid, d, _) in tasks if tid == p), None)
                if pred_duration is not None:
                    print(f"{p} -> {t_id} = {pred_duration}")
                else:
                    print(f"Attention : prédécesseur {p} introuvable pour la tâche {t_id}")

    # Arcs vers ω
    # Tâches sans successeurs
    tasks_with_preds = set()
    for (_, _, preds) in tasks:
        tasks_with_preds.update(preds)
    no_succ = all_tasks - tasks_with_preds
    for t_id, dur, _ in tasks:
        if t_id in no_succ:
            print(f"{t_id} -> {omega} = {dur}")

def build_adjacency_matrix(tasks):
    """
    Construit et renvoie la matrice d’adjacence sous forme de liste de listes,
    en marquant les absences d’arc par '*'.
    """
    nb_sommets = len(tasks) + 2
    omega = nb_sommets - 1

    # Initialisation
    matrix = [["*" for _ in range(nb_sommets)] for _ in range(nb_sommets)]

    # Placement des arcs
    for (t_id, dur, preds) in tasks:
        if not preds:
            # Arc depuis α (0)
            matrix[0][t_id] = 0
        else:
            for p in preds:
                # durée du prédécesseur
                pred_duration = next((d for (tid, d, _) in tasks if tid == p), None)
                if pred_duration is not None:
                    matrix[p][t_id] = pred_duration

    # Arcs vers ω
    all_tasks = set(t[0] for t in tasks)
    tasks_with_preds = set()
    for (_, _, preds) in tasks:
        tasks_with_preds.update(preds)
    no_succ = all_tasks - tasks_with_preds
    for (t_id, dur, _) in tasks:
        if t_id in no_succ:
            matrix[t_id][omega] = dur

    return matrix

def show_adjacency_matrix(matrix):
    """
    Affiche la matrice d’adjacence avec PrettyTable, en remplaçant
    les valeurs None ou '*' par '*'.
    """
    nb_sommets = len(matrix)
    pt = PrettyTable()
    # En-têtes de colonnes : 0, 1, 2, ..., nb_sommets-1
    headers = [" "] + [str(i) for i in range(nb_sommets)]
    pt.field_names = headers

    for i in range(nb_sommets):
        row = [str(i)] + [str(matrix[i][j]) for j in range(nb_sommets)]
        pt.add_row(row)

    print("\nMatrice d’adjacence :")
    print(pt)

def has_negative_arcs(tasks):
    """
    Vérifie si une tâche a une durée négative.
    Retourne True si au moins un arc négatif est détecté.
    """
    for (_, duration, _) in tasks:
        if duration < 0:
            print("-> Au moins un arc a une durée négative !")
            return True
    print("-> Aucun arc négatif détecté.")
    return False

def detect_cycle(matrix):
    """
    Détection de circuit par la méthode du tri topologique (Kahn).
    Retourne True s’il y a un cycle, False sinon.
    """
    n = len(matrix)
    # Calcul du degré entrant
    in_degree = [0]*n
    for i in range(n):
        for j in range(n):
            if matrix[i][j] != "*":
                # On considère qu’il y a un arc i->j
                in_degree[j] += 1

    # Recherche des points d’entrée (degré entrant = 0)
    queue = [i for i in range(n) if in_degree[i] == 0]
    count_visited = 0

    while queue:
        u = queue.pop(0)
        count_visited += 1
        # Pour chaque voisin v de u
        for v in range(n):
            if matrix[u][v] != "*":
                in_degree[v] -= 1
                if in_degree[v] == 0:
                    queue.append(v)

    if count_visited < n:
        print("-> Un circuit a été détecté !")
        return True
    else:
        print("-> Aucun circuit détecté.")
        return False

def assign_ranks(tasks):
    """
    Calcule le rang de chaque sommet (0 étant le rang de α,
    ω étant le dernier).
    Retourne un dictionnaire {sommet: rang}.
    """
    ranks = {}
    # 0 : rang 0
    ranks[0] = 0
    # On initialise les rangs des tâches et de ω à 0
    for (t_id, _, _) in tasks:
        ranks[t_id] = 0
    omega = max(ranks.keys()) + 1
    ranks[omega] = 0

    # On itère jusqu’à stabilisation
    changed = True
    while changed:
        changed = False
        for (t_id, _, preds) in tasks:
            if preds:
                # Le rang de la tâche = 1 + max(rang de ses prédécesseurs)
                max_pred_rank = max(ranks[p] for p in preds)
                new_rank = max_pred_rank + 1
                if new_rank > ranks[t_id]:
                    ranks[t_id] = new_rank
                    changed = True
            else:
                # S’il n’y a pas de prédécesseurs et que ce n’est pas α
                if t_id != 0 and ranks[t_id] == 0:
                    ranks[t_id] = 1
                    changed = True
        # Mise à jour du rang de ω
        current_omega_rank = max(ranks[t] for t in ranks if t != omega) + 1
        if current_omega_rank != ranks[omega]:
            ranks[omega] = current_omega_rank
            changed = True

    # Tri par clé pour l’affichage
    ordered = collections.OrderedDict(sorted(ranks.items()))
    return ordered

def compute_schedules(tasks, ranks):
    """
    Calcule les dates au plus tôt et au plus tard pour chaque sommet.
    Retourne deux dictionnaires : earliest[sommet], latest[sommet].
    """
    earliest = {}
    latest = {}
    # Le sommet α (0) commence à 0
    earliest[0] = 0
    # Identifiant de ω
    omega = max(ranks.keys())

    # On trie les tâches par rang pour respecter l’ordre
    sorted_by_rank = sorted(tasks, key=lambda x: ranks[x[0]])

    # Calcul des dates au plus tôt
    for (t_id, dur, preds) in sorted_by_rank:
        if preds:
            earliest[t_id] = max(earliest[p] + get_duration(p, tasks) for p in preds)
        else:
            # Pas de prédécesseur (sauf α) => earliest[t_id] = earliest[0]
            if t_id != 0:
                earliest[t_id] = earliest[0]

    # Pour ω, c’est la max de earliest[t_id] + durée de la tâche
    tasks_ids = [t[0] for t in tasks]
    # Tâches sans successeurs
    tasks_with_succ = set()
    for (_, _, preds) in tasks:
        tasks_with_succ.update(preds)
    no_succ = set(tasks_ids) - tasks_with_succ

    earliest[omega] = max(earliest[t] + get_duration(t, tasks) for t in no_succ) if no_succ else 0

    # Calcul des dates au plus tard : on part de ω
    latest[omega] = earliest[omega]
    # On parcourt les tâches en sens inverse du rang
    for (t_id, dur, preds) in reversed(sorted_by_rank):
        # On recherche les successeurs
        succs = [tid for (tid, _, pds) in tasks if t_id in pds]
        if not succs:
            # Si pas de successeurs et que ce n’est pas ω
            if t_id != omega:
                latest[t_id] = latest[omega] - dur
        else:
            # min(latest[succ]) - durée
            latest[t_id] = min(latest[s] for s in succs) - dur

    return earliest, latest

def get_duration(task_id, tasks):
    """
    Renvoie la durée de la tâche task_id.
    """
    for (tid, dur, _) in tasks:
        if tid == task_id:
            return dur
    return 0

def calculate_slacks(earliest, latest):
    """
    Calcule la marge pour chaque sommet : slack = latest - earliest.
    Retourne un dict {sommet: marge}.
    """
    slacks = {}
    all_nodes = set(earliest.keys()) | set(latest.keys())
    for node in all_nodes:
        slacks[node] = latest[node] - earliest[node]
    return slacks

def show_slacks(slacks, ranks):
    """
    Affiche les marges (slacks) pour chaque sommet, triées par rang croissant.
    """
    # On ordonne selon le rang, sinon par numéro de sommet
    ordered_nodes = sorted(slacks.keys(), key=lambda x: (ranks.get(x, 9999), x))
    print("\nMarges (slacks) pour chaque sommet :")
    for node in ordered_nodes:
        print(f"Sommet {node} : marge = {slacks[node]}")

def show_critical_path(slacks, ranks):
    """
    Affiche les sommets critiques (ceux qui ont une marge nulle),
    dans l’ordre croissant de leur rang.
    """
    critical_nodes = [node for node, slack in slacks.items() if slack == 0]
    critical_nodes_sorted = sorted(critical_nodes, key=lambda x: (ranks.get(x, 9999), x))

    print("\nSommets critiques (marge = 0) :")
    if critical_nodes_sorted:
        print(" -> ".join(str(n) for n in critical_nodes_sorted))
    else:
        print("Aucun sommet critique trouvé.")
