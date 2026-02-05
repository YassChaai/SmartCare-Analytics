# 🎨 Design System - Style Nike

## 🎯 Philosophie de Design

Le dashboard Smart Care utilise un design **Nike-style** : minimaliste, impactant, noir/blanc/orange, avec une hiérarchie typographique forte.

---

## 🎨 Palette de Couleurs

### Couleurs Principales

```css
--nike-black: #111111       /* Texte principal */
--nike-white: #FFFFFF       /* Fond */
--nike-orange: #FF5700      /* Accent */
--nike-gray: #7E7E7E        /* Texte secondaire */
--nike-light-gray: #F5F5F5  /* Surfaces */
--nike-dark-gray: #2F2F2F   /* Bordures */
```

### Gradients Signature

```css
/* Gradient principal Noir → Gris */
linear-gradient(135deg, #111111 0%, #2F2F2F 100%)

/* Gradient accent Orange */
linear-gradient(135deg, #FF5700 0%, #FF8C00 100%)
```

### Couleurs d'État

| État | Couleur | Usage |
|------|---------|-------|
| 🔴 Critique | `#D32F2F` | Alertes danger, occupation >85% |
| 🟠 Attention | `#FF5700` | Avertissements, besoins |
| 🟢 Normal | `#388E3C` | État sain, confirmations |
| 🔵 Info | `#111111` | Informations, données |

---

## 🎭 Composants

### 1. Headers (Titres)

#### Header Principal (Hero)
```css
font-size: 3rem
font-weight: 900
color: #111111
letter-spacing: -1px
text-transform: uppercase
border-bottom: 4px solid #FF5700
```

**Exemple** :
```html
<h1 style="...">SMART CARE COMMAND CENTER</h1>
```

#### Headers de Section
```css
color: #111111
font-size: 1.3rem
font-weight: 700
letter-spacing: 0.5px
text-transform: uppercase
```

### 2. Cartes Métriques (KPIs)

```css
background: #FFFFFF
border: 1px solid #E5E5E5
border-radius: 0
box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08)
transition: all 0.2s ease
```

**Effet hover** :
```css
transform: translateY(-4px)
border-color: #111111
box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12)
```

**Animation shine** : Effet de lumière qui traverse la carte

### 3. Alertes

#### Alerte Danger (Critique)
```css
background: #FFEBEE
border-left: 4px solid #D32F2F
```

#### Alerte Warning (Attention)
```css
background: #FFF3E0
border-left: 4px solid #FF5700
```

#### Alerte Success (Normal)
```css
background: #E8F5E9
border-left: 4px solid #388E3C
```

### 4. Boutons

#### Style Principal
```css
background: #111111
color: #FFFFFF
border: none
border-radius: 0
font-weight: 700
text-transform: uppercase
letter-spacing: 1.5px
box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15)
```

#### Hover Effect
```css
background: #FF5700
color: #FFFFFF
transform: translateY(-3px)
box-shadow: 0 4px 16px rgba(255, 87, 0, 0.3)
```

### 5. Badges

```css
.kc-badge {
    background: linear-gradient(135deg, #2E3FE8 0%, #FFD700 100%)
    padding: 8px 16px
    border-radius: 20px
    font-weight: 700
    text-transform: uppercase
    font-size: 0.85rem
    letter-spacing: 1px
    animation: float 3s ease-in-out infinite
}
```

**Exemple** :
```html
<span class="kc-badge">DASHBOARD v2.0</span>
```

### 6. Tabs (Onglets)

#### Style Inactif
```css
background: transparent
border: 2px solid rgba(46, 63, 232, 0.3)
border-radius: 8px
color: #ffffff
```

#### Style Actif
```css
background: linear-gradient(135deg, #2E3FE8 0%, #1a237e 100%)
border-color: #FFD700
box-shadow: 0 4px 15px rgba(46, 63, 232, 0.5)
```

---

## ✨ Animations

### 1. Glow (Lueur pulsante)
```css
@keyframes glow {
    from { filter: drop-shadow(0 0 5px rgba(46, 63, 232, 0.5)); }
    to { filter: drop-shadow(0 0 20px rgba(46, 63, 232, 0.8)); }
}
```

**Usage** : Headers principaux, éléments importants

### 2. Pulse (Pulsation)
```css
@keyframes pulse {
    0%, 100% { box-shadow: 0 4px 16px rgba(244, 67, 54, 0.3); }
    50% { box-shadow: 0 4px 24px rgba(244, 67, 54, 0.6); }
}
```

**Usage** : Alertes critiques

### 3. Shine (Brillance)
```css
@keyframes shine {
    0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
    100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
}
```

**Usage** : Cartes métriques (effet de lumière qui traverse)

### 4. Float (Flottement)
```css
@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-5px); }
}
```

**Usage** : Badges, éléments décoratifs

---

## 🎨 Effets Visuels

### Glassmorphism (Effet de verre)
```css
backdrop-filter: blur(10px)
background: rgba(46, 63, 232, 0.1)
border: 1px solid rgba(46, 63, 232, 0.3)
```

### Text Gradient (Texte dégradé)
```css
background: linear-gradient(135deg, #2E3FE8 0%, #FFD700 100%)
-webkit-background-clip: text
-webkit-text-fill-color: transparent
```

### Box Shadow (Ombres)
```css
/* Ombre douce */
box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2)

/* Ombre forte (hover) */
box-shadow: 0 12px 48px rgba(46, 63, 232, 0.4)

/* Ombre colorée (bouton) */
box-shadow: 0 4px 15px rgba(46, 63, 232, 0.4)
```

---

## 📏 Typographie

### Police
```css
font-family: 'Inter', sans-serif
```

### Tailles

| Élément | Taille | Poids |
|---------|--------|-------|
| Hero Title | 3.5rem | 900 |
| Section Header | 1.5rem | 700 |
| Metric Value | 2.5rem | 900 |
| Body Text | 1rem | 400 |
| Small Text | 0.9rem | 400 |

### Letterspacing

| Usage | Valeur |
|-------|--------|
| Titres principaux | -1px |
| Headers section | 0.5px |
| Boutons/Badges | 1.5px |

---

## 🌈 Thématique

### Light Theme (Principal)
```css
background: #FFFFFF
color: #111111
```

### Sidebar (masquée)
```css
display: none
```

---

## 🎯 Composants Streamlit Customisés

### Métriques
```css
[data-testid="stMetricValue"] {
    font-size: 2.5rem
    font-weight: 900
    color: #111111
}
```

### Sliders
```css
.stSlider [data-baseweb="slider"] {
    background: linear-gradient(135deg, #111111 0%, #2F2F2F 100%)
}
```

### Expanders
```css
.streamlit-expanderHeader {
    background: #F5F5F5
    border: 1px solid #E5E5E5
    color: #111111
}
```

---

## 🎮 Scrollbar Personnalisée

```css
::-webkit-scrollbar {
    width: 10px
}

::-webkit-scrollbar-track {
    background: rgba(10, 14, 39, 0.5)
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg, #2E3FE8 0%, #FFD700 100%)
    border-radius: 5px
}
```

---

## 📦 Templates Prêts à l'Emploi

### Box d'Information
```html
<div style="
    background: linear-gradient(135deg, rgba(46, 63, 232, 0.15) 0%, rgba(26, 35, 126, 0.15) 100%);
    border: 1px solid rgba(46, 63, 232, 0.3);
    border-radius: 12px;
    padding: 15px;
    backdrop-filter: blur(10px);
">
    <p style="color: #FFD700; font-weight: 700;">TITRE</p>
    <p style="color: #e0e0e0;">Contenu...</p>
</div>
```

### Badge Status
```html
<span style="
    background: linear-gradient(135deg, #2E3FE8 0%, #FFD700 100%);
    padding: 5px 12px;
    border-radius: 15px;
    color: white;
    font-weight: 700;
    font-size: 0.8rem;
">STATUS</span>
```

### Section Header
```html
<div style="text-align: center; margin: 30px 0 20px 0;">
    <h2 style="
        color: #FFD700;
        font-size: 1.5rem;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
    ">🚨 TITRE SECTION</h2>
</div>
```

---

## 🎨 Configuration Plotly

Pour harmoniser les graphiques avec le thème :

```python
fig.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#e0e0e0'),
    legend=dict(
        bgcolor='rgba(46, 63, 232, 0.1)',
        bordercolor='rgba(46, 63, 232, 0.3)',
        borderwidth=1
    )
)
```

### Couleurs de ligne
```python
line=dict(color='#2E3FE8', width=3)  # Ligne bleue
line=dict(color='#FFD700', width=3)  # Ligne or
```

---

## ✅ Checklist d'Intégration

Lors de l'ajout de nouveaux composants, vérifier :

- [ ] Utilisation de la palette de couleurs Karmine
- [ ] Effet hover sur les éléments interactifs
- [ ] Backdrop blur pour les cartes
- [ ] Border-radius arrondi (10-15px)
- [ ] Box shadow pour la profondeur
- [ ] Transitions douces (0.3s ease)
- [ ] Typographie cohérente (Inter font)
- [ ] Couleurs de texte (#e0e0e0 pour body, #FFD700 pour headers)
- [ ] Graphiques avec fond transparent
- [ ] Animations subtiles si approprié

---

## 🚀 Évolutions Futures

### Idées d'améliorations
- [ ] Mode clair/sombre toggle
- [ ] Particules animées en arrière-plan
- [ ] Sons de notification (optionnel)
- [ ] Transitions de page animées
- [ ] Loading states personnalisés
- [ ] Micro-interactions sur les boutons
- [ ] Thème personnalisable par l'utilisateur

---

## 📚 Ressources

- **Police** : [Inter Font](https://fonts.google.com/specimen/Inter)
- **Inspiration** : Karmine Corp branding, Gaming UI, Modern dashboards
- **Outils** : CSS Gradient Generator, Color Picker, Animation Inspector

---

**Style créé pour Smart Care Dashboard - Projet DATA EPITECH 2026**

*"Un design qui inspire confiance et performance"* ⚡
