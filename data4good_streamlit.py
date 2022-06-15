#!/usr/bin/env python
# coding: utf-8 

# In[ ]:
# Importation des librairies'
import sys
#sys.path.append("")
from notebooks.age_gap.age_gap_automation import Movie
import notebooks.age_gap.process_couples as pc
import bechdelai.bechdelai.data.wikipedia as wiki
import bechdelai.bechdelai.data.tmdb as tmdb
from pyvis.network import Network
from pyvis import network as net

import streamlit as st
import streamlit_book as stb
import streamlit.components.v1 as components
from streamlit_option_menu import option_menu

from google.cloud import firestore
from google.cloud.firestore_v1.field_path import FieldPath

import pandas as pd
import numpy as np

from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import requests
import json
from pandas.io.json import json_normalize

import datetime as dt 

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt

# Streamlit webpage properties / set up the app with wide view preset and a title
st.set_page_config(page_title="BechelAI", page_icon="🐦", layout="wide")

api_k=st.secrets["api_secrets"]["tmdb_secret"]

with st.expander('vizViz'):
	if 'cast' not in st.session_state:
	    st.session_state.cast = []
	if 'crew' not in st.session_state:
	    st.session_state.crew = []
	if 'titrefilm' not in st.session_state:
	    st.session_state.titrefilm = ""
	if 'sortie' not in st.session_state:
		st.session_state.sortie = ""
	if 'idfilm' not in st.session_state:
		st.session_state.idfilm = ""
	if 'poster' not in st.session_state:
		st.session_state.poster = ""
	if 'selectinfo' not in st.session_state:
		st.session_state.selectinfo = ""

# --------------- SIDEBAR - Projet

	# --------------- HEADER
with st.sidebar:
	def header(projet,sous_projet):
		#st.markdown(f'<div><h1 style="background-color:#baeca6;color:#000;height:150px;justify-content:center;align-items:center;margin-bottom:20px;text-align:center;border-radius:6px;font-size:42px;">{projet}</br><p style="font-size:20px;padding-top:10px; color:#363535">{sous_projet}</p></div>',unsafe_allow_html=True) #background :linear-gradient(45deg, blue, red)
		st.image('logo2.png')
	header("Bechdel AI","Un projet Data 4 Good")
	

	# --------------- Add two expanders to provide additional information about this e-tutorial and the app
with st.sidebar.expander("Le projet"):
	url="https://dataforgood.fr/projects/bechdelai"
	st.image('https://dataforgoodfr.github.io/img/logo-dfg-new2.png', width=50) #use_column_width=True, https://dataforgoodfr.github.io/img/logo-dfg-new2.png, https://dataforgood.fr/img/logo-dfg-new2.png
	st.write("""Mesure et automatisation du test de Bechdel, de la (sous)représentation féminine 
		et des inégalités de représentation dans le cinéma et l'audiovisuel """)
	st.markdown(f'<a href={url} style="text-decoration:none;color:#000">En savoir plus</a>', unsafe_allow_html=True)

with st.sidebar.expander("L'application"):
     st.write("""This interactive eCourse App was built by Sharone Li using Streamlit and Streamlit_book. 
     	Streamlit_book is a Streamlit companion library that was written in Python and created by Sebastian Flores Benner. 
     	\n  \nThe Streamlit_book library was released on 01/20/2022. 
     	If you want to learn more about Streamlit_book, please read Sebastian's post here:
     	https://blog.streamlit.io/how-to-create-interactive-books-with-streamlit-and-streamlit-book-in-5-steps/""")

# --------------- SIDEBAR - MENU

with st.sidebar:
	selected = option_menu(None, 
		["Film", "Age Gap", "Formulaire"], 
	    icons=['house', 'clipboard-data', "list-task"], 
	    menu_icon="cast", 
	    default_index=0, 
	    orientation="vertical",
	    styles={
	        "container": {"padding": "0!important", "background-color": "#fafafa"},
	        "icon": {"color": "#EEAE46", "font-size": "20px"}, 
	        "nav-link": {"font-size": "20px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
	        "nav-link-selected": {"background-color": "#D0DE5C"},
	    }
	)

# --------------- RECHERCHE DES DONNEES DANS LE DATASET - Import de la liste de films FR sortie entre 2019 et 2021
df_films = pd.read_csv("data4good_streamlit/liste_imdb_2019-2021.csv")

df_toreplace_list=['VII ','VI ','IV ','III ','II ','I ','V ']
for atr in df_toreplace_list:
	df_films['annee_sortie']=df_films[['annee_sortie']].apply(lambda x : x.str.replace(atr, '', regex=False))

df_films = df_films.sort_values(by=['titre'], ascending=True)

# get a list of all possible ids, titles and years, for the widgets
titre_list = list(df_films['titre'].unique())

id_list = list(df_films['id_moviedb_final'].unique())
annee_list = list(df_films['annee_sortie'].unique())

# --------------- MENU SELECTION / INFOS FILM ET DATAVIZ
class aaaa():
	def menu_horizontal():
		selected_info = option_menu(None, 
			["Informations", "Datavisualisations", "Test Bechdel"],
		    icons=['camera-reels', 'pie-chart', "people",], 
		    menu_icon="cast", 
		    default_index=0, 
		    orientation="horizontal",
		    styles={
		        "container": {"padding": "0!important", "background-color": "#fafafa"},
		        "icon": {"color": "#EEAE46", "font-size": "20px"}, 
		        "nav-link": {"font-size": "20px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
		        "nav-link-selected": {"background-color": "#D0DE5C"},
		    }
		)
		return selected_info
	# --------------- FILM : PRESENTATION DE LA PARTIE INFOS FILMS ET DATAVIZ
	def do_home():
		st.header("INFOS FILM ET DATAVISUALISATIONS")
		st.write(""" A quoi vous fait penser Mulan ? Une femme forte, une héroine, une inspiration pour des milliers de petites filles ? Oui c’est sûrement tout cela. Et pourtant, à bien y regarder, les hommes sont plus mis en avant et leur temps de parole  (75% !) supplante celui de Mulan.
Comment a t-on pu le déterminer ? Grâce aux données disponibles sur internet, aux algorithmes et à l’IA.
C’est pourquoi nous avons créé cette application. Afin de vous sensibiliser sur les apparences que peuvent revêtir un film et les réalités concrètes établies par l’analyse des données.\n
Sélectionnez un film et découvrez :
- la composition du casting mais également de l’équipe technique
- s'il passe le test de Bechdel
- quelle est la relation entre les personnages et la différence d'âge entre les acteur.rice.s qui les incarnent.\n
 """)

# --------------------- FORMULAIRE

with st.expander(''):
	if 'num' not in st.session_state:
	    st.session_state.num = 1
	if 'data' not in st.session_state:
	    st.session_state.data = []

	class NewFilm:

		def __init__(self,submit_id):
			col_nav_form,col_form_vide,colform = st.columns([2,0.5,4])

			## --------------- MENU
			st.write(f"Film : {st.session_state.titrefilm} ({st.session_state.idfilm})") 
			st.write(f"Année de sortie: {st.session_state.sortie}")

			st.markdown("#### Personnage")
			self.nom_personnage = st.text_input('Nom du personnage (nom exact s’il est connu ; à défaut, nom permettant l’identification dans le générique)')

			self.import_personnage = st.radio('Importance du personnage dans le récit', ['Personnage principal','Personnage secondaire'])

			self.role_personnage = st.radio('Rôle du personnage dans le récit', ['Positif','Négatif','Neutre'])

			self.genre_personnage = st.selectbox('Genre', ['Homme cisgenre','Femme cisgenre','Homme trans','Femme trans','Autre'])

			self.catg_sociopro = st.selectbox('Catégorie socioprofessionnelle', ['Agriculteur·trice, exploitant·e','Artisan, commerçant·e, chef d’entreprise',
										'Cadre et profession intellectuelle supérieure','Profession intermédiaire','Employé·e' ,'Ouvrier·e ','Retraité·e','Élève/Collégien·ne/Lycéen·ne/Étudiant·e',
										'Personne sans emploi','Activités marginales ou illégales','Inconnu'])
			self.prec_metier = st.text_input('Précisez le métier exercé ou la nature de l’activité (y compris pour les retraité·es lorsque l’information est connue) :')

			self.origine = st.radio('Origine perçue', ['Perçu comme blanc','Perçu comme noir','Perçu comme arabe','Perçu comme asiatique','Autre'])

			st.markdown("#### Santé")
			self.handicap = st.radio('Le personnage est-il en situation de handicap :',['Oui','Non'])
			self.prec_handi = st.selectbox('Si oui, précisez le type :',['Handicap moteur','Handicap sensoriel','Handicap psychique','Handicap mental','Maladie invalidante'])
			self.maladie = st.radio('Le personnage est-il atteint d’une affection de longue durée (VIH, diabète, maladie d’Alzheimer, etc.) ou d’une maladie grave (ex : cancer) :',['Oui','Non'])
			self.addiction = st.radio('Le personnage souffre-t-il d’une addiction (alcool, médicaments, drogue, etc.) :',['Oui','Non'])

			st.markdown("#### Âge")
			self.age = st.selectbox('', ['Moins de 15 ans','15-20 ans','20-34 ans','35-49 ans','50-64 ans','65-79 ans','80 ans et plus'])		
			
			st.markdown("#### Situation de précarité")
			self.precarite = st.radio('',['Oui','Non','Inconnu'])
			self.prec_preca= st.selectbox('Si oui, précisez le type de situation de précarité :',['Chômage','Bénéficiaire du RMI/RSA','Personne sans domicile fixe','Personne ayant une situation professionnelle instable (petits boulots)',
									'Jeune de 16-25 ans exclu du milieu scolaire','Personne en situation d’endettement/grande difficulté financière'])

			st.markdown("#### Lieu de résidence")
			self.residence = st.radio('Le personnage vit-il en France ?',['Oui','Non'])
			self.prec_resid_non = st.text_input('Si non, précisez le pays :')
			self.prec_resid = st.selectbox('Où réside le personnage :',['Centre-ville','Quartier périphérique de pavillon et de petits immeubles',
									'Grands ensembles de banlieue populaire','Village','Autre'])
			self.region = st.selectbox('Dans quelle région, le personnage vit-il ?',['Auvergne-Rhône-Alpes','Bourgogne-Franche-Comté','Bretagne','Centre-Val de Loire','Corse','Grand Est','Hauts-de-France','Ile-de-France','Normandie','Nouvelle-Aquitaine',
								 'Occitanie','Pays de la Loire','PACA','Guadeloupe','Martinique','Guyane','La Réunion','Mayotte'])

			self.ville = st.selectbox('Le personnage vit-il dans l’une de ces villes ?',['Paris','Marseille','Lyon','Toulouse','Nice',
								'Nantes','Montpellier','Strasbourg','Bordeaux','Lille'])

			st.markdown('#### Situation familiale')
			self.sit_fam = st.selectbox('Le personnage est :',['Célibataire','En union libre','Marié/pacsé','Divorcé/séparé','Veuf','Non pertinent/inconnu'])
			self.enfant = st.radio('Le personnage a-t-il des enfants :',['Oui','Non','Inconnu'])
			self.avorte = st.radio('Le personnage a-t-il avorté :',['Oui','Non','Inconnu'])
			self.perte_enfant = st.radio('Le personnage a-t-il perdu un enfant :',['Oui','Non','Inconnu'])
			self.adultere = st.radio('Le personnage est-il engagé dans une ou des relations adultères :',['Oui','Non','Inconnu'])
		    
			st.markdown('###### Pour les personnages mineurs :')
			self.pere = st.radio('Le père du personnage participe-t-il activement à son éducation :',['Oui','Non','Inconnu'])
			self.mere = st.radio('La mère du personnage participe-t-elle activement à son éducation :',['Oui','Non','Inconnu'])
			self.orphelin = st.radio('Le personnage est-il orphelin :',['Oui','Non','Inconnu'])

			st.markdown('#### Religion')
			self.religon = st.selectbox('En terme de religion, le personnage est-il :',['Chrétien (catholique ou protestant)','Juif','Musulman','Athée','Autre','Information inconnue'])
			self.pratiquant = st.radio('Le personnage apparaît-il :',['Pratiquant','Non-pratiquant','Information inconnue'])

			st.markdown('#### Langue et accent')
			self.langue_francaise = st.radio('Le personnage parle-t-il français :',['Oui','Non'])
			self.langue_autre = st.radio('Le personnage parle-t-il une autre langue que le français :',['Oui','Non'])
			self.prec_langue = st.text_input('Si oui, préciser de quelle(s) langue(s) il s’agit :')

			self.accent_region = st.radio('Le personnage a-t-il un accent régional marqué :',['Oui','Non'])
			self.prec_accent_reg = st.selectbox('Si oui :',['Accent parisien','Accent du nord','Accent du sud',
		    						'Accent lyonnais','Accent d’un territoire ultra-marin','Autre'])
			self.accent_etranger = st.radio('Le personnage a-t-il un accent étranger :',['Oui','Non'])
			self.prec_accent_etrg = st.selectbox('Si oui :',['Accent anglophone','Accent européen (italien, allemand, espagnol, etc.)',
		    						'Accent africain','Accent asiatique','Accent russe','Autre'])
		    
			st.markdown('#### Vie amoureuse et sexualité')
			self.orientation_sexuelle = st.radio('Quelle est l’orientation sexuelle du personnage ?',['Hétérosexuel','Homosexuel','Bisexuel','Information inconnue'])
			self.embrasse = st.radio('Le personnage embrasse-t-il quelqu’un au cours du film',['Oui','Non'])
			self.embrasse_qui = st.radio('Si oui, embrasse-t-il :',['Un ou des hommes','Une ou des femmes','Un/des hommes et une/des femmes'])
			self.rapport_sexuel = st.radio('Le personnage a-t-il des rapports sexuels au cours du film',['Oui','Non'])
			self.rapport_avec_qq = st.radio('Si oui, embrasse-t-il :',['1 ou des hommes','Une ou des femmes','Un/des hommes et une/des femmes'])
			self.denude = st.radio('Le personnage apparaît-il dénudé ?',['De façon importante','De façon suggérée','Non'])

			st.markdown('#### Travail et loisirs')
			self.env_travail = st.radio('Le personnage est-il montré dans son environnement de travail :',['Oui','Non'])
			self.env_domestique = st.radio('Le personnage est-il montré dans son environnement domestique :',['Oui','Non'])
			self.cadre_familial = st.radio('Le personnage est-il montré dans son cadre familial :',['Oui','Non'])
			self.act_loisir = st.radio('Le personnage est-il montré dans des activités de loisirs :',['Oui','Non'])

			self.tache_domest = st.multiselect('Le personnage accomplit-il les tâches domestiques suivantes (plusieurs réponses possibles) :',
		    						['Courses (dont liste de courses ou courses en ligne)','Cuisine et préparation des repas','Rangement',
									'Gestion du linge (ramassage, lessive, repassage)','Ménage'])

			self.travail_parental = st.multiselect('Le personnage accomplit-il les tâches relatives au travail parental citées ci-dessous (plusieurs réponses possibles) :',
		    						['Éducation des enfants (aide aux devoirs, rendez-vous avec les professeurs)','Soins aux enfants (habillage, bain, change, etc.)',
		    						'Occupation des enfants (jeu, transports, accompagnement lors d’une activité de loisirs)',
		    						'Charge mentale du travail parental (discussions, écoute, inquiétude, interactions parents-enfants)'])


			st.markdown('#### Parcours de vie')
			self.parcous_ascendant = st.radio('Le personnage a-t-il un parcours social ascendant ?',['Oui','Non','Inconnu'])
			self.traj_migratoire = st.radio('Le personnage a-t-il une trajectoire migratoire ?',['Oui','Non','Inconnu'])
			self.double_culture = st.radio('Le personnage a-t-il une double culture/double appartenance culturelle ?',['Oui','Non','Inconnu'])
			self.parle_origine = st.radio('Le personnage parle-t-il de ses origines ?',['Oui','Non'])

			st.markdown('#### Activités illégales ou marginales')
			self.act_marginale = st.radio('Le personnage s’engage-t-il dans des activités illégales ou marginales ?',['Oui','Non'])
			self.prec_act_marg = st.multiselect('Si oui (plusieurs réponses possibles) :',['Activités criminelles (trafic d’armes, braquages, etc.)',
							'Détention, consommation ou trafic de stupéfiants','Prostitution','Cybercriminalité','Dégradation de biens',
							'Délinquance financière (corruption, blanchiment, évasion fiscale, délit d’initiés)'])

			st.markdown('#### Rapport aux autorités (police / justice)')
			self.police = st.radio('Le personnage est-il confronté à la police (arrestation, dépôt de plaintes, interrogatoire, etc.) ?',['Oui','Non'])
			self.justice = st.radio('Le personnage est-il confronté à la justice (consultation d’un avocat, divorce, convocation par un juge, etc.) ?',['Oui','Non'])
			self.violence_police = st.radio('Le personnage est-il victime de violences policières (contrôles d’identité abusifs, coups, humiliations, etc.) ?',['Oui','Non'])
			self.prison = st.radio('Le personnage est-il incarcéré au cours du film ?',['Oui','Non'])
			self.mis_examen = st.radio('Le personnage est-il mis en examen pour un crime ou un délit ?',['Oui','Non'])

			st.markdown('#### Violences')
			self.subit_violence = st.radio('Le personnage subit-il des violences :',['Oui','Non'])
			self.prec_subit_violence = st.multiselect('Si oui, lesquelles(plusieurs réponses possibles) :',['Homicide (y compris coups et blessures volontaires suivis de mort)',
		    					'Coups et blessures volontaires','Violences sexuelles (y compris viol, inceste, harcèlement sexuel)',
		    					'Violences sexuelles (y compris viol, inceste, harcèlement sexuel)','Cambriolage','Escroquerie','Violences psychologiques (y compris harcèlement, injures)',
								'Vol avec arme (armes à feu, armes blanches ou par destination)','Violences intrafamiliales'])
			self.victime_violence_reconnu = st.radio('Si oui, le personnage est-il reconnu comme victime dans la narration :',['Oui','Non'])
		    
			self.exerce_violence = st.radio('Le personnage exerce-t-il des violences :',['Oui','Non'])
			self.prec_exerce_violence = st.multiselect('Si oui, lesquelles(choix multiples) :',['Homicide (y compris coups et blessures volontaires suivis de mort)',
		    					'Coups et blessures volontaires','Violences sexuelles (y compris viol, inceste, harcèlement sexuel)',
		    					'Violences sexuelles (y compris viol, inceste, harcèlement sexuel)','Cambriolage','Escroquerie','Violences psychologiques (y compris harcèlement, injures)',
								'Vol avec arme (armes à feu, armes blanches ou par destination)','Violences intrafamiliales'])
		    
			self.reconnu_coupable_violence = st.radio('Si oui, le personnage est-il reconnu comme coupable dans la narration :',['Oui','Non'])
		    
			st.markdown('#### Discriminations et propos insultants')
			self.subit_discrimination = st.radio('Le personnage subit-il des actes de discrimination :',['Oui','Non'])
			self.prec_subit_discr = st.multiselect('Si oui (plusieurs réponses possibles)',['Discrimination fondée sur la couleur de peau ou l’origine',
		    					'Discrimination fondée sur le genre','Discrimination fondée sur la religion','Discrimination fondée sur l’état de santé/le handicap',
		    					'Discrimination fondée sur l’orientation sexuelle','Discrimination fondée sur la grossesse',
		    					'Discrimination fondée sur l’opinion politique ou l’activité syndicale','Discrimination fondée sur l’apparence physique',
		    					'Discrimination fondée sur la situation de précarité'])
			self.victime_disc_reconnu = st.radio('Si oui, le personnage est-il reconnu comme victime :',['Oui','Non'])
		    
			self.exerce_discrimination = st.radio('Le personnage commet-il des actes de discrimination :',['Oui','Non'])
			self.prec_exerce_discrim = st.multiselect('Si oui (choix multiples)',['Discrimination fondée sur la couleur de peau ou l’origine',
		    					'Discrimination fondée sur le genre','Discrimination fondée sur la religion','Discrimination fondée sur l’état de santé/le handicap',
		    					'Discrimination fondée sur l’orientation sexuelle','Discrimination fondée sur la grossesse',
		    					'Discrimination fondée sur l’opinion politique ou l’activité syndicale','Discrimination fondée sur l’apparence physique',
		    					'Discrimination fondée sur la situation de précarité'])
			self.reconnu_coupable_discr = st.radio('Si oui, le personnage est-il reconnu comme coupable de discrimination dans la narration :',['Oui','Non'])
		    
			self.est_offensant = st.radio('Le personnage a-t-il des propos insultants ou offensants :',['Oui','Non'])
			self.prec_est_offensant = st.multiselect('Si oui, ces propos insultants ou offensants sont fondés sur : (plusieurs réponses possibles)',['la couleur de peau ou l’origine',
							'le genre','la religion','l’état de santé/le handicap','l’orientation sexuelle','la grossesse',
							'l’opinion politique ou l’activité syndicale','l’apparence physique','la situation de précarité'])

			self.est_offensant_condamne = st.radio('Si oui, ces propos sont-ils condamnés ou critiqués dans le récit ?',['Oui','Non'])

			self.subit_offence = st.radio('Le personnage fait-il l’objet de propos insultants ou offensants :',['Oui','Non'])
			self.prec_subit_offence = st.multiselect('Si oui, ces derniers sont fondés sur : (plusieurs réponses possibles)',['la couleur de peau ou l’origine',
							'le genre','la religion','l’état de santé/le handicap','l’orientation sexuelle','la grossesse',
							'l’opinion politique ou l’activité syndicale','l’apparence physique','la situation de précarité'])

			self.se_sent_offence = st.radio('Si oui, le personnage se sent-il offensé ou insulté ?',['Oui','Non'])

			self.se_grime = st.radio('Le personnage se grime-t-il (costume et/ou maquillage et/ou accent emprunté) en adoptant des traits culturels ou phénotypiques attribués à un groupe culturel dont il ne fait pas partie ?',['Oui','Non'])

			st.markdown('#### Mort des personnages')
			self.perso_meurt = st.radio('Le personnage meurt-il ?',['Oui','Non'])
			self.prec_mort = st.selectbox('Si oui :',['De mort naturelle','Des suites d’une maladie','D’un suicide','Des suites d’un homicide','Des suites d’un accident','Autre'])

	def intro_form():
		# --------------- PRESENTATION DE LA PARTIE FORMULAIRE
		st.header("INFOS FORMULAIRE")
		st.write(""" En s'inspirant de l'étude Cinégalités du Collectif 50/50(1), l'objectif ici est d'étendre son périmètre (remonter dans le temps, plateformes indépendantes, séries) 
			et automatiser la collecte de données pour les films d'initiative française(2).""")

		st.markdown(f'<p style="font-size:10px;">(1) Rapport Cinégalité (<a style="font-size:10px;" href="https://collectif5050.com/wordpress/wp-content/uploads/2022/05/Cinegalite-s-Rapport.pdf">Télecharger le rapport complet</a>) <br> (2) film d\'initiative française (FIF): "Un Film d’Initiative Française est un film agréé par le CNC dont le financement est majoritairement ou intégralement français. Ces Films d’Initiative Française peuvent être coproduits avec des coproducteurs étrangers mais, dans ce cas, la part étrangère sera minoritaire" (Source : (<a style="font-size:10px;" href="https://www.afar-fiction.com/IMG/pdf/L_economie_des_films_francais.pdf">Afar Fiction</a>)</p>', unsafe_allow_html=True)
		
		with st.expander("Principe"):
			st.write(""" Ce formulaire est la version numérique de la grille de visionnage 
			de l'étude Cinégalité. L'objectif est ici de recueillir les données relatives aux personnages locuteurs récurrents. 
			On entend par là les personnages "apparaissant au moins dans deux séquences dans lesquelles ils s’expriment".
			Les données sont de trois ordres : \n
-les caractéristiques sociodémographiques des personnages, \n
-leur place dans la narration,\n
-certains éléments relatifs à leurs actions ou à leur trajectoire dans le récit".""")

		st.write("""Méthodologie :\n
1) Sélectionnez le film (FIF) de votre choix. S'il n'est pas dans la liste, renseignez le champs vide.\n
2) Renseignez les champs du formulaire. Vous pouvez vous aider du menu à gauche pour accédez à un thème du questionnaire.
			>>A noter : l'idéal est de remplir tous les champs.\n
3) une fois que vous avez terminé,cliquer sur "Submit". Deux options s'offrent alors à vous :\n
	1) poursuivre et renseigner un nouveau film \n
	2) terminer en cliquant sur "End" """)		

	def main():
		col_nav_form,colform = st.columns([2,5])

		with st.sidebar.container():
			st.markdown(""" <style>
				p{padding-left:10px;}
				ul, .form_ul{
				list-style-type: none;
				border-radius:6px;
				color: #000;
				background-color:#fafafa;
				padding:5px!important;}

				a:link{
				font-size:15px;
				color: #000 ;
				text-decoration: None;
				margin:0px;
				}

				a:visited{
				color:#000;
				}

				a:hover{
				color: #D0DE5C;
				text-decoration: None;
				}
				</style>""", unsafe_allow_html=True)

			titre = st.selectbox(label = 'Choisir un film', options = titre_list)
			st.session_state.titrefilm = titre

			st.markdown("""
			<p style=>Vous pouvez cliquer sur une des rubrique ci-dessous pour accéder à la section à remplir :</p>
			<ul class="form_ul">
			<li> <a href="#personnage">Personnage</a></li>
			<li> <a href="#sant">Santé</a></li>
			<li> <a href="#ge">Âge</a></li>
			<li> <a href="#situation-de-pr-carit">Situation de précarité</a></li>
			<li> <a href="#r-sidence">Lieu de résidence</a></li>
			<li> <a href="#situation-familiale">Situation familiale</a></li>
			<li> <a href="#religion">Religion</a></li>
			<li> <a href="#langue-et-accent">Langue et accent</a></li>
			<li> <a href="#vie-amoureuse-et-sexualit">Vie amoureuse et sexualité</a></li>
			<li> <a href="#travail-et-loisirs">Travail et loisirs</a></li>
			<li> <a href="#parcours-de-vie">Parcours de vie</a></li>
			<li> <a href="#activit-s-ill-gales-ou-marginales">Activités illégales ou marginales</a></li>
			<li> <a href="#rapport-aux-autorit-s-police-justice">Rapport aux autorités (police / justice)</a></li>
			<li> <a href="#violences">Violences</a></li>
			<li> <a href="#discriminations-et-propos-insultants">Discriminations et propos insultants</a></li>
			<li> <a href="#mort-des-personnages">Mort des personnages</a></li></div>""", unsafe_allow_html=True)

		placeholder = st.empty()
		placeholder2 = st.empty()
	
		while True:
			num = st.session_state.num

			if placeholder2.button('end', key=num):
				placeholder2.empty()
				#if st.button("Store result in the database"):
				db = firestore.Client.from_service_account_info(st.secrets["gcp_service_account"])
				#data_form = {u"table_results": st.session_state.data}
				data_form = {}
				#st.write(st.session_state.data) # => list
				#st.write(type(data_form)) # => dict

				for data in st.session_state.data :
					id = data['titre_film']
					index_submit = data['id_submit']
					docs = db.collection(u'formulaire').get()
					for doc in docs:
						if id == doc.id and doc.exists:
							db.collection('formulaire').document(id).collection('table_results').document(str(index_submit)).set(data)
						else : 
							db.collection('formulaire').document(id)
							db.collection('formulaire').document(id).collection('table_results').document(str(index_submit)).set(data)
				
				# --------------- LORSQUE LA PARTIE FORMULAIRE A ETE SOUMISE
				st.success('Le fomulaire a bien envoyé !')
				placeholder.write(""" Merci pour votre contribution.""")

				df = pd.DataFrame(st.session_state.data)
				st.dataframe(df)

				break

			else:
				with placeholder.form(key=str(num), clear_on_submit = True):

					new_film = NewFilm(submit_id=num)

					submitted = st.form_submit_button("Submit")

					if submitted:
						st.session_state.data.append({
		                    'id_submit': num,'titre_film' : st.session_state.titrefilm,'id_tmdb': st.session_state.idfilm,
		                    'annee_sortie': st.session_state.sortie,'nom_personnage': new_film.nom_personnage, 'role_principal': new_film.import_personnage, 
		                    'role_personnage':new_film.role_personnage,'genre_personnage':new_film.genre_personnage,'csp':new_film.catg_sociopro,
		                    'metier':new_film.prec_metier,'origine':new_film.origine,'handicap':new_film.handicap,
		                    'precision_handicap':new_film.prec_handi,'maladie':new_film.maladie,'addiction':new_film.addiction,
		                    'age':new_film.age,'precarite':new_film.precarite,'precision_precarite':new_film.prec_preca,
		                    'residence':new_film.residence,'precision_residence_si_non':new_film.prec_resid_non,'precision_residence':new_film.prec_resid,
		                    'region':new_film.region,'ville':new_film.ville,'situation_familiale':new_film.sit_fam,
		                    'enfant':new_film.enfant,'avorte':new_film.avorte,'perte_enfant':new_film.perte_enfant,
		                    'adultere':new_film.adultere,'pere':new_film.pere,'mere':new_film.mere,
		                    'orphelin':new_film.orphelin,'religon':new_film.religon,'pratiquant':new_film.pratiquant,
		                    'langue_francaise':new_film.langue_francaise,'langue_autre':new_film.langue_autre,'precision_langue':new_film.prec_langue,
		                    'accent_region':new_film.accent_region,'precision_accent_reg':new_film.prec_accent_reg,'accent_etranger':new_film.accent_etranger,
		                    'precision_accent_etranger':new_film.prec_accent_etrg,'orientation_sexuelle':new_film.orientation_sexuelle,'embrasse':new_film.embrasse,
		                    'embrasse_qui':new_film.embrasse_qui,'rapport_sexuel':new_film.rapport_sexuel,'rapport_avec_quelqu_un':new_film.rapport_avec_qq,
		                    'denude':new_film.denude,'environnement_travail':new_film.env_travail,'environnement_domestique':new_film.env_domestique,
		                    'cadre_familial':new_film.cadre_familial,'activite_loisir':new_film.act_loisir,'tache_domestique':new_film.tache_domest,
		                    'travail_parental':new_film.travail_parental,'parcours_ascendant':new_film.parcous_ascendant,'trajectoire_migratoire':new_film.traj_migratoire,
		                    'double_culture':new_film.double_culture,'parle_origine':new_film.parle_origine,'activite_marginale':new_film.act_marginale,
		                    'precision_activite_marginale':new_film.prec_act_marg,'police':new_film.police,'justice':new_film.justice,
		                    'violence_police':new_film.violence_police,'prison':new_film.prison,'mis_en_examen':new_film.mis_examen,
		                    'subit_violence':new_film.subit_violence,'precision_subit_violence':new_film.prec_subit_violence,'victime_violence_reconnu':new_film.victime_violence_reconnu,
		                    'exerce_violence':new_film.exerce_violence,'precision_exerce_violence':new_film.prec_exerce_violence,'reconnu_coupable_violence':new_film.reconnu_coupable_violence,
		                    'subit_discrimination':new_film.subit_discrimination,'precision_subit_discrimination':new_film.prec_subit_discr,'victime_discrimination_reconnu':new_film.victime_disc_reconnu,
		                    'exerce_discrimination':new_film.exerce_discrimination,'precision_exerce_discrimination':new_film.prec_exerce_discrim,'reconnu_coupable_discrimination':new_film.reconnu_coupable_discr,
		                    'est_offensant':new_film.est_offensant,'precision_est_offensant':new_film.prec_est_offensant,'est_offensant_condamné':new_film.est_offensant_condamne,
		                    'subit_offence':new_film.subit_offence,'precision_subit_offence':new_film.prec_subit_offence,'se_sent_offencé':new_film.se_sent_offence,
		                    'se_grime':new_film.se_grime,'personnage_meurt':new_film.perso_meurt,'precision_mort':new_film.prec_mort})
						st.session_state.num += 1
						placeholder.empty()
						placeholder2.empty()
					else:
						st.stop()
						placeholder.empty()

# --------------------- AGE GAP
def do_dataset():
	MOVIE_FILES = {"Harry Potter et la Coupe de Feu":"notebooks/age_gap/hp4.csv",
	               "Call me by your name":"notebooks/age_gap/call_me.csv",
	               "The Big Lebowski":"lnotebooks/age_gap/lebowski.csv",
	               "Love Actually":"love_actually.csv"}
	MOVIE_YEARS = {"Harry Potter et la Coupe de Feu":2005,
	              "Call me by your name":2017,
	              "The Big Lebowski":1998,
	              "Love Actually":2003}
	MOVIE_ORIG = {"Harry Potter et la Coupe de Feu":"Harry Potter and the Goblet of Fire",
	             "Call me by your name":"Call me by your name",
	             "The Big Lebowski":"The Big Lebowski",
	             "Love Actually":"Love Actually"}

	VERBS = ['kisses', 'sleeps with', 'goes on a date with', 'has sex with', 'marries', 'is in love with','is in couple with', 'is the father of', 'is the mother of']
	LOVE_VERBS = ['kisses', 'sleeps with', 'goes on a date with', 'has sex with', 'marries', 'is in love with','is in couple with']

	@st.cache(allow_output_mutation=True)
	def load_data_from_file(file):
	    return pd.read_csv(file)
	@st.cache
	def load_data(movie):
	    return pc.compute_relationships_in_movie(movie.cast,movie.plot, VERBS) #return pc.compute_relationships_in_movie(movie, VERBS) #movie.cast,movie.plot,

	# --------------- MENU SELECTION
	def menu_horizontal():
	    selected_info = option_menu(None,
	        ["Relations", "Couples", "Corrections"],
	        icons=['people', 'heart', "check-all",],
	        menu_icon="cast",
	        default_index=0,
	        orientation="horizontal",
	        styles={
	            "container": {"padding": "0!important", "background-color": "#fafafa"},
	            "icon": {"color": "#EEAE46", "font-size": "20px"},
	            "nav-link": {"font-size": "20px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
	            "nav-link-selected": {"background-color": "#D0DE5C"},
	        }
	    )
	    return selected_info	

	def create_network(cast,scores):
	    # Define color by relationship type
	    relationship_type = {'kisses':'love',
	                          'sleeps with':'love',
	                          'goes on a date with':'love',
	                          'has sex with':'love',
	                          'marries':'love',
	                          'is in love with':'love',
	                          'is in couple with':'love',
	                          'is the father of':'family',
	                          'is the mother of':'family',
	                          'is the son of':'family',
	                          'is the daughter of':'family',
	                          'is a friend of':'friend',
	                          'is in the family of':'family',
	                          'is the enemy of':'enemy'}
	    relationship_color = {'love':'#fca311',
	                          'family':'#cce03d',
	                          'friend':'#35c4d7',
	                          'enemy':'#000000'}
	    color_node = {0:'#187498',
	                  1:'#F9D923',
	                  2:'#36AE7C',
	              3:'#EB5353'}

	    g = Network('750px', '690px')

	    # add nodes
	    all_stars = np.unique(list(scores.star1.values)+list(scores.star2.values))
	    for star in all_stars:
	        star_data = cast[cast.name==star]
	        character = star_data['character'].iloc[0]
	        image_path = tmdb.get_person_image_from_id(star_data.id.iloc[0])
	        try:
	            image = 'https://image.tmdb.org/t/p/original'+image_path["profiles"][0]["file_path"]
	        except IndexError:
	            image = "http://cdn.onlinewebfonts.com/svg/img_233997.png"
	        g.add_node(star,
	                   label = character,
	                   title = star,
	                   shape='circularImage',
	                   image =image,
	    #                borderWidth=0, # without border
	                   color = color_node[star_data['gender'].iloc[0]], # with color border by gender
	                   borderWidth=3, # with color border
	                   size = 30,
	                   labelHighlightBold=True)

	    # add edges
	    for i,row in scores.iterrows():
	        row_relation_type = relationship_type[row.question]
	        title = "{} {} {}\n\n".format(row.character2,row.question,row.character1)+\
	                "At movie release\n"+\
	                '{} was {} years old \n'.format(row.star1,cast[cast.name==row.star1]['age_at_release'].iloc[0])+\
	                '{} was {} years old \n'.format(row.star2,cast[cast.name==row.star2]['age_at_release'].iloc[0])


	    #     if row_relation_type=='love': # is romantic relationship
	    #         title = age_gap
	        g.add_edge(row.star1,row.star2,
	                   value=100*row.score,
	                   color=relationship_color[row_relation_type],
	                   title = title)
	    return g

	def do_relations(cast,scores):
	    g = create_network(cast,scores)
	    g.save_graph(f'relation_graph.html')
	    # st.header('Connections by Company Graph')
	    HtmlFile = open(f'relation_graph.html','r',encoding='utf-8')

	    # Load HTML into HTML component for display on Streamlit
	    components.html(HtmlFile.read(), height=800, width=800)

	def get_scores(movie,title):
	    try:
	        scores = load_data_from_file(MOVIE_FILES[title])
	    except FileNotFoundError:
	        with st.spinner('Patientez...'):
	            scores = load_data(movie)
	    return scores

	def do_couples(scores, cast):
	    scores.sort_values('score',ascending=False,inplace=True)
	    scores.drop_duplicates(['star1','star2'],keep='first',inplace=True) # TO DO: avoid duplicates when star1 and star2 are inversed

	    count=0
	    for i,row in scores.iterrows():

	        if row.question not in LOVE_VERBS:
	            continue

	        if (count==10) | (row.score<0.7):
	            break

	        star_younger = {'name':row.star1,
	                 'character':row.character1,
	                 'age':cast[cast.name==row.star1]['age_at_release'].iloc[0],
	                 'gender':cast[cast.name==row.star1]['gender'].iloc[0],
	                 'image' : tmdb.get_person_image_from_id(row.star_id1)["profiles"][0]["file_path"] }
	        star_older = {'name':row.star2,
	                 'character':row.character2,
	                 'age':cast[cast.name==row.star2]['age_at_release'].iloc[0],
	                 'gender':cast[cast.name==row.star2]['gender'].iloc[0],
	                 'image' : tmdb.get_person_image_from_id(row.star_id2)["profiles"][0]["file_path"] }

	        if star_younger['age'] > star_older['age']:
	            star_aux = star_younger
	            star_younger = star_older
	            star_older = star_aux



	        st.subheader('{} et {}'.format(star_younger['character'], star_older['character']))
	        st.write('Ces personnages ont été joués par {} et {} respectivement. '.format(star_younger['name'], star_older['name']))
	        st.write('Ecart d\'âge: ' ,row.age_gap)

	        col1, col2, col3 = st.columns([1.5,5,1.5])
	        col1.image('https://image.tmdb.org/t/p/original'+star_younger['image'],width=100)


	        values = col2.slider(
	             '',
	             10, 50,
	             (star_younger['age'], star_older['age']),
	             disabled=True, key = "slider_"+str(i))

	        col3.image('https://image.tmdb.org/t/p/original'+star_older['image'],width=100)

	        count+=1

	def do_corrections(scores):
	        count=0
	        for i,row in scores.iterrows():

	            if row.question not in VERBS:
	                continue

	            if (count==10):
	                break

	            if ('mother' in row.question) | ('father' in row.question): # for parental relationship, the threshold is high
	                if row.score < 0.85:
	                    continue
	            st.subheader('{} {} {}'.format(row.character2, row.question, row.character1))
	            st.write('Score: ',row.score)
	            # st.write('Age gap: ' ,row.age_gap)

	            col1, col2, col3 = st.columns([2,2,2])
	            img_star2 = tmdb.get_person_image_from_id(row.star_id2)
	            col1.image('https://image.tmdb.org/t/p/original'+img_star2["profiles"][0]["file_path"],width=150)

	            img_star1 = tmdb.get_person_image_from_id(row.star_id1)
	            col2.image('https://image.tmdb.org/t/p/original'+img_star1["profiles"][0]["file_path"],width=150)

	            relationship_true = col3.radio('Is this relationship true?', ['Yes', 'No'],key = "couple_"+str(i))

	            st.text("\n")
	            count+=1

	menu_nav_viz_dict = {
	"Relations" : {"fn": do_relations},
	"Couples" : {"fn": do_couples},
	"Corrections" : {"fn": do_corrections},}

	def main():
	    #st.set_page_config(layout="centered")
	    title = st.selectbox("Choisissez un film:",list(MOVIE_FILES.keys()))
	    # st.title(title)

	    movie = Movie(MOVIE_ORIG[title],MOVIE_YEARS[title])
	    cast = movie.cast
	    scores = get_scores(movie,title)
	    scores = scores.sort_values('score',ascending=False)

	    selected_info= menu_horizontal()

	    if selected_info in menu_nav_viz_dict.keys():
	        if selected_info == "Relations":
	            do_relations(cast,scores[scores.score>0.4])
	        elif selected_info == "Couples":
	            do_couples(scores,cast)
	        elif selected_info == "Corrections":
	            do_corrections(scores[scores.score>0.4])
	        else :
	            st.empty()

	if __name__ == "__main__":
	    main()

	#import plotly.figure_factory as ff
	#import plotly.express as px
	#dataset_analyse = pd.read_csv("data4good_streamlit/dataset_analyse.csv")
#
	##st.dataframe(dataset_analyse)
#
	##colors_ds=[str(y) for y in dataset_analyse.annee_sortie]
#
	##fig = px.scatter(x=dataset_analyse.index.to_list(), y=[rating for rating in dataset_analyse.rating],color=colors_ds)
#
	### Add histogram data
	##x1 = np.random.randn(200) - 2
	##x2 = np.random.randn(200)
	##x3 = np.random.randn(200) + 2
#
	## Group data together
	##hist_data = [x1, x2, x3]
#
	##group_labels = ['Group 1', 'Group 2', 'Group 3']
#
	## Create distplot with custom bin_size
	##fig = ff.create_distplot(
	# #        hist_data, group_labels, bin_size=[.1, .25, .5])
#
	## Plot!
#
	#df = px.data.tips()
	#fig = px.sunburst(df, path=['day', 'time', 'sex'], values='total_bill')
	#fig.show()
#
	#st.plotly_chart(fig, use_container_width=True)

	placeholder_dataset = st.empty()
	with placeholder_dataset.container():
		st.empty()

# --------------------- ACTION MENU SIDEBAR
menu_dict = {
    "Film" : {"fn": aaaa},
    "Age Gap" : {"fn": do_dataset},
    "Formulaire" : {"fn": NewFilm},
}

if selected in menu_dict.keys():
	if selected == "Formulaire":
		intro_form()
		main()
		selected_info= ""
	elif selected == "Film":
		aaaa.do_home()
		selected_info= aaaa.menu_horizontal()
	elif selected == "Age Gap":
		do_dataset()
		selected_info= ""
		

# ---------- INFOS FILM

def do_home_info():
	colselect,colvide1,colinfofilm = st.columns([2.5,0.5,5])
	placeholderhome = st.empty()
	titre=st.session_state.titrefilm

	# --------------- COLONNES SELECTION FILM

	with colselect :
		#colselect.markdown("Sélectionnez un film", unsafe_allow_html=True)
		titre = st.selectbox(label = 'Sélectionnez un film', options = titre_list)
		st.session_state.titrefilm = titre

		id_m = df_films['id_moviedb_final'].loc[df_films['titre']==titre].values[0] #st.selectbox(label = "Choix id film", options = id_list)
		st.session_state.idfilm = id_m

		annee = df_films['annee_sortie'].loc[df_films['titre']==titre].values[0] #st.selectbox(label = "Choix année", options = annee_list)
		st.session_state.sortie = annee

		st.caption('Année de sortie : '+annee)
		st.caption('Id The movie DB : '+id_m)

		url_poster='https://api.themoviedb.org/3/movie/'+str(id_m)+'/images?api_key='+api_k
		response_poster = requests.get(url_poster)
		film_poster_dict = response_poster.json()
		film_poster=film_poster_dict.get('posters')
		film_poster_df= pd.DataFrame(film_poster)
		poster = film_poster_df['file_path'].loc[(film_poster_df['iso_639_1']=='fr')].values[0]

		# widget to display the poster
		st.session_state.poster = st.image('https://www.themoviedb.org/t/p/original/'+poster,use_column_width=True) #width=350)

	colvide1.write('')

	with placeholderhome.container():

		url_info_film= 'https://api.themoviedb.org/3/movie/'+str(id_m)+'?api_key='+api_k+'&language=fr-FR'
		response_info_film = requests.get(url_info_film)
		info_film_dict = response_info_film.json()
		info_film=info_film_dict.get('overview')

		colinfofilm.markdown("Infos film :", unsafe_allow_html=True)
		colinfofilm.write(info_film)

	placeholderhome.empty()
		
# ---------- TEST BECHDEL

def do_bechdel():
	colselect,colvide1,colinfofilm = st.columns([2.5,0.5,5])

	st.session_state.titrefilm = st.session_state.titrefilm
	st.session_state.idfilm = st.session_state.idfilm
	st.session_state.sortie = st.session_state.sortie

	placeholderbt = st.empty()

	# --------------- COLONNES SELECTION FILM

	with colselect :
		#colselect.markdown("Sélectionnez un film", unsafe_allow_html=True)
		titre = st.selectbox(label = 'Sélectionnez un film', options = titre_list)
		st.session_state.titrefilm = titre

		id_m = df_films['id_moviedb_final'].loc[df_films['titre']==titre].values[0] #st.selectbox(label = "Choix id film", options = id_list)
		st.session_state.idfilm = id_m

		annee = df_films['annee_sortie'].loc[df_films['titre']==titre].values[0] #st.selectbox(label = "Choix année", options = annee_list)
		st.session_state.sortie = annee

		st.caption('Année de sortie : '+annee)
		st.caption('Id The movie DB : '+id_m)

		url_poster='https://api.themoviedb.org/3/movie/'+str(id_m)+'/images?api_key='+api_k
		response_poster = requests.get(url_poster)
		film_poster_dict = response_poster.json()
		film_poster=film_poster_dict.get('posters')
		film_poster_df= pd.DataFrame(film_poster)
		poster = film_poster_df['file_path'].loc[(film_poster_df['iso_639_1']=='fr')].values[0]

		# widget to display the poster
		st.session_state.poster = st.image('https://www.themoviedb.org/t/p/original/'+poster,use_column_width=True) #width=350)

	colvide1.write('')

	with placeholderbt.container():
		colinfofilm.write("Resultat Test Bechdel")#, unsafe_allow_html=True)

		with colinfofilm.expander('Principe du test de Bechdel'):
			st.markdown("""Lorsque vous regardez un film, amusez-vous à vous poser ces questions. 
				Une oeuvre réussit le test si les trois interrogations suivantes reçoivent une réponse positive :
			    - Y a-t-il au moins deux personnages féminins identifiables (elles doivent être nommées) ? ;
		   		- Parlent-elles l’une avec l’autre ? ;
		   		- Parlent-elles d’autre chose que d’un personnage masculin ?""")

		# widget to display bechdel test result

		url_imbd='https://api.themoviedb.org/3/movie/'+str(st.session_state.idfilm)+'/external_ids?api_key='+api_k
		response_imbd = requests.get(url_imbd)
		film_imdb_dict = response_imbd.json()
		film_imdb=film_imdb_dict.get('imdb_id').replace('tt','')

			## 2) je retrouve le résultat du test à l'aide de l'api Bechdel Test avec l'id IMDB récupérer par l'étape 1
		url_bechdel = 'http://bechdeltest.com/api/v1/getMovieByImdbId?imdbid='+str(film_imdb)
		#st.write(url_bechdel)
		response_bechdel = requests.get(url_bechdel)
		film_bechdel_dict = response_bechdel.json()
		film_bechdel=film_bechdel_dict.get('rating')

		images = ['BechdelAI.png']

		if film_bechdel not in [1,2,3]:
			colinfofilm.caption("Ce film n'a pas encore été évalué. N'hésitez pas à le faire sur le site du Test Bechdel : https://bechdeltest.com/")
		else : 
			#colinfofilm.metric(label="Rating :", value=film_bechdel)
			if film_bechdel == 1 :
				colinfofilm.image(images * int(film_bechdel),width=130, caption = 'Il y au moins deux personnages féminins identifiables')
			if film_bechdel == 2 :
				colinfofilm.image(images * int(film_bechdel),width=130, caption = ['Il y au moins deux personnages fémininsidentifiables','qui parlent l’une avec l’autre'])
			if film_bechdel == 3 :
				colinfofilm.image(images * int(film_bechdel),width=130, caption = ['Il y au moins deux personnages féminins identifiables','qui parlent l’une avec l’autre','d’autre chose que d’un personnage masculin.'])

	placeholderbt.empty()

# ---------- DATAVISUALISATION

def do_visualisation():
	colselect,colvide1,colinfofilm = st.columns([2.5,0.5,5])

	placeholderviz = st.empty()

	# --------------- COLONNES SELECTION FILM

	#colselect,colvide1,colinfofilm = st.columns([2.5,0.5,5])

	with colselect :
		#colselect.markdown("Sélectionnez un film", unsafe_allow_html=True)
		titre = st.selectbox(label = 'Sélectionnez un film', options = titre_list)
		st.session_state.titrefilm = titre

		id_m = df_films['id_moviedb_final'].loc[df_films['titre']==titre].values[0] #st.selectbox(label = "Choix id film", options = id_list)
		st.session_state.idfilm = id_m

		annee = df_films['annee_sortie'].loc[df_films['titre']==titre].values[0] #st.selectbox(label = "Choix année", options = annee_list)
		st.session_state.sortie = annee

		st.caption('Année de sortie : '+annee)
		st.caption('Id The movie DB : '+id_m)

		url_poster='https://api.themoviedb.org/3/movie/'+str(id_m)+'/images?api_key='+api_k
		response_poster = requests.get(url_poster)
		film_poster_dict = response_poster.json()
		film_poster=film_poster_dict.get('posters')
		film_poster_df= pd.DataFrame(film_poster)
		poster = film_poster_df['file_path'].loc[(film_poster_df['iso_639_1']=='fr')].values[0]

		# widget to display the poster
		st.session_state.poster = st.image('https://www.themoviedb.org/t/p/original/'+poster,use_column_width=True) #width=350)

	colvide1.write('')

	with placeholderviz.container():

		#colinfofilm.subheader('Répartition par genre')

		url_mdb = 'https://api.themoviedb.org/3/movie/'+str(st.session_state.idfilm)+'/credits?api_key='+api_k+'&language=fr-FR'
		#st.write(url_mdb) #-- pour vérifier les données remontées par l'API

		response_l = requests.get(url_mdb)

		film_credit_dict = response_l.json()

		### Creation du dataframe du casting pour le film sélectionné

		film_credit=film_credit_dict.get('cast')
		film_credit_cast_df= pd.DataFrame(film_credit)
		film_credit_cast_df.insert(0,'id_tmdb',film_credit_dict.get('id'))
		film_credit_cast_df.insert(0,'Titre_film',st.session_state.titrefilm)
		film_credit_cast_df.insert(0,'annee_sortie',st.session_state.sortie)

		#Ajouter une colonne pour avoir la correspondance code du genre par un texte
		film_credit_cast_df.insert(5,'gender_text',["nc" if g == 0 else "femme" if g == 1 else "homme" for g in film_credit_cast_df.gender])
		#st.dataframe(film_credit_cast_df.head(3))

		### Creation du dataframe de l'équipe technique pour le film sélectionné

		film_credit_crew=film_credit_dict.get('crew')
		film_credit_crew_df= pd.DataFrame(film_credit_crew)
		film_credit_crew_df.insert(0,'id_tmdb',film_credit_dict.get('id'))
		film_credit_crew_df.insert(0,'Titre_film',st.session_state.titrefilm)
		film_credit_crew_df.insert(0,'annee_sortie',st.session_state.sortie)

		#Ajouter une colonne pour avoir la correspondance code du genre par un texte
		film_credit_crew_df.insert(5,'gender_text',["nc" if g == 0 else "femme" if g == 1 else "homme" for g in film_credit_crew_df.gender])
		#st.dataframe(film_credit_crew_df.head(3))

		# --------------------- Creation pour les dataviz
			# Create subplots: use 'domain' type for Pie subplot

		gender_viz_cast = film_credit_cast_df[['gender','gender_text','id_tmdb']].groupby(by=['gender',"gender_text"]).count().reset_index()
		gender_viz_cast.rename(columns = {'id_tmdb':'nb_by_genre'}, inplace = True)
		st.session_state.cast = gender_viz_cast
		#st.dataframe(gender_viz_cast)

		gender_viz_crew = film_credit_crew_df[['gender','gender_text','id_tmdb']].groupby(by=['gender',"gender_text"]).count().reset_index()
		gender_viz_crew.rename(columns = {'id_tmdb':'nb_by_genre'}, inplace = True)
		st.session_state.crew = gender_viz_crew
		#st.dataframe(gender_viz_crew)

		fig = make_subplots(rows=1, cols=2, specs=[[{'type':'pie'}, {'type':'pie'}]])

		fig.add_trace(go.Pie(labels=gender_viz_cast.gender_text, values=gender_viz_cast.nb_by_genre, name="Casting"),
		              1, 1)
		fig.add_trace(go.Pie(labels=gender_viz_crew.gender_text, values=gender_viz_crew.nb_by_genre, name="Equipe tech"),
		              1, 2)

		colors0 = ['red' if x == 1 else 'blue' if x == 2 else 'green' if x == 0 else 'grey' for x in gender_viz_cast['gender']]
		colors1 = ['red' if x == 1 else 'blue' if x == 2 else 'green' if x == 0 else 'grey' for x in gender_viz_crew['gender']]

		fig.update_traces(hole=.4, hoverinfo="label+value+name",marker=dict(colors=colors0), col=1) # Use `hole` to create a donut-like pie chart&

		fig.update_traces(hole=.4, hoverinfo="label+value+name",marker=dict(colors=colors1), col=2)

		fig.update_layout(width = 450,
			margin=dict(t=0, b=0, l=0, r=0),
			legend=dict(
	    		orientation="h",
	    		yanchor="bottom",
	    		y=0.05,
	    		xanchor="right",
	    		x=1),
		    title=dict(text="Répartition par genre",y=0.9,),
		    # Add annotations in the center of the donut pies.
		    annotations=[dict(text='Casting', x=0.15, y=0.5, font_size=20, showarrow=False),
		                 dict(text='Crew', x=0.83, y=0.5, font_size=20, showarrow=False)])

		colinfofilm.plotly_chart(fig)

		#colinfofilm.write("Répartition par genre de l'équipe technique")
		with colinfofilm.expander("Table de données"):
			st.write("Casting")
			st.dataframe(gender_viz_cast)
			st.write("Equipe technique")
			st.dataframe(gender_viz_crew)
	placeholderviz.empty()	

		# --------------------- ACTIVATION MENU SELECTION FILM

menu_nav_viz_dict = {
"Informations" : {"fn": do_home_info},
"Datavisualisations" : {"fn": do_visualisation},
"Test Bechdel" : {"fn": do_bechdel},}


#if selected_info in menu_nav_viz_dict.keys():
#	menu_nav_viz_dict[str(selected_info)]["fn"]()

if selected_info in menu_nav_viz_dict.keys():
	if selected_info == "Informations":
		do_home_info()
	elif selected_info == "Datavisualisations":
		do_visualisation()
	elif selected_info == "Test Bechdel":
		do_bechdel()
	else :
		st.empty()
