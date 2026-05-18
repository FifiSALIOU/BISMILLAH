from typing import Dict, List, Optional, Tuple
import re
import random
from difflib import SequenceMatcher
from app.utils.logging import logger

class PredefinedQASystem:
    """Système de questions-réponses prédéfinies pour éviter les appels LLM inutiles"""
    
    def __init__(self):
        self.qa_database = {
            "Bonjour": {
                "answers": [
                    "Bonjour ! Comment puis-je vous aider aujourd'hui ?",
                    "Salut ! Que puis-je faire pour vous ?",
                    "Bonjour ! Je suis là pour vous assister.",
                    "Hello ! En quoi puis-je vous être utile ?",
                    "Bonjour ! Bienvenue sur l'assistance CSS AI.",
                    "Salut ! Je suis à votre disposition pour toute question.",
                    "Bonjour ! Comment allez-vous ? Que puis-je faire pour vous ?",
                    "Hello ! Ravi de vous accueillir. Comment puis-je vous aider ?",
                    "Bonjour ! N'hésitez pas à me poser vos questions CSS.",
                    "Salut ! Je suis votre assistant CSS AI, comment puis-je vous aider ?"
                ],
                "keywords": ["Bonjour", "salutation"],
                "confidence": 0.95
            },

            "Salut": {
                "answers": [
                    "Salut ! Comment puis-je vous aider aujourd'hui ?",
                    "Hey ! Que puis-je faire pour vous ?",
                    "Salut ! Je suis à votre service.",
                    "Coucou ! Comment puis-je vous assister ?",
                    "Salut ! Bienvenue, comment ça va ?",
                    "Hey ! Je suis là pour vous accompagner.",
                    "Salut ! Que souhaitez-vous savoir sur la CSS ?",
                    "Hello ! Comment puis-je vous être utile ?",
                    "Salut ! Votre assistant CSS AI à votre service.",
                    "Hey ! N'hésitez pas à me poser vos questions."
                ],
                "keywords": ["Salut", "salutation"],
                "confidence": 0.95
            },

            "Comment ça va": {
                "answers": [
                    "Bien, merci ! Comment puis-je vous aider aujourd'hui ?",
                    "Ça va très bien ! Et vous, comment allez-vous ?",
                    "Tout va bien de mon côté ! Que puis-je faire pour vous ?",
                    "Parfaitement bien ! En quoi puis-je vous être utile ?",
                    "Ça va super ! Comment puis-je vous assister ?",
                    "Très bien merci ! Et vous ? Que puis-je faire pour vous ?",
                    "Tout roule ! Comment puis-je vous aider avec la CSS ?",
                    "Ça va parfaitement ! Quelle est votre question ?",
                    "Excellente journée ! Comment puis-je vous accompagner ?",
                    "Ça va bien ! Je suis prêt à répondre à vos questions."
                ],
                "keywords": ["Comment", "ça", "va"],
                "confidence": 0.95
            },

            "Comment vous appelez-vous": {
                "answers": [
                    "Je m'appelle CSS AI. Comment puis-je vous aider aujourd'hui ?",
                    "Mon nom est CSS AI, votre assistant virtuel pour la CSS.",
                    "Je suis CSS AI, l'intelligence artificielle de la Caisse de Sécurité Sociale.",
                    "CSS AI, c'est mon nom ! Je suis là pour vous accompagner.",
                    "Je me présente : CSS AI, votre assistant numérique CSS.",
                    "Mon nom est CSS AI, spécialisé dans l'assistance CSS.",
                    "Je suis CSS AI, l'assistant virtuel de la sécurité sociale sénégalaise.",
                    "CSS AI pour vous servir ! C'est ainsi que je m'appelle.",
                    "Je porte le nom de CSS AI, votre guide pour la CSS.",
                    "CSS AI, c'est moi ! Votre assistant personnel pour la CSS."
                ],
                "keywords": ["Comment", "vous", "appelez-vous"],
                "confidence": 0.95
            },

            "Comment vous présentez-vous": {
                "answers": [
                    "Je suis une intelligence artificielle spécialisée dans la fourniture d'assistance aux citoyens en sénégal. Je suis capable de répondre à vos questions sur la retraite, les cotisations, les allocations familiales et bien plus encore. Comment puis-je vous aider aujourd'hui ?",
                    "Je suis CSS AI, votre assistant virtuel dédié aux services de la Caisse de Sécurité Sociale. Je peux vous renseigner sur tous les aspects de vos droits sociaux.",
                    "En tant qu'assistant IA de la CSS, je suis conçu pour vous accompagner dans vos démarches administratives et répondre à toutes vos questions sur la sécurité sociale.",
                    "Je suis l'assistant numérique de la CSS, programmé pour vous fournir des informations précises sur les retraites, cotisations et prestations sociales.",
                    "CSS AI, intelligence artificielle dédiée à l'assistance des usagers de la Caisse de Sécurité Sociale du Sénégal.",
                    "Je suis votre conseiller virtuel CSS, expert en prestations sociales, retraites et allocations familiales.",
                    "Assistant numérique spécialisé dans les services CSS : je vous guide dans toutes vos démarches sociales.",
                    "IA conversationnelle de la CSS, je réponds à vos interrogations sur la sécurité sociale sénégalaise.",
                    "Votre interlocuteur digital CSS pour tout savoir sur vos droits et prestations sociales.",
                    "Assistant virtuel expert CSS : retraites, cotisations, allocations - je suis là pour vous informer."
                ],
                "keywords": ["Comment", "vous", "présentez-vous"],
                "confidence": 0.95
            },

            "Comment vous pouvez vous aider": {
                "answers": [
                    "Je suis là pour vous aider. Que souhaitez-vous savoir ?",
                    "Je peux vous assister dans toutes vos démarches CSS. Quelle est votre question ?",
                    "Mon rôle est de vous accompagner. Comment puis-je vous être utile ?",
                    "Je suis à votre disposition pour répondre à vos questions. Que puis-je faire pour vous ?",
                    "Je vous guide dans l'univers CSS. Quelle information recherchez-vous ?",
                    "Mon assistance couvre tous les domaines CSS. De quoi avez-vous besoin ?",
                    "Je réponds à toutes vos interrogations CSS. Posez-moi vos questions !",
                    "Je vous accompagne dans vos démarches sociales. Comment puis-je vous aider ?",
                    "Mon expertise CSS est à votre service. Que souhaitez-vous découvrir ?",
                    "Je vous oriente et informe sur la CSS. Quelle est votre préoccupation ?"
                ],
                "keywords": ["Comment", "vous", "pouvez", "vous", "aider"],
                "confidence": 0.95
            },

            "Quel est votre nom": {
                "answers": [
                    "Je m'appelle CSS AI. Comment puis-je vous aider aujourd'hui ?",
                    "Mon nom est CSS AI, votre assistant virtuel de la CSS.",
                    "CSS AI, c'est moi ! Que puis-je faire pour vous ?",
                    "Je suis CSS AI, l'assistant numérique de la Caisse de Sécurité Sociale.",
                    "CSS AI pour vous servir ! Comment puis-je vous assister ?",
                    "Mon identité : CSS AI, spécialiste de l'assistance CSS.",
                    "Je porte le nom CSS AI, votre conseiller virtuel.",
                    "CSS AI, assistant IA de la sécurité sociale sénégalaise.",
                    "Je me nomme CSS AI, à votre service pour la CSS.",
                    "CSS AI, c'est ainsi que je m'identifie. Comment puis-je vous aider ?"
                ],
                "keywords": ["Quel", "est", "votre", "nom"],
                "confidence": 0.95
            },

            "Quel est votre rôle": {
                "answers": [
                    "Je suis une intelligence artificielle spécialisée dans la fourniture d'assistance aux citoyens en sénégal. Je suis capable de répondre à vos questions sur la retraite, les cotisations, les allocations familiales et bien plus encore. Comment puis-je vous aider aujourd'hui ?",
                    "Mon rôle est d'être votre guide dans l'univers de la sécurité sociale sénégalaise. Je vous aide avec les retraites, cotisations et prestations.",
                    "Je suis l'assistant virtuel de la CSS, conçu pour vous informer sur tous les aspects de la sécurité sociale au Sénégal.",
                    "En tant qu'IA spécialisée CSS, je vous accompagne dans vos démarches administratives et réponds à vos questions sur vos droits sociaux.",
                    "Ma mission : vous orienter et conseiller sur toutes les prestations CSS disponibles.",
                    "Je facilite votre compréhension de la sécurité sociale : explications, procédures, droits.",
                    "Conseiller numérique CSS : je vulgarise les informations sur retraites, cotisations et allocations.",
                    "Mon objectif : rendre accessible l'information CSS et vous accompagner dans vos démarches.",
                    "Je traduis la complexité administrative CSS en informations claires et pratiques.",
                    "Votre interface humaine avec le système CSS : questions, réponses, accompagnement personnalisé."
                ],
                "keywords": ["Quel", "est", "votre", "rôle"],
                "confidence": 0.95
            },

            "Qu'est-ce que la retraite": {
                "answers": [
                    "La retraite est une pension sociale offerte aux travailleurs salariés affiliés à la CSS. Elle permet de couvrir les coûts de santé et de retraite des travailleurs en sénégal.",
                    "C'est une prestation sociale qui garantit un revenu aux travailleurs après leur cessation d'activité, financée par les cotisations CSS.",
                    "La pension de retraite CSS est un droit acquis par les cotisations versées pendant votre carrière professionnelle.",
                    "Il s'agit d'une allocation mensuelle versée aux anciens salariés affiliés à la CSS pour assurer leur sécurité financière après 60 ans.",
                    "Système de remplacement de revenu pour les travailleurs ayant cessé leur activité professionnelle.",
                    "Prestation viagère destinée à maintenir le niveau de vie des anciens salariés CSS.",
                    "Revenu de substitution calculé sur la base des cotisations versées durant la carrière.",
                    "Protection sociale garantissant une ressource financière aux retraités du secteur privé.",
                    "Pension mensuelle acquise grâce aux contributions sociales versées pendant la vie active.",
                    "Dispositif de sécurité sociale assurant un revenu régulier après la fin de l'activité professionnelle."
                ],
                "keywords": ["retraite", "pension", "sociale", "affilié"],
                "confidence": 0.95
            },

            "Merci": {
                "answers": [
                    "De rien ! N'hésitez pas à me poser d'autres questions.",
                    "Je vous en prie ! Je reste à votre disposition.",
                    "Avec plaisir ! Y a-t-il autre chose que je puisse faire pour vous ?",
                    "C'est tout naturel ! N'hésitez pas si vous avez d'autres questions.",
                    "Pas de quoi ! Je suis là pour vous aider.",
                    "Il n'y a pas de quoi ! Revenez quand vous voulez.",
                    "Je vous en prie ! Mon plaisir de vous avoir aidé.",
                    "De rien ! C'est pour cela que je suis là.",
                    "Avec grand plaisir ! N'hésitez jamais à me solliciter.",
                    "Tout le plaisir était pour moi ! À votre service !"
                ],
                "keywords": ["Merci", "merci"],
                "confidence": 0.95
            },

            "Ok": {
                "answers": [
                    "Ok ! N'hésitez pas à me poser d'autres questions.",
                    "Parfait ! Je suis là si vous avez besoin d'aide.",
                    "Très bien ! Que puis-je faire d'autre pour vous ?",
                    "D'accord ! N'hésitez pas à revenir vers moi.",
                    "Entendu ! Je reste disponible pour vos questions.",
                    "Parfait ! Autre chose à savoir sur la CSS ?",
                    "Ok ! Mon assistance continue si besoin.",
                    "Très bien ! À votre disposition pour la suite.",
                    "C'est noté ! Que puis-je faire de plus ?",
                    "Compris ! N'hésitez pas pour d'autres informations."
                ],
                "keywords": ["Ok", "ok"],
                "confidence": 0.95
            },

            # Questions sur l'âge de retraite
            "quel est l'âge de la retraite": {
                "answers": [
                    "L'âge légal de départ à la retraite au Sénégal est de 60 ans pour les salariés du secteur privé affiliés à la CSS. Cependant, il est possible de partir en retraite anticipée sous certaines conditions ou de prolonger l'activité jusqu'à 65 ans.",
                    "Au Sénégal, vous pouvez partir à la retraite à 60 ans si vous êtes affilié à la CSS. Des départs anticipés ou des prolongations jusqu'à 65 ans sont possibles selon les cas.",
                    "L'âge de la retraite est fixé à 60 ans pour les travailleurs du secteur privé. Vous pouvez continuer à travailler jusqu'à 65 ans ou partir plus tôt sous conditions.",
                    "60 ans, c'est l'âge légal de la retraite CSS. Mais vous avez la flexibilité de partir plus tôt ou plus tard selon votre situation professionnelle.",
                    "La retraite CSS intervient normalement à 60 ans, avec des possibilités d'aménagement selon votre parcours professionnel.",
                    "60 ans : âge de référence pour la liquidation des droits à pension CSS.",
                    "L'âge normal de la retraite est de 60 ans, modulable selon les circonstances individuelles.",
                    "Seuil légal : 60 ans pour bénéficier de la pension de retraite CSS complète.",
                    "À 60 ans, vous atteignez l'âge d'ouverture des droits à la retraite CSS.",
                    "60 ans marque l'âge standard de cessation d'activité et d'entrée en retraite CSS."
                ],
                "keywords": ["âge", "retraite", "60 ans", "départ", "légal"],
                "confidence": 0.95
            },
            
            "à quel âge peut-on prendre sa retraite": {
                "answers": [
                    "Vous pouvez prendre votre retraite à partir de 60 ans si vous êtes affilié à la CSS. L'âge normal de la retraite est fixé à 60 ans, avec possibilité de prolongation jusqu'à 65 ans selon votre situation.",
                    "La retraite CSS peut être prise dès 60 ans. C'est l'âge légal, mais vous pouvez aussi continuer jusqu'à 65 ans si vous le souhaitez.",
                    "À partir de 60 ans, vous avez le droit de partir à la retraite. Vous pouvez aussi choisir de prolonger votre activité jusqu'à 65 ans maximum.",
                    "60 ans minimum pour la retraite CSS, avec la possibilité de travailler jusqu'à 65 ans selon vos besoins et votre situation.",
                    "L'ouverture des droits à pension commence à 60 ans pour tous les affiliés CSS.",
                    "Dès 60 ans révolus, vous pouvez liquider votre retraite CSS.",
                    "60 ans : âge minimal d'éligibilité à la pension de retraite CSS.",
                    "Vous êtes en droit de cesser votre activité et percevoir votre retraite dès 60 ans.",
                    "L'âge plancher pour la retraite CSS est fixé à 60 ans accomplis.",
                    "À partir de votre 60e anniversaire, la retraite CSS devient accessible."
                ],
                "keywords": ["âge", "prendre", "retraite", "60"],
                "confidence": 0.95
            },
            
            # Questions sur les cotisations
            "quel est le taux de cotisation css": {
                "answers": [
                    "Le taux de cotisation à la CSS est de 24% du salaire brut, réparti comme suit : 16% à la charge de l'employeur et 8% à la charge du salarié. Ce taux couvre les prestations familiales, la pension de retraite et les risques professionnels.",
                    "Les cotisations CSS représentent 24% du salaire brut : vous payez 8% et votre employeur 16%. Cela finance vos futures prestations sociales.",
                    "24% au total : 8% déduits de votre salaire et 16% payés par l'employeur. Ces cotisations vous donnent droit aux prestations CSS.",
                    "Le taux global est de 24% du salaire brut, partagé entre salarié (8%) et employeur (16%) pour financer la sécurité sociale.",
                    "Répartition des cotisations CSS : 8% part salariale, 16% part patronale, soit 24% du salaire brut.",
                    "Sur chaque franc de salaire brut : 8 centimes à votre charge, 16 centimes à la charge patronale.",
                    "Quote-part salarié : 8% du brut ; quote-part employeur : 16% du brut = 24% total CSS.",
                    "Prélèvement social de 24% du salaire brut partagé inégalement : 1/3 salarié, 2/3 employeur.",
                    "Cotisation CSS globale de 24% avec répartition asymétrique favorisant le salarié (8% vs 16%).",
                    "Taux CSS unifié de 24% sur salaire brut : contribution salariale 8%, contribution patronale 16%."
                ],
                "keywords": ["taux", "cotisation", "24%", "employeur", "salarié"],
                "confidence": 0.9
            },
            
            "combien cotise-t-on à la css": {
                "answers": [
                    "Les cotisations à la CSS représentent 24% du salaire brut : 8% sont prélevés sur le salaire du salarié et 16% sont payés par l'employeur. Ces cotisations donnent droit aux prestations sociales.",
                    "Vous cotisez 8% de votre salaire brut, tandis que votre employeur verse 16%, soit 24% au total pour la CSS.",
                    "8% de votre salaire est prélevé pour la CSS, complété par 16% payés par votre employeur, totalisant 24% de cotisations.",
                    "Au total 24% du salaire brut : votre part est de 8%, celle de l'employeur de 16%. Ces cotisations financent vos droits sociaux.",
                    "Votre contribution personnelle CSS s'élève à 8% du salaire brut mensuel.",
                    "Pour chaque 100 francs de salaire brut, vous cotisez 8 francs à la CSS.",
                    "Le prélèvement CSS sur votre bulletin de paie représente 8% du brut.",
                    "Déduction salariale CSS : 8% du montant brut de votre rémunération.",
                    "Votre cotisation CSS correspond à 8% de vos revenus salariaux bruts.",
                    "Part salariale CSS : 8% prélevés directement sur votre salaire avant net."
                ],
                "keywords": ["cotise", "cotisation", "24%", "8%", "16%"],
                "confidence": 0.9
            },
            
            # Questions sur les allocations familiales
            "montant des allocations familiales": {
                "answers": [
                    "Les allocations familiales de la CSS sont versées mensuellement. Le montant varie selon le nombre d'enfants à charge et leur âge. Pour connaître le montant exact applicable à votre situation, veuillez consulter le barème en vigueur auprès de votre agence CSS.",
                    "Le montant des allocations familiales dépend du nombre et de l'âge de vos enfants. Contactez votre agence CSS pour connaître le barème actualisé.",
                    "Les allocations familiales sont calculées selon un barème officiel basé sur le nombre d'enfants à charge. Renseignez-vous auprès de la CSS pour les montants exacts.",
                    "Chaque famille reçoit un montant différent selon sa composition. Le barème des allocations familiales est disponible dans toutes les agences CSS.",
                    "Tarification progressive des allocations familiales selon le nombre d'enfants bénéficiaires.",
                    "Montants différenciés par tranche d'âge des enfants et taille de la fratrie.",
                    "Barème dégressif ou progressif selon la politique CSS en vigueur pour les prestations familiales.",
                    "Calcul personnalisé basé sur la composition familiale déclarée à la CSS.",
                    "Grille tarifaire officielle CSS déterminant les montants selon critères familiaux.",
                    "Prestations modulées individuellement selon le profil familial de chaque allocataire."
                ],
                "keywords": ["montant", "allocations", "familiales", "enfants"],
                "confidence": 0.85
            },
            
            "qui a droit aux allocations familiales": {
                "answers": [
                    "Ont droit aux allocations familiales tous les salariés affiliés à la CSS ayant des enfants à charge âgés de moins de 21 ans (ou 25 ans s'ils poursuivent des études). L'enfant doit résider au Sénégal et être déclaré à la CSS.",
                    "Tous les travailleurs affiliés CSS avec des enfants de moins de 21 ans (25 ans pour les étudiants) résidant au Sénégal peuvent bénéficier des allocations familiales.",
                    "Si vous êtes salarié affilié à la CSS et avez des enfants à charge de moins de 21 ans au Sénégal, vous avez droit aux allocations familiales.",
                    "Les allocations familiales concernent les salariés CSS ayant des enfants résidents au Sénégal : moins de 21 ans ou 25 ans s'ils étudient.",
                    "Condition d'éligibilité : être affilié CSS et avoir des enfants de moins de 21 ans à charge.",
                    "Bénéficiaires : salariés CSS avec enfants mineurs (jusqu'à 21 ans, 25 ans si scolarisés).",
                    "Critères : affiliation CSS + enfants à charge résidant au Sénégal + limites d'âge respectées.",
                    "Ayants droit : travailleurs CSS déclarant des enfants dans les tranches d'âge éligibles.",
                    "Publics concernés : familles affiliées CSS avec descendants dans les critères légaux.",
                    "Conditions cumulatives : cotisant CSS + enfants à charge + résidence sénégalaise + âge limite."
                ],
                "keywords": ["droit", "allocations", "familiales", "enfants", "21 ans"],
                "confidence": 0.9
            },
            
            # Questions sur les prestations maladie
            "comment être remboursé par la css": {
                "answers": [
                    "Pour être remboursé par la CSS, vous devez : 1) Présenter votre carte CSS lors des soins, 2) Conserver tous les justificatifs (ordonnances, factures), 3) Déposer votre dossier de remboursement dans les délais, 4) Attendre le traitement de votre dossier.",
                    "Le remboursement CSS nécessite votre carte d'affilié, la conservation des factures et ordonnances, puis le dépôt du dossier complet dans les délais.",
                    "Présentez votre carte CSS, gardez tous vos justificatifs médicaux, et déposez votre demande de remboursement à temps pour être remboursé.",
                    "Étapes du remboursement : montrer la carte CSS, collecter les documents médicaux, soumettre le dossier dans les délais impartis.",
                    "Procédure : identification CSS + conservation pièces justificatives + constitution dossier + dépôt en agence.",
                    "Circuit remboursement : soins avec carte CSS → collecte factures → dossier complet → dépôt agence.",
                    "Démarche : carte CSS obligatoire → archivage documents → montage dossier → transmission CSS.",
                    "Processus : présentation carte → récupération justificatifs → assemblage dossier → soumission délais.",
                    "Méthode : usage carte CSS → sauvegarde pièces → préparation demande → envoi respectant délais.",
                    "Cheminement : identification CSS → documentation complète → dossier constitué → dépôt réglementaire."
                ],
                "keywords": ["remboursé", "remboursement", "carte", "justificatifs"],
                "confidence": 0.85
            },
            
            "quels soins sont couverts par la css": {
                "answers": [
                    "La CSS couvre les consultations médicales, les hospitalisations, les médicaments prescrits, les examens de laboratoire, la radiologie, et certains soins dentaires. Le taux de remboursement varie selon le type de soins et le statut de l'établissement.",
                    "Consultations, hospitalisations, médicaments sur ordonnance, analyses de laboratoire, radiologie et soins dentaires sont pris en charge par la CSS.",
                    "La CSS rembourse les frais médicaux : consultations, séjours hospitaliers, médicaments prescrits, examens et certains soins spécialisés.",
                    "Sont couverts : les consultations médicales, hospitalisations, pharmacie sur ordonnance, examens médicaux et soins dentaires selon les barèmes CSS.",
                    "Prise en charge : médecine générale, spécialistes, hospitalisation, pharmacie, imagerie médicale.",
                    "Couverture CSS : soins ambulatoires, hospitaliers, pharmaceutiques, paramédicaux dans les limites tarifaires.",
                    "Prestations remboursées : actes médicaux, séjours cliniques, traitements prescrits, investigations diagnostiques.",
                    "Soins éligibles : consultations toutes spécialités, hospitalisations, médicaments liste, examens complémentaires.",
                    "Champ de couverture : médecine curative, hospitalisation, pharmacie référencée, explorations médicales.",
                    "Soins pris en charge : consultations médicales, soins hospitaliers, traitements pharmaceutiques, examens diagnostiques."
                ],
                "keywords": ["soins", "couverts", "consultations", "médicaments"],
                "confidence": 0.85
            },
            
            # Questions sur les documents
            "quels documents pour s'inscrire à la css": {
                "answers": [
                    "Pour s'inscrire à la CSS, vous devez fournir : une copie de votre pièce d'identité, un certificat de travail, les bulletins de salaire des 3 derniers mois, une fiche d'état civil, et le formulaire d'immatriculation dûment rempli.",
                    "L'inscription CSS nécessite : pièce d'identité, certificat de travail, 3 derniers bulletins de salaire, état civil et formulaire d'immatriculation complété.",
                    "Documents requis : copie CNI, attestation de travail, fiches de paie récentes, extrait d'état civil et dossier d'immatriculation CSS.",
                    "Pour vous affilier : apportez votre identité, justificatif d'emploi, bulletins de salaire des 3 derniers mois, état civil et formulaire CSS rempli.",
                    "Pièces d'immatriculation : CNI, contrat de travail, fiches de paie, acte de naissance, formulaire CSS.",
                    "Dossier d'affiliation : identité officielle + preuve d'emploi + justificatifs salariaux + état civil + formulaires.",
                    "Constitution dossier : document d'identité + certification emploi + salaires récents + civil + imprimés CSS.",
                    "Éléments requis : carte identité + attestation professionnelle + bulletins paie + extrait civil + demande.",
                    "Pièces obligatoires : CNI + certificat employeur + salaires 3 mois + état civil + formulaire adhésion.",
                    "Documents d'inscription : identité + emploi certifié + rémunérations récentes + civil + imprimé CSS complété."
                ],
                "keywords": ["documents", "inscrire", "pièce", "identité", "certificat"],
                "confidence": 0.9
            },
            
            "comment obtenir une attestation css": {
                "answers": [
                    "Pour obtenir une attestation CSS, rendez-vous dans votre agence CSS avec votre pièce d'identité et votre numéro d'immatriculation. L'attestation peut aussi être demandée en ligne sur le site officiel de la CSS ou par courrier.",
                    "Trois moyens d'obtenir votre attestation CSS : en agence avec votre CNI, en ligne sur le site CSS, ou par courrier postal.",
                    "Votre attestation CSS est disponible en agence (avec pièce d'identité), sur le portail web CSS ou par demande écrite.",
                    "Obtenez votre attestation : directement en agence CSS, via le site internet officiel, ou en envoyant une demande par courrier.",
                    "Délivrance attestation : guichet agence avec CNI, télé-service CSS en ligne, ou demande postale.",
                    "Modalités d'obtention : visite agence muni d'identité, connexion portail web, ou envoi courrier.",
                    "Trois canaux : accueil physique agence, service numérique CSS, ou correspondance écrite.",
                    "Édition attestation : sur place avec pièces, via plateforme digitale, ou par voie postale.",
                    "Obtention possible : déplacement agence (CNI obligatoire), en ligne site CSS, courrier demande.",
                    "Démarches : rendez-vous agence avec identité, connexion web CSS, ou demande par courrier."
                ],
                "keywords": ["attestation", "obtenir", "agence", "identité"],
                "confidence": 0.9
            },
            
            # Questions sur les délais
            "délai de traitement css": {
                "answers": [
                    "Les délais de traitement à la CSS varient selon le type de dossier : remboursements maladie (15-30 jours), prestations familiales (7-15 jours), pension de retraite (1-3 mois). Ces délais peuvent être prolongés en cas de dossier incomplet.",
                    "Comptez 15-30 jours pour les remboursements maladie, 7-15 jours pour les allocations familiales, et 1-3 mois pour les pensions de retraite.",
                    "Délais CSS : prestations familiales sous 2 semaines, remboursements santé sous 1 mois, retraites sous 3 mois maximum.",
                    "Les traitements prennent 1-2 semaines (allocations), 2-4 semaines (maladie) ou 1-3 mois (retraite) selon la complexité du dossier.",
                    "Temporalité variable : allocations familiales rapides (1-2 semaines), maladie moyen (3-4 semaines), retraite long (2-3 mois).",
                    "Délais standards : prestations courantes 15 jours, remboursements santé 1 mois, liquidations retraite 3 mois.",
                    "Échéancier type : allocations express, remboursements médium, pensions longues selon complexité administrative.",
                    "Durées indicatives : familles 2 semaines, santé 1 mois, retraite trimestre en moyenne.",
                    "Planning traitement : prestations familiales prioritaires, maladie intermédiaire, retraite approfondie.",
                    "Délais d'instruction : rapide (allocations), moyen (santé), étendu (retraite) selon nature dossier."
                ],
                "keywords": ["délai", "traitement", "remboursement", "pension"],
                "confidence": 0.8
            },
            
            # Questions sur les contacts
            "numéro de téléphone css": {
                "answers": [
                    "Pour contacter la CSS, vous pouvez appeler le numéro vert gratuit ou vous rendre dans l'une des agences régionales. Les coordonnées complètes sont disponibles sur le site officiel de la CSS ou dans vos documents d'affiliation.",
                    "Contactez la CSS via le numéro vert gratuit, en agence régionale, ou consultez le site web pour toutes les coordonnées.",
                    "Plusieurs moyens de contact CSS : numéro gratuit, agences locales, site internet officiel avec toutes les informations.",
                    "Appelez le numéro vert CSS, rendez-vous en agence, ou trouvez tous les contacts sur le portail web officiel.",
                    "Contact CSS : ligne verte gratuite, réseau d'agences régionales, site web avec coordonnées complètes.",
                    "Moyens de communication : appel gratuit, visite agence locale, consultation site officiel CSS.",
                    "Canaux disponibles : téléphone gratuit, accueil physique, portail numérique avec contacts.",
                    "Options contact : numéro vert, agences territoriales, site web complet avec coordonnées.",
                    "Communication CSS : ligne téléphonique gratuite, bureaux régionaux, plateforme web informative.",
                    "Joindre CSS : appel sans frais, déplacement agence, navigation site avec toutes infos contact."
                ],
                "keywords": ["numéro", "téléphone", "contact", "agence"],
                "confidence": 0.85
            },
            
            "où se trouve l'agence css": {
                "answers": [
                    "La CSS dispose d'agences dans toutes les régions du Sénégal. L'agence principale se trouve à Dakar. Pour connaître l'adresse de l'agence la plus proche de chez vous, consultez le site web de la CSS ou appelez le numéro d'information.",
                    "Agences CSS dans toutes les régions sénégalaises, siège à Dakar. Trouvez la plus proche sur le site CSS ou par téléphone.",
                    "La CSS a des bureaux régionaux partout au Sénégal, avec le siège social à Dakar. Localisez votre agence via le site web.",
                    "Présence CSS dans chaque région du pays, direction générale à Dakar. Consultez le site ou appelez pour localiser votre agence.",
                    "Maillage territorial complet : agences dans toutes les régions, siège central à Dakar.",
                    "Réseau géographique étendu : bureaux régionaux partout, direction nationale dakaroise.",
                    "Implantation nationale : antennes régionales, siège social dans la capitale sénégalaise.",
                    "Couverture géographique totale : présence régionale, administration centrale à Dakar.",
                    "Organisation territoriale : agences décentralisées, direction centralisée à Dakar.",
                    "Répartition géographique : bureaux dans toutes régions, centre névralgique dakarois."
                ],
                "keywords": ["agence", "adresse", "dakar", "région"],
                "confidence": 0.85
            },
            
            # Questions générales
            "qu'est-ce que la css": {
                "answers": [
                    "La CSS (Caisse de Sécurité Sociale) est l'organisme public chargé de la gestion de la sécurité sociale au Sénégal. Elle gère les prestations familiales, les pensions de retraite, les accidents du travail et les prestations maladie pour les salariés du secteur privé.",
                    "C'est l'institution publique sénégalaise qui administre la sécurité sociale : retraites, allocations familiales, santé et accidents du travail.",
                    "La Caisse de Sécurité Sociale du Sénégal, organisme public gérant la protection sociale des travailleurs du secteur privé.",
                    "Institution nationale de sécurité sociale qui protège les salariés sénégalais : pensions, prestations familiales, couverture maladie et AT/MP.",
                    "Établissement public administratif chargé de la protection sociale des travailleurs salariés du secteur privé sénégalais.",
                    "Organisme national de sécurité sociale administrant les régimes obligatoires de protection sociale.",
                    "Institution publique de prévoyance sociale couvrant les risques sociaux des salariés privés.",
                    "Caisse publique de sécurité sociale gérant les prestations sociales légales au Sénégal.",
                    "Établissement de protection sociale administrant les régimes obligatoires pour salariés du privé.",
                    "Organisme étatique de sécurité sociale assurant la couverture des risques sociaux des travailleurs."
                ],
                "keywords": ["css", "caisse", "sécurité sociale", "organisme"],
                "confidence": 0.95
            },
            
            "comment fonctionne la css": {
                "answers": [
                    "La CSS fonctionne sur le principe de la répartition : les cotisations des actifs financent les prestations des bénéficiaires. Elle collecte les cotisations des employeurs et salariés, puis verse les prestations (retraites, allocations familiales, remboursements maladie) selon les droits acquis.",
                    "Système de répartition : vos cotisations d'aujourd'hui financent les prestations actuelles, et vos futurs droits seront financés par les cotisations futures.",
                    "La CSS collecte les cotisations sociales et redistribue immédiatement sous forme de prestations aux bénéficiaires selon leurs droits acquis.",
                    "Principe solidaire : les cotisations des travailleurs actifs servent à payer les prestations des retraités et bénéficiaires actuels.",
                    "Mécanisme de solidarité intergénérationnelle : actifs cotisent pour financer prestations des bénéficiaires actuels.",
                    "Fonctionnement redistributif : collecte cotisations → constitution réserves → versement prestations selon droits.",
                    "Système solidaire de répartition : cotisations immédiates financent prestations courantes directement.",
                    "Circuit financier : prélèvements salariaux/patronaux → gestion centralisée → redistribution ciblée.",
                    "Logique collective : mutualisation des cotisations pour financement solidaire des prestations sociales.",
                    "Principe de répartition pure : cotisations présentes alimentent prestations présentes sans capitalisation."
                ],
                "keywords": ["fonctionne", "répartition", "cotisations", "prestations"],
                "confidence": 0.9
            }
        }
        
        # Variations et synonymes pour améliorer la détection
        self.synonyms = {
            "css": ["caisse de sécurité sociale", "sécurité sociale", "caisse"],
            "retraite": ["pension", "retirement", "cessation d'activité"],
            "cotisation": ["contribution", "versement", "prélèvement"],
            "allocations": ["prestations", "indemnités", "aides"],
            "remboursement": ["remboursé", "rembourser", "prise en charge"]
        }
    
    def normalize_question(self, question: str) -> str:
        """Normalise une question pour améliorer la correspondance"""
        # Convertir en minuscules
        question = question.lower().strip()
        
        # Supprimer la ponctuation
        question = re.sub(r'[?!.,;:]', '', question)
        
        # Remplacer les synonymes
        for key, synonyms in self.synonyms.items():
            for synonym in synonyms:
                question = question.replace(synonym, key)
        
        return question
    
    def calculate_similarity(self, question1: str, question2: str) -> float:
        """Calcule la similarité entre deux questions"""
        return SequenceMatcher(None, question1, question2).ratio()
    
    def find_best_match(self, user_question: str, threshold: float = 0.7) -> Optional[Tuple[str, Dict]]:
        """Trouve la meilleure correspondance pour une question utilisateur"""
        normalized_question = self.normalize_question(user_question)
        
        best_match = None
        best_score = 0.0
        
        for predefined_question, qa_data in self.qa_database.items():
            # Similarité directe avec la question prédéfinie
            similarity = self.calculate_similarity(normalized_question, predefined_question)
            
            # Bonus si des mots-clés sont présents
            keyword_bonus = 0.0
            for keyword in qa_data["keywords"]:
                if keyword.lower() in normalized_question:
                    keyword_bonus += 0.1
            
            total_score = similarity + min(keyword_bonus, 0.3)  # Limiter le bonus à 0.3
            
            if total_score > best_score and total_score >= threshold:
                best_score = total_score
                best_match = (predefined_question, qa_data)
        
        return best_match if best_match else None
    
    def get_predefined_answer(self, user_question: str, threshold: float = 0.7) -> Optional[Dict]:
        """Récupère une réponse prédéfinie si elle existe"""
        match = self.find_best_match(user_question, threshold)
        
        if match:
            predefined_question, qa_data = match
            logger.info(f"Réponse prédéfinie trouvée pour: '{user_question}' -> '{predefined_question}'")
            
            # Sélectionner une réponse aléatoire parmi les réponses disponibles
            if "answers" in qa_data:
                # Nouveau format avec plusieurs réponses
                selected_answer = random.choice(qa_data["answers"])
                logger.info(f"Réponse sélectionnée aléatoirement: '{selected_answer[:50]}...'")
            elif "answer" in qa_data:
                # Ancien format avec une seule réponse (rétrocompatibilité)
                selected_answer = qa_data["answer"]
            else:
                logger.error(f"Format de données invalide pour la question: {predefined_question}")
                return None
            
            return {
                "answer": selected_answer,
                "confidence": qa_data["confidence"],
                "matched_question": predefined_question,
                "source": "predefined_qa",
                "keywords_matched": qa_data["keywords"],
                "total_answers_available": len(qa_data.get("answers", [qa_data.get("answer", "")]))
            }
        
        return None
    
    def add_qa_pair(self, question: str, answer, keywords: List[str], confidence: float = 0.8):
        """Ajoute une nouvelle paire question-réponse
        
        Args:
            question: La question à ajouter
            answer: Soit une string (réponse unique) soit une liste de strings (réponses multiples)
            keywords: Liste des mots-clés
            confidence: Niveau de confiance
        """
        normalized_question = self.normalize_question(question)
        
        if isinstance(answer, list):
            # Format avec plusieurs réponses
            self.qa_database[normalized_question] = {
                "answers": answer,
                "keywords": keywords,
                "confidence": confidence
            }
        else:
            # Format avec une seule réponse (rétrocompatibilité)
            self.qa_database[normalized_question] = {
                "answer": answer,
                "keywords": keywords,
                "confidence": confidence
            }
        
        logger.info(f"Nouvelle Q&A ajoutée: {question} ({len(answer) if isinstance(answer, list) else 1} réponse(s))")
    
    def get_all_questions(self) -> List[str]:
        """Retourne toutes les questions prédéfinies"""
        return list(self.qa_database.keys())
    
    def get_statistics(self) -> Dict:
        """Retourne des statistiques sur la base de Q&A"""
        return {
            "total_questions": len(self.qa_database),
            "average_confidence": sum(qa["confidence"] for qa in self.qa_database.values()) / len(self.qa_database),
            "total_keywords": sum(len(qa["keywords"]) for qa in self.qa_database.values())
        }
    
    def search_by_keyword(self, keyword: str) -> List[Tuple[str, Dict]]:
        """Recherche des Q&A par mot-clé"""
        results = []
        keyword_lower = keyword.lower()
        
        for question, qa_data in self.qa_database.items():
            if any(keyword_lower in kw.lower() for kw in qa_data["keywords"]) or keyword_lower in question:
                results.append((question, qa_data))
        
        return results