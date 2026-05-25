import streamlit as st
import streamlit.components.v1 as components
from groq import Groq

# -------------------------
# CONFIGURATION DE LA PAGE
# -------------------------
st.set_page_config(page_title="UXIntelligence IA Pro", page_icon="⚡", layout="wide")

# Masquer la sidebar par défaut pour un look épuré
st.markdown("""
<style>
[data-testid="stSidebar"] {display: none !important;}
[data-testid="stSidebarNav"] {display: none !important;}
@import url('https://googleapis.com');
html, body, div, p, h1, h2, h3, h4, h5, h6, span {
    font-family: 'Poppins', sans-serif !important;
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# CONFIGURATION PAYPAL
# -------------------------
PAYPAL_CLIENT_ID = "DEMO"  # À remplacer ce week-end
PAYPAL_PLAN_ID = "DEMO"    # À remplacer ce week-end (Abonnement à 50$/mois)

# -------------------------
# GESTION DE L'ACCÈS
# -------------------------
if "est_abonne" not in st.session_state:
    st.session_state.est_abonne = False

try:
    API_KEY = st.secrets["GROQ_API_KEY"]
except:
    API_KEY = ""

# -------------------------
# INTERFACE SÉCURISÉE
# -------------------------
st.title("⚡ UXIntelligence IA — Analyse de l'Expérience Client")

# CAS 1 : L'UTILISATEUR N'A PAS PAYÉ
if not st.session_state.est_abonne:
    st.warning("🔒 Cette application est réservée aux membres de la version Premium.")
    
    col_offre, col_connexion = st.columns(2, gap="large")
    
    with col_offre:
        st.subheader("🚀 Débloquez l'IA pour 50 $/mois")
        st.write("Détectez instantanément les pannes sur vos pages, comprenez l'abandon de panier et optimisez le parcours de vos acheteurs.")
        st.write("Le paiement est entièrement sécurisé par **PayPal**.")
        
        if PAYPAL_CLIENT_ID == "DEMO":
            paypal_html = """
            <a href="https://paypal.com" target="_blank" style="text-decoration: none;">
                <div style="background-color: #ffc439; color: #003087; text-align: center; 
                            padding: 12px; font-family: Arial, sans-serif; font-weight: bold; 
                            border-radius: 4px; max-width: 300px; cursor: pointer; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    🟨 S'abonner avec PayPal (50$/mois)
                </div>
            </a>
            """
        else:
            paypal_html = f"""
            <div id="paypal-button-container-fixed" style="max-width: 350px; margin-top: 20px;"></div>
            <script src="https://paypal.com{PAYPAL_CLIENT_ID}&vault=true&intent=subscription" data-sdk-integration-source="button-factory"></script>
            <script>
              paypal.Buttons({{
                  style: {{ shape: 'rect', color: 'gold', layout: 'vertical', label: 'subscribe' }},
                  createSubscription: function(data, actions) {{
                    return actions.subscription.create({{ 'plan_id': '{PAYPAL_PLAN_ID}' }});
                  }},
                  onApprove: function(data, actions) {{
                    alert('Abonnement réussi ! ID : ' + data.subscriptionID);
                  }}
              }}).render('#paypal-button-container-fixed');
            </script>
            """
        
        components.html(paypal_html, height=150, scrolling=False)
        
    with col_connexion:
        st.subheader("🔑 Déjà abonné ?")
        st.write("Connectez-vous pour activer vos accès.")
        email = st.text_input("Adresse e-mail", key="login_email")
        mot_de_passe = st.text_input("Mot de passe", type="password", key="login_password")
        
        if st.button("Se connecter", use_container_width=True):
            if email == "test@client.com" and mot_de_passe == "access50":
                st.session_state.est_abonne = True
                st.success("Accès accordé ! Chargement...")
                st.button("👉 Cliquer ici pour entrer")
            else:
                st.error("Identifiants incorrects ou abonnement PayPal inactif.")

# CAS 2 : L'UTILISATEUR EST ABONNÉ -> ACCÈS COMPLET
else:
    st.write("✨ **Bienvenue dans votre espace Premium.** L'analyse d'expérience utilisateur est active.")
    if st.button("🚪 Se déconnecter", key="logout"):
        st.session_state.est_abonne = False
        st.rerun()
        
    st.write("---")

    with st.container(border=True):
        col_input, col_stats = st.columns(2)
        
        with col_input:
            url_boutique = st.text_input("URL de la page ou étape analysée", placeholder="Ex: ://maboutique.com")
            etape_blocage = st.selectbox("Où les clients abandonnent-ils le plus ?", [
                "🛒 Page Panier (Avant de cliquer sur Paiement)",
                "🚚 Choix de la Livraison (Frais trop élevés ?)",
                "💳 Formulaire de Paiement (Erreur de carte / Refus)",
                "📱 Navigation Mobile (Boutons invisibles ou mal alignés)"
            ])
            
        with col_stats:
            temps_chargement = st.slider("Temps de chargement moyen de la page (en secondes)", 1.0, 15.0, 3.5, step=0.1)
            taux_abandon = st.slider("Taux de panier abandonné constaté (%)", 10, 95, 68)

        generer = st.button("🚀 Diagnostiquer le Parcours Client & Obtenir les Fixes IA", use_container_width=True)

    if generer:
        if not API_KEY:
            st.error("⚠️ Erreur : La clé GROQ_API_KEY est manquante dans les Secrets du serveur.")
        elif not url_boutique:
            st.error("⚠️ Veuillez indiquer l'URL ou le nom de la boutique.")
        else:
            with st.spinner("L'IA de Groq scanne le comportement des utilisateurs..."):
                try:
                    client = Groq(api_key=API_KEY)
                    
                    prompt_systeme = """Tu es un ingénieur expert en conversion e-commerce (CRO) et en expérience utilisateur (UX).
                    Tu dois obligatoirement formater ta réponse sous forme de tableau Markdown avec exactement 3 colonnes :
                    1. **Problème Identifié** (Analyse de la vitesse et de l'étape de blocage)
                    2. **Impact sur les Ventes** (Pourquoi cela fait perdre de l'argent)
                    3. **Solution Technique Immédiate** (Ce qu'il faut modifier sur le site pour réparer le problème)
                    Ne fais aucune intro ou conclusion."""

                    prompt_utilisateur = f"""
                    Page ciblée : {url_boutique}
                    Étape critique d'abandon : {etape_blocage}
                    Temps de chargement de la page : {temps_chargement} secondes
                    Taux d'abandon mesuré : {taux_abandon}%
                    """

                    reponse = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {"role": "system", "content": prompt_systeme},
                            {"role": "user", "content": prompt_utilisateur}
                        ],
                        temperature=0.4
                    )
                    
                    script_genere = reponse.choices[0].message.content
                    st.success("✨ Diagnostic d'expérience client terminé !")
                    st.markdown(script_genere)
                    st.text_area("Copier le rapport UX brut :", value=script_genere, height=200)

                except Exception as e:
                    st.error(f"Erreur technique Groq : {str(e)}")
