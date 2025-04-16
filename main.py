# Jeu de Puissance 4 avec IA
from agent import *

class Couleur:
    ROUGE = '\033[91m'
    JAUNE = '\033[93m'
    BLEU = '\033[94m'
    FIN = '\033[0m'
    FOND_BLEU = '\033[44m'
    BLANC = '\033[97m'

class Grille:
    def __init__(self):
        # Grille de 6 par 7
        self.grille = [[0 for _ in range(7)] for _ in range(6)]
        self.largeur = len(self.grille[0])
        self.hauteur = len(self.grille)
    
    def __str__(self):
        # Affiche la grille avec un style amélioré
        s = Couleur.BLEU + "\n  1   2   3   4   5   6   7\n"+ Couleur.FIN
        s += Couleur.BLEU + "┌" + "───┬" * (self.largeur-1) + "───┐" + Couleur.FIN + "\n"
        
        for i in range(self.hauteur):
            s += Couleur.BLEU + "│" + Couleur.FIN
            for j in range(self.largeur):
                if self.grille[i][j] == 0:
                    s += "   "
                elif self.grille[i][j] == 1:
                    s += " " + Couleur.ROUGE + "X" + Couleur.FIN + " "
                else:
                    s += " " + Couleur.JAUNE + "O" + Couleur.FIN + " "
                s += Couleur.BLEU + "│" + Couleur.FIN
            s += "\n"
            
            if i < self.hauteur - 1:
                s += Couleur.BLEU + "├" + "───┼" * (self.largeur-1) + "───┤" + Couleur.FIN + "\n"
            else:
                s += Couleur.BLEU + "└" + "───┴" * (self.largeur-1) + "───┘" + Couleur.FIN + "\n"
        
        return s
    
    def ajouter_piece(self, colonne, piece):
        # Ajoute une pièce dans la grille
        colonne -= 1  # Ajuste l'index de la colonne
        for i in range(self.hauteur-1, -1, -1):
            if self.grille[i][colonne] == 0:
                self.grille[i][colonne] = piece
                return True
        return False
    
    def est_pleine(self):
        # Vérifie si la grille est pleine
        for i in range(self.hauteur):
            for j in range(self.largeur):
                if self.grille[i][j] == 0:
                    return False
        return True
    
    def est_gagnant(self, piece):
        # Vérifie s'il y a un gagnant
        # Vérifie les lignes
        for i in range(self.hauteur):
            for j in range(self.largeur-3):
                if self.grille[i][j] == piece and self.grille[i][j+1] == piece and self.grille[i][j+2] == piece and self.grille[i][j+3] == piece:
                    return True
        # Vérifie les colonnes
        for i in range(self.hauteur-3):
            for j in range(self.largeur):
                if self.grille[i][j] == piece and self.grille[i+1][j] == piece and self.grille[i+2][j] == piece and self.grille[i+3][j] == piece:
                    return True
        # Vérifie les diagonales
        for i in range(self.hauteur-3):
            for j in range(self.largeur-3):
                if self.grille[i][j] == piece and self.grille[i+1][j+1] == piece and self.grille[i+2][j+2] == piece and self.grille[i+3][j+3] == piece:
                    return True
        for i in range(3, self.hauteur):
            for j in range(self.largeur-3):
                if self.grille[i][j] == piece and self.grille[i-1][j+1] == piece and self.grille[i-2][j+2] == piece and self.grille[i-3][j+3] == piece:
                    return True
        return False
    
    def coups_valides(self):
        # Retourne les colonnes valides (où on peut encore jouer)
        coups_valides = []
        for i in range(self.largeur):
            if self.grille[0][i] == 0:  # Si la première ligne de la colonne est vide
                coups_valides.append(i)
        return coups_valides

    def copier(self):
        # Crée une copie de la grille actuelle
        grille_copie = Grille()
        for i in range(self.hauteur):
            for j in range(self.largeur):
                grille_copie.grille[i][j] = self.grille[i][j]
        return grille_copie

# Fonctions pour l'IA

def evaluer_fenetre(fenetre, piece):
    """Évalue une fenêtre de 4 cases pour un joueur donné"""
    score = 0
    piece_adversaire = 1 if piece == 2 else 2  # Identifie la pièce adverse
    
    # Différents scénarios avec leurs scores
    if fenetre.count(piece) == 4:  # Victoire
        score += 100
    elif fenetre.count(piece) == 3 and fenetre.count(0) == 1:  # 3 pièces alignées
        score += 5
    elif fenetre.count(piece) == 2 and fenetre.count(0) == 2:  # 2 pièces alignées
        score += 2
        
    # Pénalise si l'adversaire est en position de gagner
    if fenetre.count(piece_adversaire) == 3 and fenetre.count(0) == 1:
        score -= 4
        
    return score

def calculer_score_position(grille, piece):
    """Évalue le score total d'une position pour un joueur donné"""
    score = 0
    
    # Favorise les pièces au centre (colonne 4)
    colonne_centrale = [grille.grille[i][3] for i in range(grille.hauteur)]
    score += colonne_centrale.count(piece) * 3
    
    # Évalue les lignes
    for i in range(grille.hauteur):
        ligne = [grille.grille[i][j] for j in range(grille.largeur)]
        for j in range(grille.largeur - 3):
            fenetre = ligne[j:j+4]
            score += evaluer_fenetre(fenetre, piece)
    
    # Évalue les colonnes
    for j in range(grille.largeur):
        colonne = [grille.grille[i][j] for i in range(grille.hauteur)]
        for i in range(grille.hauteur - 3):
            fenetre = colonne[i:i+4]
            score += evaluer_fenetre(fenetre, piece)
    
    # Évalue les diagonales montantes (/)
    for i in range(grille.hauteur - 3):
        for j in range(grille.largeur - 3):
            fenetre = [grille.grille[i+k][j+k] for k in range(4)]
            score += evaluer_fenetre(fenetre, piece)
    
    # Évalue les diagonales descendantes (\)
    for i in range(grille.hauteur - 3):
        for j in range(grille.largeur - 3):
            fenetre = [grille.grille[i+3-k][j+k] for k in range(4)]
            score += evaluer_fenetre(fenetre, piece)
    
    return score

def est_noeud_terminal(grille):
    """Vérifie si la partie est terminée"""
    return grille.est_gagnant(1) or grille.est_gagnant(2) or len(grille.coups_valides()) == 0

def minimax(grille, profondeur, alpha, beta, maximisant):
    """
    Algorithme Minimax avec élagage Alpha-Beta
    
    - grille: l'état actuel du jeu
    - profondeur: nombre de coups à anticiper
    - alpha, beta: paramètres pour l'élagage
    - maximisant: True si c'est au tour de l'IA, False sinon
    """
    # On récupère les colonnes où on peut jouer
    coups_valides = grille.coups_valides()
    
    # Si on a atteint la profondeur max ou si le jeu est terminé
    est_terminal = est_noeud_terminal(grille)
    if profondeur == 0 or est_terminal:
        if est_terminal:
            # Si l'IA gagne
            if grille.est_gagnant(2):  # 2 pour l'IA
                return (None, 1000000)
            # Si l'humain gagne
            elif grille.est_gagnant(1):  # 1 pour le joueur humain
                return (None, -1000000)
            # Match nul
            else:
                return (None, 0)
        # Si on a atteint la profondeur maximale
        else:
            return (None, calculer_score_position(grille, 2))
    
    # Si c'est au tour de l'IA (maximisant)
    if maximisant:
        valeur = float('-inf')
        colonne = coups_valides[0] if coups_valides else 0  # Colonne par défaut
        
        # On teste chaque colonne possible
        for col in coups_valides:
            # On crée une copie de la grille pour simuler le coup
            grille_copie = grille.copier()
            
            # On joue le coup (col+1 car les colonnes sont indexées de 1 à 7 dans ajouter_piece)
            grille_copie.ajouter_piece(col+1, 2)  # 2 pour l'IA
            
            # On évalue ce coup avec minimax récursivement
            nouveau_score = minimax(grille_copie, profondeur-1, alpha, beta, False)[1]
            
            # Si ce coup est meilleur, on le garde
            if nouveau_score > valeur:
                valeur = nouveau_score
                colonne = col
            
            # Mise à jour d'alpha
            alpha = max(alpha, valeur)
            
            # Élagage Alpha-Beta
            if alpha >= beta:
                break
                
        return colonne+1, valeur  # +1 car on veut retourner un index de 1 à 7
    
    # Si c'est au tour de l'adversaire (minimisant)
    else:
        valeur = float('inf')
        colonne = coups_valides[0] if coups_valides else 0  # Colonne par défaut
        
        # On teste chaque colonne possible
        for col in coups_valides:
            # On crée une copie de la grille pour simuler le coup
            grille_copie = grille.copier()
            
            # On joue le coup
            grille_copie.ajouter_piece(col+1, 1)  # 1 pour le joueur humain
            
            # On évalue ce coup avec minimax récursivement
            nouveau_score = minimax(grille_copie, profondeur-1, alpha, beta, True)[1]
            
            # Si ce coup est meilleur (pire pour l'IA), on le garde
            if nouveau_score < valeur:
                valeur = nouveau_score
                colonne = col
            
            # Mise à jour de beta
            beta = min(beta, valeur)
            
            # Élagage Alpha-Beta
            if alpha >= beta:
                break
                
        return colonne+1, valeur  # +1 car on veut retourner un index de 1 à 7


def agent_vs_minimax():
    """Fait jouer l'agent contre l'IA Minimax"""
    # Charge l'agent
    agent = QLearningAgent(epsilon=0.0)  # Epsilon à 0 pour jouer de façon optimale
    if not agent.load_model():
        print(Couleur.ROUGE + "⚠️ Pas de modèle entraîné trouvé! Il faut d'abord entraîner l'agent (option 4)." + Couleur.FIN)
        return
    
    # Initialise la grille
    g = Grille()
    
    # Symboles et noms des joueurs
    symboles = {1: Couleur.ROUGE + "X" + Couleur.FIN, 2: Couleur.JAUNE + "O" + Couleur.FIN}
    noms = {1: "Agent (apprentissage par renforcement)", 2: "Minimax"}
    
    # Demande qui commence
    debut = ""
    while debut not in ["1", "2"]:
        debut = input("Qui commence ?\n1 - L'Agent (IA par renforcement)\n2 - Minimax\nTon choix : ")
    
    joueur = 1 if debut == "1" else 2
    
    # Demande la difficulté pour Minimax
    difficulte = 4  # Difficulté par défaut
    try:
        diff_input = input("Choisis la difficulté de Minimax (1-10) : ")
        difficulte = int(diff_input)
        if difficulte < 1 or difficulte > 10:
            print(Couleur.ROUGE + "⚠️ Difficulté invalide ! Réglage à 4 par défaut." + Couleur.FIN)
            difficulte = 4
    except ValueError:
        print(Couleur.ROUGE + "⚠️ Entrée invalide ! Difficulté réglée à 4 par défaut." + Couleur.FIN)
    
    # Demande la vitesse d'exécution
    vitesse = ""
    while vitesse not in ["1", "2", "3"]:
        vitesse = input("Vitesse de jeu :\n1 - Rapide (sans pause)\n2 - Normale (pause courte)\n3 - Lente (pause longue)\nTon choix : ")
    
    temps_pause = 0
    if vitesse == "2":
        temps_pause = 1  # 1 seconde
    elif vitesse == "3":
        temps_pause = 3  # 3 secondes
    
    # Nombre de parties à jouer
    try:
        nb_parties = int(input("Combien de parties veux-tu faire jouer ? "))
    except ValueError:
        print(Couleur.ROUGE + "⚠️ Nombre invalide ! On joue 1 partie." + Couleur.FIN)
        nb_parties = 1
    
    # Statistiques
    stats = {"agent": 0, "minimax": 0, "nuls": 0}
    
    # Joue plusieurs parties
    for partie in range(nb_parties):
        print(f"\n{Couleur.FOND_BLEU + Couleur.BLANC} PARTIE {partie+1}/{nb_parties} {Couleur.FIN}")
        
        # Réinitialise la grille pour chaque partie
        g = Grille()
        game_over = False
        joueur = 1 if debut == "1" else 2  # Réinitialise qui commence
        
        # Boucle de jeu
        while not game_over:
            # Affiche la grille
            print(g)
            
            # Affiche le tour du joueur
            print(f"C'est au tour de {noms[joueur]} ({symboles[joueur]})")
            
            # Tour de l'Agent
            if joueur == 1:
                print("L'Agent réfléchit...")
                actions_valides = [col+1 for col in g.coups_valides()]
                col = agent.choose_action(g, actions_valides)
                g.ajouter_piece(col, joueur)
                print(f"L'Agent joue dans la colonne {col}")
            
            # Tour de Minimax
            else:
                print("Minimax réfléchit...")
                col, _ = minimax(g, difficulte, float('-inf'), float('inf'), True)
                g.ajouter_piece(col, joueur)
                print(f"Minimax joue dans la colonne {col}")
            
            # Pause pour voir le jeu se dérouler
            if temps_pause > 0:
                import time
                time.sleep(temps_pause)
                
            # Vérifie si le joueur a gagné
            if g.est_gagnant(joueur):
                print(g)
                if joueur == 1:
                    print(f"🧠 {Couleur.FOND_BLEU + Couleur.BLANC} L'Agent a gagné! {Couleur.FIN} 🧠")
                    stats["agent"] += 1
                else:
                    print(f"🤖 {Couleur.FOND_BLEU + Couleur.BLANC} Minimax a gagné! {Couleur.FIN} 🤖")
                    stats["minimax"] += 1
                game_over = True
                
            # Vérifie si la grille est pleine
            if not game_over and g.est_pleine():
                print(g)
                print(f"{Couleur.FOND_BLEU + Couleur.BLANC} Match nul! {Couleur.FIN}")
                stats["nuls"] += 1
                game_over = True
                
            # Change de joueur
            if not game_over:
                joueur = 3 - joueur
    
    # Affiche les statistiques finales
    print("\n" + "="*40)
    print(f"{Couleur.FOND_BLEU + Couleur.BLANC} RÉSULTATS APRÈS {nb_parties} PARTIES {Couleur.FIN}")
    print(f"Victoires de l'Agent : {stats['agent']} ({stats['agent']/nb_parties*100:.1f}%)")
    print(f"Victoires de Minimax : {stats['minimax']} ({stats['minimax']/nb_parties*100:.1f}%)")
    print(f"Matchs nuls : {stats['nuls']} ({stats['nuls']/nb_parties*100:.1f}%)")
    print("="*40)







def afficher_titre():
    titre = """
    ╔═══════════════════════════════╗
    ║          PUISSANCE 4          ║
    ╚═══════════════════════════════╝
    """
    print(Couleur.FOND_BLEU + Couleur.BLANC + titre + Couleur.FIN)

def jeu():
    # Initialise la grille
    g = Grille()
    # Initialise le joueur
    joueur = 1
    symboles = {1: Couleur.ROUGE + "X" + Couleur.FIN, 2: Couleur.JAUNE + "O" + Couleur.FIN}
    
    afficher_titre()
    
    # Demande si le joueur veut jouer contre l'IA
    mode_jeu = ""
    while mode_jeu not in ["1", "2", "3", "4", "5"]:  # Ajout de l'option 5
        mode_jeu = input("Choisis le mode de jeu :\n"
                         "1 - Joueur contre Joueur\n"
                         "2 - Joueur contre IA Minimax\n"
                         "3 - Joueur contre Agent (IA par renforcement)\n"
                         "4 - Entraîner l'Agent\n"
                         "5 - Agent contre Minimax (spectateur)\n"
                         "Ton choix : ")
    
    # Si on veut faire jouer l'agent contre minimax
    if mode_jeu == "5":
        agent_vs_minimax()
        return
    
    # Si on veut entraîner l'agent
    if mode_jeu == "4":
        try:
            nb_parties = int(input("Combien de parties d'entraînement ? (5000 recommandé pour débuter) : "))
            entrainer_agent(episodes=nb_parties)
        except ValueError:
            print(Couleur.ROUGE + "⚠️ Nombre invalide ! Entraînement avec 5000 parties." + Couleur.FIN)
            entrainer_agent(episodes=5000)
        return
    
    mode_ia_minimax = mode_jeu == "2"
    mode_agent = mode_jeu == "3"
    
    # Charge l'agent si nécessaire
    agent = None
    if mode_agent:
        agent = QLearningAgent(epsilon=0.0)  # Epsilon à 0 pour jouer de façon optimale
        if not agent.load_model():
            print(Couleur.ROUGE + "⚠️ Pas de modèle entraîné trouvé! Il faut d'abord entraîner l'agent (option 4)." + Couleur.FIN)
            return
    
    # Demande la difficulté si on joue contre l'IA Minimax
    difficulte = 4  # Difficulté par défaut
    if mode_ia_minimax:
        try:
            diff_input = input("Choisis la difficulté (1-10) - Plus le chiffre est élevé, plus l'IA est forte mais réfléchit longtemps: ")
            difficulte = int(diff_input)
            if difficulte < 1 or difficulte > 10:
                print(Couleur.ROUGE + "⚠️ Difficulté invalide ! Réglage à 4 par défaut." + Couleur.FIN)
                difficulte = 4
        except ValueError:
            print(Couleur.ROUGE + "⚠️ Entrée invalide ! Difficulté réglée à 4 par défaut." + Couleur.FIN)
    
    # Qui commence ? (pour les modes avec IA)
    if mode_ia_minimax or mode_agent:
        debut = ""
        while debut not in ["1", "2"]:
            debut = input("Qui commence ?\n1 - Toi\n2 - L'IA\nTon choix : ")
        
        joueur = 1 if debut == "1" else 2
    
    # Boucle de jeu
    while True:
        # Affiche la grille
        print(g)
        
        # Affiche le tour du joueur
        print(f"C'est au tour du joueur {symboles[joueur]}")
        
        # Tour du joueur humain
        if joueur == 1 or (not mode_ia_minimax and not mode_agent):
            # Demande au joueur de jouer
            try:
                col = int(input(f"Choisis une colonne (1-7): "))
                # Vérifie si la colonne est valide
                if col < 1 or col > 7:
                    print(Couleur.ROUGE + "⚠️ Colonne invalide! Choisis entre 1 et 7." + Couleur.FIN)
                    continue
                # Vérifie si la colonne est pleine
                if not g.ajouter_piece(col, joueur):
                    print(Couleur.ROUGE + "⚠️ Cette colonne est pleine! Essaie une autre." + Couleur.FIN)
                    continue
            except ValueError:
                print(Couleur.ROUGE + "⚠️ Entrée invalide! Tu dois entrer un nombre." + Couleur.FIN)
                continue
        # Tour de l'IA Minimax
        elif mode_ia_minimax:
            print("L'IA Minimax réfléchit...")
            col, minimax_score = minimax(g, difficulte, float('-inf'), float('inf'), True)
            g.ajouter_piece(col, joueur)
            print(f"L'IA Minimax joue dans la colonne {col}")
        # Tour de l'Agent (IA par renforcement)
        elif mode_agent:
            print("L'Agent réfléchit...")
            col = jouer_contre_agent(g, joueur, agent)
            print(f"L'Agent joue dans la colonne {col}")
                
        # Vérifie si le joueur a gagné
        if g.est_gagnant(joueur):
            print(g)
            if joueur == 1:
                print(f"🎉 {Couleur.FOND_BLEU + Couleur.BLANC} Tu as gagné! {Couleur.FIN} 🎉")
            else:
                if mode_ia_minimax:
                    print(f"🤖 {Couleur.FOND_BLEU + Couleur.BLANC} L'IA Minimax a gagné! {Couleur.FIN} 🤖")
                elif mode_agent:
                    print(f"🧠 {Couleur.FOND_BLEU + Couleur.BLANC} L'Agent a gagné! {Couleur.FIN} 🧠")
                else:
                    print(f"🎉 {Couleur.FOND_BLEU + Couleur.BLANC} Le joueur 2 a gagné! {Couleur.FIN} 🎉")
            break
            
        # Vérifie si la grille est pleine
        if g.est_pleine():
            print(g)
            print(f"{Couleur.FOND_BLEU + Couleur.BLANC} Match nul! {Couleur.FIN}")
            break
            
        # Change de joueur
        joueur = 3 - joueur
    
    # Demande si on veut rejouer
    rejouer = input("\nVeux-tu rejouer? (o/n): ").lower()
    if rejouer == 'o':
        jeu()

if __name__ == "__main__":
    jeu()