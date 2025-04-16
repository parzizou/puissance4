# Module pour l'agent d'apprentissage par renforcement
import numpy as np
import random
import pickle
import os
from tqdm import tqdm  # Pour afficher une barre de progression (pip install tqdm si nécessaire)

# Module pour les couleurs dans le terminal
class Couleur:
    ROUGE = '\033[91m'
    JAUNE = '\033[93m'
    BLEU = '\033[94m'
    FIN = '\033[0m'
    FOND_BLEU = '\033[44m'
    BLANC = '\033[97m'

class QLearningAgent:
    def __init__(self, alpha=0.1, gamma=0.9, epsilon=0.1):
        """
        Initialise l'agent d'apprentissage par renforcement
        
        alpha: taux d'apprentissage (à quel point les nouvelles infos remplacent les anciennes)
        gamma: facteur de réduction (importance des récompenses futures)
        epsilon: probabilité d'explorer plutôt que d'exploiter
        """
        self.q_table = {}  # Stocke les valeurs Q pour chaque paire (état, action)
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
    
    def get_state_key(self, grille):
        """Convertit la grille en une chaîne de caractères unique (clé)"""
        # On utilise une représentation sous forme de tuple de tuples pour la grille
        return tuple(tuple(ligne) for ligne in grille.grille)
    
    def get_q_value(self, state, action):
        """Récupère la valeur Q pour un état et une action"""
        # Si on n'a jamais vu cet état ou cette action, on retourne 0
        if state not in self.q_table:
            self.q_table[state] = {}
        if action not in self.q_table[state]:
            self.q_table[state][action] = 0.0
        return self.q_table[state][action]
    
    def update_q_value(self, state, action, reward, next_state, next_actions):
        """Met à jour la valeur Q pour un état et une action"""
        # Vérifie si l'état existe dans le dictionnaire, sinon l'initialise
        if state not in self.q_table:
            self.q_table[state] = {}
        
        # Vérifie si l'action existe pour cet état, sinon l'initialise
        if action not in self.q_table[state]:
            self.q_table[state][action] = 0.0
            
        # Formule du Q-learning : Q(s,a) = Q(s,a) + alpha * [r + gamma * max(Q(s',a')) - Q(s,a)]
        max_next_q = max([self.get_q_value(next_state, a) for a in next_actions]) if next_actions else 0
        self.q_table[state][action] += self.alpha * (reward + self.gamma * max_next_q - self.q_table[state][action])
    
    def choose_action(self, grille, actions_valides):
        """
        Choisit une action selon la stratégie epsilon-greedy:
        - Avec probabilité epsilon: exploration (action aléatoire)
        - Avec probabilité 1-epsilon: exploitation (meilleure action connue)
        """
        state = self.get_state_key(grille)
        
        # Exploration: choisir une action aléatoire
        if random.random() < self.epsilon:
            return random.choice(actions_valides) if actions_valides else None
        
        # Exploitation: choisir la meilleure action connue
        else:
            # Si on n'a jamais vu cet état, on initialise ses valeurs Q
            if state not in self.q_table:
                self.q_table[state] = {}
            
            # Si certaines actions n'ont pas de valeur Q, on les initialise
            for action in actions_valides:
                if action not in self.q_table[state]:
                    self.q_table[state][action] = 0.0
            
            # Trouve l'action avec la plus grande valeur Q
            if actions_valides:
                return max(actions_valides, key=lambda a: self.q_table[state].get(a, 0.0))
            return None
    
    def save_model(self, filename='q_learning_model.pkl'):
        """Sauvegarde le modèle dans un fichier"""
        with open(filename, 'wb') as f:
            pickle.dump(self.q_table, f)
        print(f"Modèle sauvegardé dans {filename}")
    
    def load_model(self, filename='q_learning_model.pkl'):
        """Charge le modèle depuis un fichier"""
        if os.path.exists(filename):
            with open(filename, 'rb') as f:
                self.q_table = pickle.load(f)
            print(f"Modèle chargé depuis {filename}")
            return True
        return False


def entrainer_agent(episodes=10000, save_interval=1000):
    """Entraîne l'agent en le faisant jouer contre lui-même"""
    agent = QLearningAgent()
    
    # Essaie de charger un modèle existant
    agent.load_model()
    
    print(f"Début de l'entraînement sur {episodes} parties...")
    
    # Pour suivre les performances
    resultats = {"victoires_joueur1": 0, "victoires_joueur2": 0, "matchs_nuls": 0}
    
    # Import ici pour éviter les problèmes d'importation circulaire
    from main import Grille  
    
    for episode in tqdm(range(episodes)):
        # Réinitialise le jeu
        grille = Grille()
        joueur = 1  # Joueur 1 commence
        game_over = False
        
        # Historique des actions pour mettre à jour les valeurs Q à la fin
        historique = []
        
        # Joue jusqu'à la fin de la partie
        while not game_over:
            # Obtient les actions valides
            actions_valides = [col+1 for col in grille.coups_valides()]
            if not actions_valides:  # Match nul
                game_over = True
                reward = 0
                resultats["matchs_nuls"] += 1
                break
            
            # État actuel
            etat_actuel = agent.get_state_key(grille)
            
            # Choisit une action
            action = agent.choose_action(grille, actions_valides)
            
            # Joue l'action
            grille.ajouter_piece(action, joueur)
            
            # Enregistre l'action
            historique.append((etat_actuel, action, joueur))
            
            # Vérifie si le joueur a gagné
            if grille.est_gagnant(joueur):
                game_over = True
                reward = 1 if joueur == 1 else -1
                if joueur == 1:
                    resultats["victoires_joueur1"] += 1
                else:
                    resultats["victoires_joueur2"] += 1
            
            # Change de joueur
            joueur = 3 - joueur
        
        # Met à jour les valeurs Q pour toutes les actions de la partie
        if game_over:
            # Récompense finale
            for etat, action, joueur_action in reversed(historique):
                # L'agent qui a joué le dernier coup gagnant reçoit une récompense positive
                # L'autre agent reçoit une récompense négative
                r = reward if joueur_action == (3 - joueur) else -reward
                
                # Le prochain état est terminal, donc pas d'actions futures
                agent.update_q_value(etat, action, r, None, [])
        
        # Sauvegarde périodiquement le modèle
        if (episode + 1) % save_interval == 0:
            agent.save_model()
            print(f"\nAprès {episode + 1} parties:")
            print(f"Victoires joueur 1: {resultats['victoires_joueur1']}")
            print(f"Victoires joueur 2: {resultats['victoires_joueur2']}")
            print(f"Matchs nuls: {resultats['matchs_nuls']}")
    
    # Sauvegarde finale
    agent.save_model()
    
    print("\nEntraînement terminé!")
    print(f"Victoires joueur 1: {resultats['victoires_joueur1']}")
    print(f"Victoires joueur 2: {resultats['victoires_joueur2']}")
    print(f"Matchs nuls: {resultats['matchs_nuls']}")
    
    return agent

def jouer_contre_agent(g, joueur, agent):
    """Fonction pour faire jouer l'agent contre un humain"""
    # Obtient les actions valides
    actions_valides = [col+1 for col in g.coups_valides()]
    
    # L'agent choisit une action
    col = agent.choose_action(g, actions_valides)
    
    # Joue l'action
    g.ajouter_piece(col, joueur)
    
    return col