"""
TP Traitement d'Images — Partie Classification (KNN + Moyenne + Améliorations)
===============================================================================
Suite du script tp_segmentation.py (Q1–Q9 cavités).
Ce fichier traite les questions de classification du TP de M. Vandenbroucke Nicolas.

  Q_class 1  : Définition de l'espace de décision (vecteur d'attributs)
  Q_class 2  : Apprentissage hors-ligne (matrice features, vecteur classes, moyennes)
  Q_class 3  : Classification 1-NN (plus proche voisin)
  Q_class 4  : Validation 1-NN sur la base de test
  Q_class 5  : Classification par plus proche moyenne (centroïde)
  Q_class 6  : Validation + comparaison 1-NN vs Moyenne
  Q_class 7  : Enrichissement avec attributs regionprops invariants à l'échelle
  Q_class 8  : Recalage en rotation avant classification
  Q_class 9  : Séparation des chiffres qui se touchent

UTILISATION (Google Colab + Drive) :
    from google.colab import drive
    drive.mount('/content/drive')

    Entraînement : /content/drive/MyDrive/Train_set (1)
                   images nommées 0_Nom.jpg … 9_Nom.jpg
    Test         : /content/drive/MyDrive/Test_set
                   images de codes postaux à classifier
    Puis lancez : python tp_classification.py
"""

import os
import time
import warnings
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from   matplotlib.colors import ListedColormap
from   PIL import Image
from   scipy.ndimage import (binary_fill_holes, rotate as ndrotate,
                              label as ndlabel)
from   skimage.filters     import threshold_otsu
from   skimage.exposure    import equalize_adapthist
from   skimage.morphology  import (closing, opening, dilation,
                                   remove_small_objects, disk)
from   skimage.measure     import label, regionprops
from   skimage.segmentation import clear_border

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────────────────────────
#  PARAMÈTRES GLOBAUX  (à ajuster selon votre jeu de données)
# ─────────────────────────────────────────────────────────────────────────────
NB_CLASSES      = 10          # chiffres 0–9
NB_PROTO_MAX    = 6           # max prototypes retenus par image d'apprentissage

# ── Chemins Google Drive (Colab) ────────────────────────────────────────────
DOSSIER_TRAIN   = "/content/drive/MyDrive/Train_set (1)"
DOSSIER_TEST    = "/content/drive/MyDrive/Test_set"

SEUIL           = 130         # seuil de binarisation de repli (utilisé si Otsu échoue)
AIRE_MIN        = 300         # aire minimale d'une composante connexe (px²)
AIRE_MAX        = 60_000      # aire maximale
MARGE_BB        = 8           # marge autour de chaque chiffre isolé
K_VOISINS       = 3           # nombre de voisins pour le classifieur k-NN
ANGLE_ROT_MAX   = 10.0        # angle de rotation maximal autorisé (degrés)
NB_CHIFFRES_MAX = 6           # nombre max de chiffres attendus par code postal

# Seuil de "contact" entre chiffres pour Q9 (rapport d'aspect élevé → fusion)
RATIO_CONTACT   = 1.8         # largeur/hauteur > RATIO_CONTACT → possible fusion

# ─────────────────────────────────────────────────────────────────────────────
#  CHARGEMENT DES DONNÉES (Google Drive)
# ─────────────────────────────────────────────────────────────────────────────

_EXTENSIONS_IMG = {
    '.png', '.jpg', '.jpeg', '.tif', '.tiff', '.bmp',
    '.PNG', '.JPG', '.JPEG', '.TIF', '.TIFF', '.BMP',
}


def lister_images_dossier(dossier):
    """Retourne la liste triée des chemins d'images dans un dossier."""
    if not os.path.isdir(dossier):
        return []
    return sorted(
        os.path.join(dossier, nom)
        for nom in os.listdir(dossier)
        if os.path.splitext(nom)[1] in _EXTENSIONS_IMG
    )


def extraire_classe_train(nom_fichier):
    """
    Extrait le chiffre (0–9) au début du nom de fichier.
    Exemple : '0_ASSOUMA_AbdouMalick.jpg' → 0
    """
    base = os.path.splitext(os.path.basename(nom_fichier))[0]
    prefixe = base.split('_')[0]
    if len(prefixe) == 1 and prefixe.isdigit():
        return int(prefixe)
    return None


# ─────────────────────────────────────────────────────────────────────────────
#  FONCTIONS UTILITAIRES PARTAGÉES
# ─────────────────────────────────────────────────────────────────────────────

def charger_image_gris(chemin):
    """Ouvre une image et la convertit en niveaux de gris (uint8)."""
    img = np.array(Image.open(chemin))
    if img.ndim == 3:
        R, G, B = img[:,:,0].astype(np.float64), \
                  img[:,:,1].astype(np.float64), \
                  img[:,:,2].astype(np.float64)
        return (0.299*R + 0.587*G + 0.114*B).astype(np.uint8)
    return img.astype(np.uint8)


def binariser(img_gris, seuil=None):
    """
    Binarisation adaptative : CLAHE + Otsu.
    Si Otsu échoue (image trop uniforme), on utilise le seuil de repli.
    """
    img_clahe = equalize_adapthist(img_gris, clip_limit=0.03)
    img_uint8 = (img_clahe * 255).astype(np.uint8)
    try:
        seuil_otsu = threshold_otsu(img_uint8)
    except Exception:
        seuil_otsu = seuil if seuil is not None else SEUIL
    return img_uint8 < seuil_otsu


def pretraiter(bin_bool, aire_min=AIRE_MIN):
    """Pipeline morphologique : clear_border → fill → close → open."""
    b = clear_border(bin_bool)
    b = remove_small_objects(b, min_size=aire_min)
    b = binary_fill_holes(b)
    b = closing(b, disk(2))
    b = opening(b, disk(1))
    return b


def localiser_chiffres(bin_propre, aire_min=AIRE_MIN, aire_max=AIRE_MAX,
                       filtrage_median=False):
    """
    Étiquetage des composantes connexes + filtrage par aire.
    Si filtrage_median=True, ne garde que les composantes dont l'aire
    est entre 0.15× et 5× la médiane, et limite à NB_CHIFFRES_MAX.
    """
    img_lab  = label(bin_propre)
    props    = regionprops(img_lab)
    filtrees = [r for r in props if aire_min < r.area < aire_max]

    if filtrage_median and len(filtrees) > NB_CHIFFRES_MAX:
        aires = np.array([r.area for r in filtrees], dtype=float)
        med = np.median(aires)
        filtrees = [r for r in filtrees if 0.15 * med < r.area < 5.0 * med]
        if len(filtrees) > NB_CHIFFRES_MAX:
            filtrees = sorted(filtrees, key=lambda r: abs(r.area - med))
            filtrees = filtrees[:NB_CHIFFRES_MAX]

    filtrees.sort(key=lambda r: r.bbox[1])
    return img_lab, filtrees


def limiter_prototypes_train(props, nb_max=NB_PROTO_MAX):
    """
    Garde au plus nb_max prototypes par image d'apprentissage.
    Si trop de régions détectées, conserve celles dont l'aire est
    la plus proche de la médiane (élimine le bruit trop petit/grand).
    """
    if len(props) <= nb_max:
        return props
    aires = np.array([p.area for p in props], dtype=float)
    med = np.median(aires)
    triees = sorted(props, key=lambda p: abs(p.area - med))
    return sorted(triees[:nb_max], key=lambda p: p.bbox[1])


def extraire_region(bin_propre, img_lab, prop, marge=MARGE_BB):
    """
    Extrait le masque booléen d'un chiffre isolé (sans ses voisins)
    avec une marge autour de la bounding box.
    """
    minr, minc, maxr, maxc = prop.bbox
    r0 = max(0, minr - marge);  c0 = max(0, minc - marge)
    r1 = min(bin_propre.shape[0], maxr + marge)
    c1 = min(bin_propre.shape[1], maxc + marge)
    masque = (img_lab[r0:r1, c0:c1] == prop.label)
    return masque.astype(bool)


def dilater_4_directions(chiffre_bool):
    """Dilatations directionnelles N, S, E, O avec éléments structurants linéaires."""
    V, H = chiffre_bool.shape
    se_est   = np.zeros((1, 2*H+1), dtype=bool); se_est[0, H:]   = True
    se_ouest = np.fliplr(se_est)
    se_sud   = np.zeros((2*V+1, 1), dtype=bool); se_sud[V:, 0]   = True
    se_nord  = np.flipud(se_sud)
    return {
        'est'  : dilation(chiffre_bool, se_est),
        'ouest': dilation(chiffre_bool, se_ouest),
        'sud'  : dilation(chiffre_bool, se_sud),
        'nord' : dilation(chiffre_bool, se_nord),
    }


def detecter_cavites(chiffre_bool, dilat):
    """Calcule les 5 masques de cavités (centre, est, ouest, nord, sud)."""
    e, o, s, n = dilat['est'], dilat['ouest'], dilat['sud'], dilat['nord']
    inv = ~chiffre_bool
    return {
        'centre': e & o  & s  & n  & inv,
        'est'   : e & ~o & s  & n  & inv,
        'ouest' : ~e& o  & s  & n  & inv,
        'nord'  : e & o  & ~s & n  & inv,
        'sud'   : e & o  & s  & ~n & inv,
    }


# ─────────────────────────────────────────────────────────────────────────────
#  Q_class 1 — ESPACE DE DÉCISION
# ─────────────────────────────────────────────────────────────────────────────

def calculer_vecteur_attributs_base(chiffre_bool):
    """
    Q_class 1 — Vecteur d'attributs basique (5 surfaces de cavités normalisées).
    Chaque cavité est exprimée en pourcentage de la surface totale du chiffre.
    """
    dilat  = dilater_4_directions(chiffre_bool)
    cavites = detecter_cavites(chiffre_bool, dilat)
    aire_chiffre = max(1, np.sum(chiffre_bool))   # évite division par 0
    noms = ['centre', 'est', 'ouest', 'nord', 'sud']
    return np.array([np.sum(cavites[n]) / aire_chiffre for n in noms])


def calculer_vecteur_attributs_enrichi(chiffre_bool, prop=None):
    """
    Q_class 7 — Vecteur enrichi : 5 surfaces cavités + attributs regionprops
    invariants à l'échelle.
    Attributs ajoutés (tous normalisés → sans unité, invariants à l'échelle) :
      - excentricité            (0 = cercle, 1 = segment)
      - solidité                (aire / aire_convexe)
      - rapport d'aspect        (axe_min / axe_maj)
      - rondeur                 (4π·aire / périmètre²)
      - nb de trous (Euler)     (label sur fond → proxy du nb de cavités fermées)
    """
    vect_base = calculer_vecteur_attributs_base(chiffre_bool)

    if prop is None:
        # On recalcule regionprops sur le masque isolé si non fourni
        lbl  = label(chiffre_bool)
        prop = max(regionprops(lbl), key=lambda r: r.area, default=None)

    if prop is None:
        return np.concatenate([vect_base, np.zeros(5)])

    aire     = max(prop.area, 1)
    perim    = max(prop.perimeter, 1)
    excentr  = prop.eccentricity                          # [0,1]
    solidite = prop.solidity                              # [0,1]
    if prop.major_axis_length > 0:
        rapport_aspect = prop.minor_axis_length / prop.major_axis_length
    else:
        rapport_aspect = 0.0
    rondeur  = (4 * np.pi * aire) / (perim ** 2)         # [0,1]

    # Euler number (proxy nb de trous) : normalisé entre 0 et 1
    euler    = prop.euler_number  # positif = sans trou, négatif = trous
    euler_n  = np.clip(-euler / 3.0, 0, 1)               # 0→sans trou, 1→3+ trous

    attrs_rp = np.array([excentr, solidite, rapport_aspect, rondeur, euler_n])
    return np.concatenate([vect_base, attrs_rp])


# ─────────────────────────────────────────────────────────────────────────────
#  Q_class 2 — APPRENTISSAGE HORS-LIGNE
# ─────────────────────────────────────────────────────────────────────────────

def apprentissage(mode='base', verbose=True):
    """
    Q_class 2 — Construit :
      - matrice_features  : (nb_prototypes_total, nb_attributs)
      - vecteur_classes   : (nb_prototypes_total,)  étiquette 0–9
      - matrice_moyennes  : (NB_CLASSES, nb_attributs)  centre de chaque classe
    mode = 'base' → 5 attributs (Q1–Q6)
    mode = 'enrichi' → 10 attributs (Q7)

    Parcourt DOSSIER_TRAIN : la classe est lue au début du nom de fichier
    (ex. '0_Nom.jpg' → classe 0).
    """
    t0 = time.time()
    calc_vect = (calculer_vecteur_attributs_enrichi
                 if mode == 'enrichi'
                 else calculer_vecteur_attributs_base)

    all_features = []
    all_labels   = []
    nb_total     = 0

    fichiers_train = lister_images_dossier(DOSSIER_TRAIN)

    if verbose:
        print(f"\n{'='*60}")
        print(f"Q_class 2 — Apprentissage hors-ligne  [mode={mode}]")
        print(f"{'='*60}")
        print(f"  Dossier train : {DOSSIER_TRAIN}")
        print(f"  {len(fichiers_train)} image(s) trouvée(s)")

    for chemin in fichiers_train:
        nom = os.path.basename(chemin)
        classe = extraire_classe_train(nom)
        if classe is None or not (0 <= classe < NB_CLASSES):
            if verbose:
                print(f"  [IGNORÉ] {nom} — étiquette invalide (attendu : 0_Nom.ext)")
            continue

        img_gris = charger_image_gris(chemin)
        bin_bool = binariser(img_gris)
        bin_prop = pretraiter(bin_bool)
        img_lab, props = localiser_chiffres(bin_prop)
        props = limiter_prototypes_train(props)

        if verbose:
            print(f"  {nom} (classe {classe}) : {len(props)} prototype(s) détecté(s)")

        for prop in props:
            ch = extraire_region(bin_prop, img_lab, prop)
            if mode == 'enrichi':
                # Recalculer regionprops sur le masque isolé
                lbl_iso = label(ch)
                props_iso = regionprops(lbl_iso)
                p_iso = max(props_iso, key=lambda r: r.area) if props_iso else None
                vect = calculer_vecteur_attributs_enrichi(ch, p_iso)
            else:
                vect = calculer_vecteur_attributs_base(ch)
            all_features.append(vect)
            all_labels.append(classe)
            nb_total += 1

    if nb_total == 0:
        print("  ERREUR : aucun prototype chargé. Vérifiez DOSSIER_TRAIN.")
        return None, None, None, None, None

    matrice_features = np.array(all_features)     # (N, D)
    vecteur_classes  = np.array(all_labels)        # (N,)

    # Normalisation z-score par attribut
    feat_mean = matrice_features.mean(axis=0)
    feat_std  = matrice_features.std(axis=0)
    feat_std[feat_std < 1e-8] = 1.0
    matrice_features = (matrice_features - feat_mean) / feat_std

    # Matrice des moyennes : une ligne par classe
    D = matrice_features.shape[1]
    matrice_moyennes = np.zeros((NB_CLASSES, D))
    for c in range(NB_CLASSES):
        idx = vecteur_classes == c
        if np.any(idx):
            matrice_moyennes[c] = matrice_features[idx].mean(axis=0)

    dt = time.time() - t0
    if verbose:
        print(f"\n  Prototypes chargés : {nb_total}")
        print(f"  Dimension du vecteur d'attributs : {D}")
        print(f"  Temps d'apprentissage : {dt*1000:.1f} ms")
        noms_attr = (['Cav.Centre','Cav.Est','Cav.Ouest','Cav.Nord','Cav.Sud']
                     + (['Excentr.','Solidité','Rapp.Aspect','Rondeur','Euler']
                        if mode == 'enrichi' else []))
        print(f"\n  Moyennes par classe :")
        header = f"  {'Classe':>6} | " + " | ".join(f"{n:>12}" for n in noms_attr)
        print(header)
        print("  " + "-" * (len(header)-2))
        for c in range(NB_CLASSES):
            idx = vecteur_classes == c
            if np.any(idx):
                vals = " | ".join(f"{v:>12.4f}" for v in matrice_moyennes[c])
                print(f"  {c:>6} | {vals}")

    return matrice_features, vecteur_classes, matrice_moyennes, feat_mean, feat_std


# ─────────────────────────────────────────────────────────────────────────────
#  PIPELINE : traiter une image de code postal → liste de chiffres + attributs
# ─────────────────────────────────────────────────────────────────────────────

def traiter_image_code(chemin_img, mode='base', recalage_rotation=False,
                       separer_contacts=False):
    """
    Charge une image de code postal, la prétraite et extrait les vecteurs
    d'attributs de chaque chiffre détecté.

    Retourne :
      img_gris      : image grise originale
      bin_propre    : image binaire prétraitée
      props_final   : liste des regionprops (chiffres détectés)
      features_test : ndarray (nb_chiffres, D)
      angle_deg     : angle de rotation corrigé (Q8) ou 0
    """
    img_gris = charger_image_gris(chemin_img)

    # ── Q8 : recalage en rotation ──────────────────────────────────────────
    angle_deg = 0.0
    if recalage_rotation:
        bin_tmp  = pretraiter(binariser(img_gris))
        lbl_tmp, props_tmp = localiser_chiffres(bin_tmp)
        if props_tmp:
            # On travaille sur l'ensemble des pixels des chiffres détectés
            # pour estimer l'axe principal d'inertie global
            centres = np.array([[p.centroid[1], p.centroid[0]]
                                 for p in props_tmp])
            if len(centres) >= 2:
                cov = np.cov(centres.T)
                vals, vecs = np.linalg.eigh(cov)
                v = vecs[:, np.argmax(vals)]
                angle_deg = np.degrees(np.arctan2(v[1], v[0]))
                if abs(angle_deg) > ANGLE_ROT_MAX:
                    angle_deg = 0.0
                if abs(angle_deg) > 1.0:
                    img_gris = ndrotate(img_gris, angle_deg,
                                        reshape=False, order=1,
                                        mode='nearest').astype(np.uint8)

    bin_bool = binariser(img_gris)
    bin_prop = pretraiter(bin_bool)

    # ── Q9 : séparation des chiffres qui se touchent ───────────────────────
    if separer_contacts:
        bin_prop = separer_chiffres_touches(bin_prop)

    img_lab, props = localiser_chiffres(bin_prop, filtrage_median=True)

    features_test = []
    for prop in props:
        ch = extraire_region(bin_prop, img_lab, prop)
        if mode == 'enrichi':
            lbl_iso   = label(ch)
            props_iso = regionprops(lbl_iso)
            p_iso     = max(props_iso, key=lambda r: r.area) if props_iso else None
            vect      = calculer_vecteur_attributs_enrichi(ch, p_iso)
        else:
            vect      = calculer_vecteur_attributs_base(ch)
        features_test.append(vect)

    features_test = np.array(features_test) if features_test else np.zeros((0, 5))
    return img_gris, bin_prop, props, features_test, angle_deg


# ─────────────────────────────────────────────────────────────────────────────
#  Q_class 3 — CLASSIFIEUR 1-NN (plus proche voisin)
# ─────────────────────────────────────────────────────────────────────────────

def classer_knn(vecteur, matrice_features, vecteur_classes, k=K_VOISINS):
    """
    Q_class 3 — Classifieur k-NN avec vote majoritaire.
    Retourne la classe prédite et la distance moyenne des k voisins.
    """
    distances = np.linalg.norm(matrice_features - vecteur, axis=1)
    k_eff = min(k, len(distances))
    idx_k = np.argpartition(distances, k_eff)[:k_eff]
    classes_k = vecteur_classes[idx_k].astype(int)
    votes = np.bincount(classes_k, minlength=NB_CLASSES)
    classe = int(np.argmax(votes))
    dist_moy = float(np.mean(distances[idx_k]))
    return classe, dist_moy


def classifier_code_1nn(features_test, matrice_features, vecteur_classes):
    """Classifie tous les chiffres d'un code postal avec le classifieur k-NN."""
    predictions = []
    distances   = []
    for vect in features_test:
        cl, dist = classer_knn(vect, matrice_features, vecteur_classes)
        predictions.append(cl)
        distances.append(dist)
    return predictions, distances


# ─────────────────────────────────────────────────────────────────────────────
#  Q_class 5 — CLASSIFIEUR PAR PLUS PROCHE MOYENNE (centroïde)
# ─────────────────────────────────────────────────────────────────────────────

def classer_moyenne(vecteur, matrice_moyennes):
    """
    Q_class 5 — Recherche de la plus proche moyenne (centroïde de classe).
    Retourne la classe prédite et la distance au centroïde.
    """
    distances = np.linalg.norm(matrice_moyennes - vecteur, axis=1)
    idx_min   = np.argmin(distances)
    return int(idx_min), float(distances[idx_min])


def classifier_code_moyenne(features_test, matrice_moyennes):
    """Classifie tous les chiffres d'un code postal avec le classifieur par moyenne."""
    predictions = []
    distances   = []
    for vect in features_test:
        cl, dist = classer_moyenne(vect, matrice_moyennes)
        predictions.append(cl)
        distances.append(dist)
    return predictions, distances


# ─────────────────────────────────────────────────────────────────────────────
#  Q_class 9 — SÉPARATION DES CHIFFRES QUI SE TOUCHENT
# ─────────────────────────────────────────────────────────────────────────────

def separer_chiffres_touches(bin_propre):
    """
    Q_class 9 — Détecte les composantes connexes dont le rapport largeur/hauteur
    est anormalement élevé (2 chiffres collés) et tente de les séparer par
    érosion verticale locale suivie de reconstruction.
    """
    img_lab, props = localiser_chiffres(bin_propre)
    bin_result = bin_propre.copy()

    for prop in props:
        minr, minc, maxr, maxc = prop.bbox
        h = maxr - minr
        w = maxc - minc
        if h == 0:
            continue
        ratio = w / h
        if ratio > RATIO_CONTACT:
            # Région suspecte : on applique une érosion verticale étroite
            # sur la portion centrale pour créer une coupure
            region = bin_result[minr:maxr, minc:maxc].copy()
            # Érosion par une colonne verticale de hauteur totale
            se_vertical = np.ones((h, 1), dtype=bool)
            # On cherche la colonne de moindre densité (vallée dans la projection)
            proj_h = region.sum(axis=0)
            # On cherche le minimum local dans la moitié centrale
            demi  = w // 4
            plage = proj_h[demi: w - demi]
            if len(plage) > 0:
                col_coupe = demi + int(np.argmin(plage))
                # Effacement d'une colonne de largeur 2 autour de la coupure
                c_abs = minc + col_coupe
                bin_result[minr:maxr, max(minc, c_abs-1):min(maxc, c_abs+2)] = False

    return bin_result


# ─────────────────────────────────────────────────────────────────────────────
#  AFFICHAGE — Code postal annoté dans l'image
# ─────────────────────────────────────────────────────────────────────────────

def afficher_code_postal(img_gris, bin_propre, props, predictions,
                         titre="Code postal reconnu", sauvegarde=None):
    """
    Affiche l'image originale avec les bounding boxes colorées et les chiffres
    reconnus annotés au-dessus de chaque région.
    """
    code_str = "".join(str(p) for p in predictions)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Panneau gauche : image grise + annotations
    axes[0].imshow(img_gris, cmap='gray', vmin=0, vmax=255)
    couleurs = plt.cm.tab10(np.linspace(0, 1, max(len(props), 1)))
    for i, (prop, pred) in enumerate(zip(props, predictions)):
        minr, minc, maxr, maxc = prop.bbox
        h, w = maxr - minr, maxc - minc
        rect = mpatches.Rectangle((minc, minr), w, h,
                                   linewidth=2, edgecolor=couleurs[i % 10],
                                   facecolor='none')
        axes[0].add_patch(rect)
        axes[0].text(minc + w//2, minr - 8, str(pred),
                     color='red', fontsize=16, fontweight='bold',
                     ha='center', va='bottom',
                     bbox=dict(boxstyle='round,pad=0.2',
                               facecolor='yellow', alpha=0.8))
    axes[0].set_title(f"{titre}\nCode postal lu : « {code_str} »",
                      fontsize=13, fontweight='bold')
    axes[0].axis('off')

    # Panneau droit : image binaire propre
    axes[1].imshow(bin_propre, cmap='gray')
    axes[1].set_title("Image binaire prétraitée", fontsize=12)
    axes[1].axis('off')

    plt.tight_layout()
    if sauvegarde:
        plt.savefig(sauvegarde, dpi=100, bbox_inches='tight')
    plt.show()
    return code_str


# ─────────────────────────────────────────────────────────────────────────────
#  VALIDATION — Calcul des métriques sur la base de test
# ─────────────────────────────────────────────────────────────────────────────

def valider_sur_base_test(matrice_features, vecteur_classes, matrice_moyennes,
                           feat_mean=None, feat_std=None,
                           mode='base', recalage=False, separation=False,
                           verbose=True, label_methode="1-NN"):
    """
    Q_class 4 & 6 — Parcourt toutes les images de DOSSIER_TEST,
    applique les deux classifieurs et retourne les résultats.
    """
    resultats = []   # liste de dicts
    fichiers_test = lister_images_dossier(DOSSIER_TEST)

    if verbose:
        print(f"  Dossier test : {DOSSIER_TEST}")
        print(f"  {len(fichiers_test)} image(s) trouvée(s)")

    for idx, trouve in enumerate(fichiers_test):
        nom = os.path.basename(trouve)

        img_gris, bin_prop, props, feats, angle = traiter_image_code(
            trouve, mode=mode,
            recalage_rotation=recalage,
            separer_contacts=separation
        )

        if len(feats) == 0:
            if verbose:
                print(f"  {nom} : aucun chiffre détecté")
            continue

        # Normaliser les features de test avec les mêmes paramètres
        feats_norm = feats
        if feat_mean is not None and feat_std is not None:
            feats_norm = (feats - feat_mean) / feat_std

        pred_1nn, dist_1nn   = classifier_code_1nn(feats_norm, matrice_features,
                                                    vecteur_classes)
        pred_moy, dist_moy   = classifier_code_moyenne(feats_norm, matrice_moyennes)

        code_1nn = "".join(str(p) for p in pred_1nn)
        code_moy = "".join(str(p) for p in pred_moy)

        resultats.append({
            'fichier'  : trouve,
            'nom'      : nom,
            'idx'      : idx,
            'img_gris' : img_gris,
            'bin_prop' : bin_prop,
            'props'    : props,
            'feats'    : feats,
            'pred_1nn' : pred_1nn,
            'pred_moy' : pred_moy,
            'code_1nn' : code_1nn,
            'code_moy' : code_moy,
            'angle'    : angle,
        })

        if verbose:
            print(f"  {nom} | {len(props)} chiffres | "
                  f"1-NN → {code_1nn}  |  Moy. → {code_moy}"
                  + (f"  [rot={angle:.1f}°]" if recalage and abs(angle) > 0.5 else ""))

    return resultats


# ─────────────────────────────────────────────────────────────────────────────
#  VISUALISATION — Comparaison 1-NN vs Moyenne (Q6)
# ─────────────────────────────────────────────────────────────────────────────

def afficher_comparaison(resultats, sauvegarde="comparaison_classifieurs.png"):
    """
    Q_class 6 — Affiche un tableau comparatif 1-NN vs Moyenne pour chaque image.
    """
    if not resultats:
        print("  Aucun résultat à afficher.")
        return

    nb = len(resultats)
    fig, axes = plt.subplots(nb, 2, figsize=(14, 3 * nb))
    if nb == 1:
        axes = axes.reshape(1, 2)

    for row, res in enumerate(resultats):
        for col, (preds, methode) in enumerate([
            (res['pred_1nn'], f"1-NN  → « {res['code_1nn']} »"),
            (res['pred_moy'], f"Moy.  → « {res['code_moy']} »"),
        ]):
            ax = axes[row, col]
            ax.imshow(res['img_gris'], cmap='gray', vmin=0, vmax=255)
            couleurs = plt.cm.tab10(np.linspace(0, 1, max(len(res['props']), 1)))
            for i, (prop, pred) in enumerate(zip(res['props'], preds)):
                minr, minc, maxr, maxc = prop.bbox
                h, w = maxr - minr, maxc - minc
                rect = mpatches.Rectangle((minc, minr), w, h,
                                           linewidth=1.5,
                                           edgecolor=couleurs[i % 10],
                                           facecolor='none')
                ax.add_patch(rect)
                ax.text(minc + w//2, minr - 5, str(pred),
                        color='red', fontsize=13, fontweight='bold',
                        ha='center',
                        bbox=dict(boxstyle='round,pad=0.1',
                                  facecolor='yellow', alpha=0.7))
            titre_img = f"{res['nom']} | {methode}"
            ax.set_title(titre_img, fontsize=10)
            ax.axis('off')

    plt.suptitle("Q_class 6 — Comparaison 1-NN vs Plus proche Moyenne",
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(sauvegarde, dpi=100, bbox_inches='tight')
    plt.show()
    print(f"  Figure sauvegardée : {sauvegarde}")


# ─────────────────────────────────────────────────────────────────────────────
#  VISUALISATION — Espace de décision 2D (Q1)
# ─────────────────────────────────────────────────────────────────────────────

def visualiser_espace_decision(matrice_features, vecteur_classes,
                                matrice_moyennes,
                                idx_x=0, idx_y=1,
                                noms_attr=None,
                                sauvegarde="espace_decision.png"):
    """
    Q_class 1 — Projette les prototypes et les centroïdes dans un plan 2D
    défini par deux attributs (idx_x, idx_y).
    """
    if noms_attr is None:
        noms_attr = ['Cav.Centre','Cav.Est','Cav.Ouest','Cav.Nord','Cav.Sud',
                     'Excentr.','Solidité','Rapp.Aspect','Rondeur','Euler']

    fig, ax = plt.subplots(figsize=(10, 8))
    cmap   = plt.cm.get_cmap('tab10', NB_CLASSES)
    colors = [cmap(c) for c in range(NB_CLASSES)]

    for c in range(NB_CLASSES):
        idx = vecteur_classes == c
        if not np.any(idx):
            continue
        x = matrice_features[idx, idx_x]
        y = matrice_features[idx, idx_y]
        ax.scatter(x, y, color=colors[c], alpha=0.5, s=60,
                   label=f"Chiffre {c}")
        # Centroïde
        cx, cy = matrice_moyennes[c, idx_x], matrice_moyennes[c, idx_y]
        ax.scatter(cx, cy, color=colors[c], edgecolors='black',
                   s=200, marker='*', zorder=5)
        ax.annotate(str(c), (cx, cy),
                    textcoords='offset points', xytext=(6, 6),
                    fontsize=12, fontweight='bold', color=colors[c])

    ax.set_xlabel(noms_attr[idx_x] if idx_x < len(noms_attr) else f"Attr. {idx_x}",
                  fontsize=12)
    ax.set_ylabel(noms_attr[idx_y] if idx_y < len(noms_attr) else f"Attr. {idx_y}",
                  fontsize=12)
    ax.set_title("Q_class 1 — Espace de décision (prototypes + centroïdes ★)",
                 fontsize=13, fontweight='bold')
    ax.legend(loc='upper right', fontsize=9)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(sauvegarde, dpi=100, bbox_inches='tight')
    plt.show()
    print(f"  Figure sauvegardée : {sauvegarde}")


# ─────────────────────────────────────────────────────────────────────────────
#  PROGRAMME PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":

    print(f" Train : {DOSSIER_TRAIN}")
    print(f" Test  : {DOSSIER_TEST}")

    # ══════════════════════════════════════════════════════════════════════════
    # Q_class 1 — ESPACE DE DÉCISION : explication
    # ══════════════════════════════════════════════════════════════════════════
    print("=" * 60)
    print("Q_class 1 — Espace de décision")
    print("=" * 60)
    print("""
  Espace de décision proposé : R^5 (puis R^10 en Q7)

  Chaque chiffre est représenté par un vecteur de 5 attributs :
    attr[0] = Surface_CENTRE / Surface_Chiffre  (cavité centrale)
    attr[1] = Surface_EST    / Surface_Chiffre  (cavité droite)
    attr[2] = Surface_OUEST  / Surface_Chiffre  (cavité gauche)
    attr[3] = Surface_NORD   / Surface_Chiffre  (cavité haute)
    attr[4] = Surface_SUD    / Surface_Chiffre  (cavité basse)

  La normalisation par la surface du chiffre rend les attributs
  invariants à la taille (zoom, résolution).

  Intuition par chiffre :
    0 → grande cavité CENTRE
    1 → toutes les cavités ≈ 0 (plein)
    6 → cavité SUD dominante
    8 → deux cavités (CENTRE élevée, autres faibles)
    9 → cavité NORD dominante
    ...
""")

    # ══════════════════════════════════════════════════════════════════════════
    # Q_class 2 — APPRENTISSAGE HORS-LIGNE (mode base)
    # ══════════════════════════════════════════════════════════════════════════
    mat_feat, vec_cls, mat_moy, f_mean, f_std = apprentissage(mode='base', verbose=True)

    if mat_feat is None:
        print("\n  ARRÊT : base d'apprentissage introuvable.")
        print(f"  Vérifiez le dossier : {DOSSIER_TRAIN}")
        exit(1)

    # Visualisation de l'espace de décision (Q1 — graphique)
    visualiser_espace_decision(mat_feat, vec_cls, mat_moy,
                                idx_x=0, idx_y=4,   # Cavité Centre vs Sud
                                sauvegarde="q1_espace_decision.png")

    # Projection sur 2 autres axes (Est vs Ouest)
    visualiser_espace_decision(mat_feat, vec_cls, mat_moy,
                                idx_x=1, idx_y=2,   # Cavité Est vs Ouest
                                sauvegarde="q1_espace_decision_EO.png")

    # ══════════════════════════════════════════════════════════════════════════
    # Q_class 3 & 4 — CLASSIFICATION 1-NN + VALIDATION
    # ══════════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 60)
    print("Q_class 3 & 4 — Classifieur 1-NN + Validation")
    print("=" * 60)

    resultats_base = valider_sur_base_test(
        mat_feat, vec_cls, mat_moy, f_mean, f_std,
        mode='base', recalage=False, separation=False,
        verbose=True, label_methode="k-NN"
    )

    # Affichage annoté de chaque image (1-NN)
    for res in resultats_base:
        sauveg = f"q4_1nn_{os.path.splitext(res['nom'])[0]}.png"
        afficher_code_postal(
            res['img_gris'], res['bin_prop'], res['props'], res['pred_1nn'],
            titre=f"1-NN — {res['nom']}",
            sauvegarde=sauveg
        )

    # ══════════════════════════════════════════════════════════════════════════
    # Q_class 5 & 6 — CLASSIFIEUR PAR MOYENNE + COMPARAISON
    # ══════════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 60)
    print("Q_class 5 & 6 — Classifieur par Moyenne + Comparaison")
    print("=" * 60)

    # La validation déjà faite contient aussi les résultats Moyenne
    # On réaffiche la comparaison côte à côte
    afficher_comparaison(resultats_base,
                         sauvegarde="q6_comparaison_1nn_moy.png")

    # Analyse comparative
    print("\n  ANALYSE — Comparaison 1-NN vs Plus proche Moyenne :")
    print(f"  {'Fichier':<30} | {'1-NN':^12} | {'Moyenne':^12}")
    print("  " + "-" * 60)
    for res in resultats_base:
        accord = "✓" if res['code_1nn'] == res['code_moy'] else "≠"
        print(f"  {res['nom']:<30} | {res['code_1nn']:^12} | "
              f"{res['code_moy']:^12}  {accord}")

    print("""
  CONCLUSION :
    - Le classifieur 1-NN est plus précis localement : il tient compte de
      la distribution réelle des prototypes, pas seulement du centroïde.
    - La méthode par Moyenne est plus rapide (O(nb_classes) vs O(nb_proto))
      et moins sensible aux prototypes aberrants.
    - Avec peu de prototypes (5/classe), les deux méthodes donnent souvent
      des résultats proches. La différence apparaît sur les cas limites.
""")

    # ══════════════════════════════════════════════════════════════════════════
    # Q_class 7 — ATTRIBUTS ENRICHIS (regionprops, invariants à l'échelle)
    # ══════════════════════════════════════════════════════════════════════════
    print("=" * 60)
    print("Q_class 7 — Attributs enrichis (regionprops)")
    print("=" * 60)
    print("""
  Attributs ajoutés (tous invariants à l'échelle) :
    [5] Excentricité   : 0=cercle parfait, 1=segment (forme allongée)
    [6] Solidité       : aire_réelle / aire_convexe  → compacité
    [7] Rapport d'axe  : axe_min / axe_maj           → rondeur de la forme
    [8] Rondeur        : 4π·aire / périmètre²         → circularité isopérimétrique
    [9] Euler normalisé: proxy du nombre de trous fermés (0=plein, 1=3+ trous)

  Ces attributs permettent de distinguer par exemple :
    - 0 vs 8 (un trou vs deux trous → Euler différent)
    - 1 vs 7 (excentricité et rapport d'axe très différents)
    - 3 vs 5 (rondeur et solidité différentes)
""")

    mat_feat_e, vec_cls_e, mat_moy_e, f_mean_e, f_std_e = apprentissage(mode='enrichi', verbose=True)

    if mat_feat_e is not None:
        # Validation avec attributs enrichis
        print("\n  Validation avec attributs enrichis :")
        resultats_enrich = valider_sur_base_test(
            mat_feat_e, vec_cls_e, mat_moy_e, f_mean_e, f_std_e,
            mode='enrichi', recalage=False, separation=False,
            verbose=True
        )

        # Espace de décision enrichi : projection Excentricité vs Solidité
        noms = ['Cav.Centre','Cav.Est','Cav.Ouest','Cav.Nord','Cav.Sud',
                'Excentr.','Solidité','Rapp.Aspect','Rondeur','Euler']
        visualiser_espace_decision(mat_feat_e, vec_cls_e, mat_moy_e,
                                    idx_x=5, idx_y=6,  # Excentricité vs Solidité
                                    noms_attr=noms,
                                    sauvegarde="q7_espace_enrichi.png")

    # ══════════════════════════════════════════════════════════════════════════
    # Q_class 8 — RECALAGE EN ROTATION
    # ══════════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 60)
    print("Q_class 8 — Recalage en rotation")
    print("=" * 60)
    print("""
  Principe :
    1. Détecter les pixels des chiffres dans l'image brute.
    2. Calculer la matrice de covariance des coordonnées (y, x).
    3. Extraire le vecteur propre dominant → axe principal d'inertie.
    4. Calculer l'angle de cet axe par rapport à l'horizontale.
    5. Pivoter l'image du même angle en sens inverse (correction).
    6. Re-lancer le pipeline de classification sur l'image corrigée.
""")

    resultats_rot = valider_sur_base_test(
        mat_feat, vec_cls, mat_moy, f_mean, f_std,
        mode='base', recalage=True, separation=False,
        verbose=True, label_methode="k-NN + Rotation"
    )

    for res in resultats_rot:
        if abs(res['angle']) > 0.5:
            sauveg = f"q8_rotation_{os.path.splitext(res['nom'])[0]}.png"
            afficher_code_postal(
                res['img_gris'], res['bin_prop'], res['props'], res['pred_1nn'],
                titre=f"Q8 — {res['nom']} après recalage rotation ({res['angle']:.1f}°)",
                sauvegarde=sauveg
            )
            print(f"  {res['nom']} → angle corrigé : {res['angle']:.2f}°")

    # ══════════════════════════════════════════════════════════════════════════
    # Q_class 9 — SÉPARATION DES CHIFFRES QUI SE TOUCHENT
    # ══════════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 60)
    print("Q_class 9 — Séparation des chiffres qui se touchent")
    print("=" * 60)
    print(f"""
  Principe :
    1. Après étiquetage, si une composante a un rapport largeur/hauteur
       supérieur à {RATIO_CONTACT:.1f}, elle est considérée comme une fusion.
    2. On calcule la projection horizontale (somme par colonne).
    3. On cherche le minimum local dans la zone centrale → point de coupure.
    4. On efface une colonne de pixels à ce point pour séparer les deux.
    5. Ré-étiquetage → deux composantes distinctes.
""")

    resultats_sep = valider_sur_base_test(
        mat_feat, vec_cls, mat_moy, f_mean, f_std,
        mode='base', recalage=False, separation=True,
        verbose=True, label_methode="k-NN + Séparation"
    )

    for res in resultats_sep:
        sauveg = f"q9_separation_{os.path.splitext(res['nom'])[0]}.png"
        afficher_code_postal(
            res['img_gris'], res['bin_prop'], res['props'], res['pred_1nn'],
            titre=f"Q9 — {res['nom']} (séparation contacts activ.)",
            sauvegarde=sauveg
        )

    # ══════════════════════════════════════════════════════════════════════════
    # RÉSUMÉ FINAL
    # ══════════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 60)
    print("RÉSUMÉ DU TP — Résultats sur la base de test")
    print("=" * 60)
    print(f"  {'Fichier':<30} | {'1-NN':^12} | {'Moy.':^12} | "
          f"{'1-NN+Rot':^12} | {'1-NN+Sep':^12}")
    print("  " + "-" * 86)

    d_base = {r['idx']: r for r in resultats_base}
    d_rot  = {r['idx']: r for r in resultats_rot}
    d_sep  = {r['idx']: r for r in resultats_sep}

    for idx in sorted(d_base.keys()):
        rb = d_base[idx]
        rr = d_rot.get(idx)
        rs = d_sep.get(idx)
        code_rot = rr['code_1nn'] if rr else "—"
        code_sep = rs['code_1nn'] if rs else "—"
        print(f"  {rb['nom']:<30} | {rb['code_1nn']:^12} | {rb['code_moy']:^12} | "
              f"{code_rot:^12} | {code_sep:^12}")

    fichiers_gen = (
        ["q1_espace_decision.png", "q1_espace_decision_EO.png",
         "q6_comparaison_1nn_moy.png", "q7_espace_enrichi.png"]
        + [f"q4_1nn_{os.path.splitext(r['nom'])[0]}.png"   for r in resultats_base]
        + [f"q8_rotation_{os.path.splitext(r['nom'])[0]}.png"
           for r in resultats_rot if abs(r['angle']) > 0.5]
        + [f"q9_separation_{os.path.splitext(r['nom'])[0]}.png" for r in resultats_sep]
    )
    print("\n  Fichiers générés :")
    for f in fichiers_gen:
        print(f"    {f}")

    # ══════════════════════════════════════════════════════════════════════════
    # MÉTRIQUES DE PERFORMANCE
    # ══════════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 60)
    print("MÉTRIQUES DE PERFORMANCE")
    print("=" * 60)

    methodes = [
        ("k-NN (base)",       resultats_base, 'pred_1nn'),
        ("Moyenne (base)",    resultats_base, 'pred_moy'),
        ("k-NN + Rotation",   resultats_rot,  'pred_1nn'),
        ("k-NN + Séparation", resultats_sep,  'pred_1nn'),
    ]

    for nom_methode, resultats, cle_pred in methodes:
        y_vrai_chiffres = []
        y_pred_chiffres = []
        nb_codes_exact  = 0
        nb_codes_total  = 0

        for res in resultats:
            nom_fich = os.path.splitext(res['nom'])[0]
            code_attendu = nom_fich.split('_')[0]
            if not code_attendu.isdigit():
                continue

            preds = res[cle_pred]
            code_predit = "".join(str(p) for p in preds)

            nb_codes_total += 1
            if code_predit == code_attendu:
                nb_codes_exact += 1

            n = min(len(code_attendu), len(preds))
            for i in range(n):
                y_vrai_chiffres.append(int(code_attendu[i]))
                y_pred_chiffres.append(int(preds[i]))

        y_vrai = np.array(y_vrai_chiffres)
        y_pred = np.array(y_pred_chiffres)

        if len(y_vrai) == 0:
            continue

        acc_chiffre = np.mean(y_vrai == y_pred) * 100
        acc_code    = (nb_codes_exact / nb_codes_total * 100
                       if nb_codes_total > 0 else 0)

        print(f"\n  ── {nom_methode} ──")
        print(f"  Accuracy par chiffre  : {acc_chiffre:.1f}% "
              f"({np.sum(y_vrai == y_pred)}/{len(y_vrai)})")
        print(f"  Accuracy par code     : {acc_code:.1f}% "
              f"({nb_codes_exact}/{nb_codes_total})")

        # Matrice de confusion (texte)
        conf = np.zeros((NB_CLASSES, NB_CLASSES), dtype=int)
        for v, p in zip(y_vrai, y_pred):
            conf[v, p] += 1
        print(f"\n  Matrice de confusion ({nom_methode}) :")
        header = "  Vrai\\Préd |  " + "  ".join(f"{c:>3}" for c in range(NB_CLASSES))
        print(header)
        print("  " + "-" * len(header))
        for c in range(NB_CLASSES):
            vals = "  ".join(f"{conf[c, j]:>3}" for j in range(NB_CLASSES))
            print(f"  {c:>9} |  {vals}")

        # Matrice de confusion (graphique)
        fig, ax = plt.subplots(figsize=(8, 7))
        im = ax.imshow(conf, cmap='Blues', interpolation='nearest')
        ax.set_xticks(range(NB_CLASSES))
        ax.set_yticks(range(NB_CLASSES))
        ax.set_xlabel("Classe prédite", fontsize=12)
        ax.set_ylabel("Classe réelle", fontsize=12)
        ax.set_title(f"Matrice de confusion — {nom_methode}\n"
                     f"Acc. chiffre = {acc_chiffre:.1f}%  |  "
                     f"Acc. code = {acc_code:.1f}%",
                     fontsize=13, fontweight='bold')
        for i in range(NB_CLASSES):
            for j in range(NB_CLASSES):
                val = conf[i, j]
                color = 'white' if val > conf.max() / 2 else 'black'
                ax.text(j, i, str(val), ha='center', va='center',
                        fontsize=11, fontweight='bold', color=color)
        fig.colorbar(im, ax=ax, shrink=0.8)
        plt.tight_layout()
        sauveg_conf = f"confusion_{nom_methode.replace(' ', '_').replace('(', '').replace(')', '')}.png"
        plt.savefig(sauveg_conf, dpi=100, bbox_inches='tight')
        plt.show()
        print(f"  Figure sauvegardée : {sauveg_conf}")
        fichiers_gen.append(sauveg_conf)

    print("\nTP terminé.")
