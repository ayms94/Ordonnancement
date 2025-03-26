# -*- coding: utf-8 -*-
"""
main.py
-------
Point d'entrée du programme. 
Boucle interactive qui demande à l’utilisateur de choisir un numéro de test (1 à 14),
puis effectue les étapes d’ordonnancement :
  1) Lecture du fichier table{choix}.txt
  2) Affichage du tableau de contraintes
  3) Construction et affichage de la matrice d’adjacence
  4) Vérification arcs négatifs + détection de circuit
  5) Calcul des rangs
  6) Calcul des dates au plus tôt et au plus tard
  7) Calcul et affichage des marges
  8) Affichage des sommets critiques

Auteur : Votre équipe
Année : 2024/2025
"""

import sys
from fonctions import (
    read_constraints_from_file, 
    show_constraints_overview,
    show_arcs,
    build_adjacency_matrix,
    show_adjacency_matrix,
    has_negative_arcs,
    detect_cycle,
    assign_ranks,
    compute_schedules,
    calculate_slacks,
    show_slacks,
    show_critical_path
)

def main():
    while True:
        print("\n=== ORDONNANCEMENT DE PROJET ===")
        choice = input("Entrez un numéro de test (1-14) ou 'q' pour quitter : ")
        if choice.lower() == 'q':
            print("Fin du programme.")
            sys.exit(0)

        # Construction du chemin d'accès au fichier
        file_path = f"Fichiers_a_test/table{choice}.txt"
        
        # Tentative de lecture du fichier
        try:
            tasks = read_constraints_from_file(file_path)
        except FileNotFoundError:
            print(f"Fichier introuvable : {file_path}")
            continue
        except ValueError:
            print(f"Format de fichier invalide pour : {file_path}")
            continue
        
        # Étape 1 : Affichage du tableau de contraintes
        print("\n[Étape 1] Lecture et affichage du tableau de contraintes :")
        show_constraints_overview(tasks)

        # Affichage des arcs (création du graphe)
        show_arcs(tasks)

        # Étape 2 : Construction + affichage de la matrice d’adjacence
        print("\n[Étape 2] Construction et affichage de la matrice :")
        matrix = build_adjacency_matrix(tasks)
        show_adjacency_matrix(matrix)

        # Étape 3 : Vérification arcs négatifs + détection de circuit
        print("\n[Étape 3] Vérifications : arcs négatifs et circuit")
        negative = has_negative_arcs(tasks)
        cycle = detect_cycle(matrix)
        if negative or cycle:
            print("Propriétés non vérifiées. Fin de l’ordonnancement pour ce fichier.")
            continue

        # Étape 4 : Calcul des rangs
        print("\n[Étape 4] Calcul des rangs :")
        ranks = assign_ranks(tasks)
        for node in sorted(ranks.keys()):
            print(f"Sommet {node} : rang = {ranks[node]}")

        # Étape 5 : Calcul des dates au plus tôt / plus tard
        print("\n[Étape 5] Calcul des dates (au plus tôt et au plus tard) :")
        earliest, latest = compute_schedules(tasks, ranks)
        # Affichage
        for n in sorted(ranks.keys()):
            print(f"Sommet {n} : ES = {earliest[n]} / LF = {latest[n]}")

        # Étape 6 : Calcul et affichage des marges
        print("\n[Étape 6] Calcul des marges :")
        slacks = calculate_slacks(earliest, latest)
        show_slacks(slacks, ranks)

        # Étape 7 : Chemin critique (ou sommets critiques)
        print("\n[Étape 7] Affichage des sommets (ou chemins) critiques :")
        show_critical_path(slacks, ranks)

if __name__ == "__main__":
    main()

