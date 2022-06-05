#!/usr/bin/env python
# coding: utf-8

# In[ ]:
# Importation des librairies'
import streamlit as st
import streamlit_book as stb
from streamlit_option_menu import option_menu
from google.cloud import firestore

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
st.set_page_config(page_title="HappyBirds", page_icon="🐦", layout="wide")

<<<<<<< HEAD
api_k=st.secrets["api_secrets"]["tmdb_secret"]
#api_k='4f0d9b752dd1d3a0b158afb56be09ac7'
=======
api_k='4f0d9b752dd1d3a0b158afb56be09ac7'
>>>>>>> aab37b8f9cd74f02f42edd4c246052a9715bb739

#def form_callback():
    #st.write(st.session_state.titrefilm)

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

# --------------- SIDEBAR - Projet

	# --------------- HEADER

with st.sidebar:
	def header(content):
		st.markdown(f'<p style="background-color:#7f3046;color:#FFF;height:150px;font-size:42px;display:flex;justify-content:center;align-items:center;margin-top:5px;margin-bottom:20px;text-align:center">{content}</p>', unsafe_allow_html=True)
	header("Data 4 Good : Bechdel AI")

	# --------------- Add two expanders to provide additional information about this e-tutorial and the app
with st.sidebar.expander("About this project"):
	url="https://dataforgood.fr/projects/bechdelai"
	st.image('https://dataforgood.fr/img/logo-dfg-new2.png', width=50) #use_column_width=True,
	st.write("""Mesure et automatisation du test de Bechdel, de la (sous)représentation féminine 
		et des inégalités de représentation dans le cinéma et l'audiovisuel """)
	st.markdown(f'<a href={url} style="text-decoration:none;color:#000">En savoir plus</a>', unsafe_allow_html=True)

with st.sidebar.expander("About the App"):
     st.write("""This interactive eCourse App was built by Sharone Li using Streamlit and Streamlit_book. 
     	Streamlit_book is a Streamlit companion library that was written in Python and created by Sebastian Flores Benner. 
     	\n  \nThe Streamlit_book library was released on 01/20/2022. 
     	If you want to learn more about Streamlit_book, please read Sebastian's post here:
     	https://blog.streamlit.io/how-to-create-interactive-books-with-streamlit-and-streamlit-book-in-5-steps/""")

# --------------- SIDEBAR - MENU

with st.sidebar:
	selected = option_menu(None, 
		["Film", 'Datasets', "Formulaire"], 
	    icons=['house', 'clipboard-data', "list-task"], 
	    menu_icon="cast", 
	    default_index=0, 
	    orientation="vertical",
	    styles={
	        "container": {"padding": "0!important", "background-color": "#fafafa"},
	        "icon": {"color": "orange", "font-size": "20px"}, 
	        "nav-link": {"font-size": "20px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
	        "nav-link-selected": {"background-color": "green"},
	    }
	)

# --------------- RECHERCHE DES DONNEES DANS LE DATASET - Import de la liste de films FR sortie entre 2019 et 2021
df_films = pd.read_csv("data4good_streamlit/liste_imdb_2019-2021.csv")

df_toreplace_list=['VII ','VI ','IV ','III ','II ','I ','V ']
for atr in df_toreplace_list:
	df_films['annee_sortie']=df_films[['annee_sortie']].apply(lambda x : x.str.replace(atr, '', regex=False))

# get a list of all possible ids, titles and years, for the widgets
titre_list = list(df_films['titre'].unique())
id_list = list(df_films['id_moviedb_final'].unique())
annee_list = list(df_films['annee_sortie'].unique())


# --------------- FILM : PRESENTATION DE LA PARTIE INFOS FILMS ET DATAVIZ

def do_home():
	st.header("INFOS FILM ET DATAVISUALISATIONS")
	st.write(""" Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris mi tellus, finibus quis lorem nec, 
	pharetra commodo metus. Vivamus sollicitudin sapien eget leo pretium, et scelerisque leo blandit. 
	In hendrerit sapien eget rutrum molestie. Aliquam eu consectetur enim. 
	Morbi vestibulum justo non suscipit pretium. In in congue tortor, vel euismod nulla. Proin gravida, 
	dui non accumsan mollis, dolor sapien efficitur felis, nec ornare elit mi at nisi. Etiam fringilla, 
	nibh at imperdiet varius, mauris tellus gravida urna, sed placerat velit turpis sit amet neque. 
	Donec sem metus, volutpat quis consectetur vel, porta ac est. Proin lectus tellus, aliquet et 
	rhoncus sit amet, interdum ac magna.""")


# --------------------- FORMULAIRE

with st.expander('Grille de visionnage 2 : Formulaire'):
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
		st.write(""" Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris mi tellus, finibus quis lorem nec, 
		pharetra commodo metus. Vivamus sollicitudin sapien eget leo pretium, et scelerisque leo blandit. 
		In hendrerit sapien eget rutrum molestie. Aliquam eu consectetur enim. 
		Morbi vestibulum justo non suscipit pretium. In in congue tortor, vel euismod nulla. Proin gravida, 
		dui non accumsan mollis, dolor sapien efficitur felis, nec ornare elit mi at nisi. Etiam fringilla, 
		nibh at imperdiet varius, mauris tellus gravida urna, sed placerat velit turpis sit amet neque. 
		Donec sem metus, volutpat quis consectetur vel, porta ac est. Proin lectus tellus, aliquet et 
		rhoncus sit amet, interdum ac magna.""")

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
				color: green;
				text-decoration: None;
				}
				</style>""", unsafe_allow_html=True)


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
				df = pd.DataFrame(st.session_state.data)
				st.dataframe(df)
				#if st.button("Store result in the database"):
				db = firestore.Client.from_service_account_info(st.secrets["gcp_service_account"])
				data_form = {u"table_results": st.session_state.data}
				db.collection("formulaire").document(st.session_state.titrefilm).set(data_form)
				break

			else:
				with placeholder.form(key=str(num), clear_on_submit = True):

					new_film = NewFilm(submit_id=num)

					submitted = st.form_submit_button("Submit")

					if submitted:
						st.session_state.data.append({
		                    'id_submit': num,'titre_film' : {st.session_state.titrefilm} ,'id_tmdb':  {st.session_state.idfilm} ,
		                    'annee_sortie':  {st.session_state.sortie} ,'nom_personnage': new_film.nom_personnage, 'role_principal': new_film.import_personnage, 
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
						df = pd.DataFrame(st.session_state.data)
					else:
						st.stop()
						placeholder.empty()

			st.dataframe(df)



	# --------------------- Carte
	#code_region = [11,24,27,28,32,44,52,53,75,76,84,93,94]
	#liste_region = ["Ile-de-France",'Centre-Val de Loire','Bourgogne-Franche-Comté','Normandie','Hauts-de-France','Grand Est',
	#	'Pays de la Loire','Bretagne','Nouvelle-Aquitaine','Occitanie','Auvergne-Rhône-Alpes',"Provence-Alpes-Côte d'Azur",'Corse']
	#lat = [48.8499198,47.243599,47.280513,48.879870,50.629250,48.580002,47.7632836,48.202047,43.551921,43.892723,45.1695797,43.9351691,42.039604]
	#lon = [2.6370411,0.689200,4.999437,0.171253,3.057256,7.750000,-0.3299687,-2.932644,-1.388997,3.282762,5.4502821,6.0679194,9.012893]
	#dfm = pd.DataFrame(list(zip(code_region, liste_region,lat,lon)), columns = ['Code Officiel Région', 'Nom Officiel Région','lat', 'lon'])
	#st.map(dfm)


menu_dict = {
    "Film" : {"fn": do_home},
    "Formulaire" : {"fn": NewFilm},
}


if selected in menu_dict.keys():
	if selected == "Formulaire":
		intro_form()
		main()
	else:
		menu_dict[selected]["fn"]()


# --------------- MENU SELECTION / INFOS FILM ET DATAVIZ
selected_info = option_menu(None, 
	["Informations", "Datavisualisations", "Test Bechdel"],
    icons=['camera-reels', 'pie-chart', "people",], 
    menu_icon="cast", 
    default_index=0, 
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#fafafa"},
        "icon": {"color": "orange", "font-size": "20px"}, 
        "nav-link": {"font-size": "20px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
        "nav-link-selected": {"background-color": "green"},
    }
)	

# --------------- COLONNES SELECTION FILM
colselect,colvide1,colinfofilm = st.columns([2.5,0.5,5])

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

# ---------- INFOS FILM

def do_home_info():
	placeholderhome = st.empty()

	with placeholderhome.container():

		colinfofilm.markdown("Infos film :", unsafe_allow_html=True)
		colinfofilm.write(titre+""" : Duis nec neque arcu. Fusce malesuada eu nibh non euismod. 
	In quis leo at dui pretium porta quis in ipsum. Aliquam erat volutpat. 
	Integer vulputate nisi metus, ac porttitor ante mollis ut. 
	Nam tempor suscipit quam et ullamcorper. Curabitur augue ligula, 
	tincidunt id nisi suscipit, tincidunt consectetur quam. 
	Aenean bibendum placerat sem, eu aliquet ante. Curabitur mi massa, tincidunt 
	sed semper in, imperdiet nec nisi. """)
	placeholderhome.empty()
		
# ---------- TEST BECHDEL

def do_bechdel():

	st.session_state.titrefilm = st.session_state.titrefilm
	st.session_state.idfilm = st.session_state.idfilm
	st.session_state.sortie = st.session_state.sortie

	placeholderbt = st.empty()

	#colsf, colvide2,colbechdel = st.columns([2.5,0.5,5])
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

		if film_bechdel not in [1,2,3]:
			colinfofilm.caption("Ce film n'a pas encore été évalué. N'hésitez à le faire sur le site du Test Bechdel : https://bechdeltest.com/")
		else : 
			colinfofilm.metric(label="Rating :", value=film_bechdel)

	placeholderbt.empty()

# ---------- DATAVISUALISATION

def do_visualisation():

	placeholderviz = st.empty()
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

# TEST
#		# --------------------- Viz : casting 
#
#	gender_viz_cast = film_credit_cast_df[['gender','gender_text','id_tmdb']].groupby(by=['gender',"gender_text"]).count().reset_index()
#	gender_viz_cast.rename(columns = {'id_tmdb':'nb_by_genre'}, inplace = True)
#	st.session_state.cast = gender_viz_cast
#	#st.dataframe(gender_viz_cast)
#
#	colinfofilm.write('Répartition par genre du casting')
#	with colinfofilm.expander("table de données"):
#		st.dataframe(gender_viz_cast)
#
#	colorscast = ['red' if x == 1 else 'blue' if x == 2 else 'green' if x == 0 else 'grey' for x in st.session_state.cast['gender']]
#
#	figcast = make_subplots(specs=[[{"type": "pie"}]],)
#
#	figcast.add_trace(go.Pie(labels=st.session_state.cast['gender_text'], values=st.session_state.cast['nb_by_genre'], name="Casting"),
#	              row=1, col=1)
#
#	figcast.update_traces(hole=.4, hoverinfo="label+value+name",marker=dict(colors=colorscast), row=1) # Use `hole` to create a donut-like pie chart
#
#	figcast.update_layout(width = 400,
#		margin=dict(t=0, b=0, l=50, r=0),
#    	#title_text="Casting",
#    	# Add annotations in the center of the donut pies.
#    	annotations=[dict(text='Casting', x=0.5, y=0.5, font_size=20, showarrow=False)])
#
#	colinfofilm.plotly_chart(figcast)
#
		# --------------------- Viz : crew

#	gender_viz_crew = film_credit_crew_df[['gender','gender_text','id_tmdb']].groupby(by=['gender',"gender_text"]).count().reset_index()
#	gender_viz_crew.rename(columns = {'id_tmdb':'nb_by_genre'}, inplace = True)
#	st.session_state.crew = gender_viz_crew
#	#st.dataframe(gender_viz_crew)
#
#	colinfofilm.write("Répartition par genre de l'équipe technique")
#	with colinfofilm.expander("table de données"):
#		st.dataframe(gender_viz_crew)
#
#	colorscrew = ['red' if x == 1 else 'blue' if x == 2 else 'green' if x == 0 else 'grey' for x in st.session_state.crew['gender']]
#
#	# Create subplots: use 'domain' type for Pie subplot
#	figcrew = make_subplots(specs=[[{"type": "pie"}]],)
#
#	figcrew.add_trace(go.Pie(labels=st.session_state.crew['gender_text'], values=st.session_state.crew['nb_by_genre'], name="Equipe tech"),
#	              row=1, col=1)
#
#	figcrew.update_traces(hole=.4, hoverinfo="label+value+name",marker=dict(colors=colorscrew), row=1)
#
#	figcrew.update_layout(width = 300,
#		margin=dict(t=0, b=0, l=50, r=0),
#    	#title_text="Casting",
#    	# Add annotations in the center of the donut pies.
#    	annotations=[dict(text='Crew', x=0.5, y=0.5, font_size=20, showarrow=False)])
#
#	colinfofilm.plotly_chart(figcrew)

	# --------------------- ACTIVATION MENU SELECTION FILM
menu_nav_viz_dict = {
    "Informations" : {"fn": do_home_info},
    "Datavisualisations" : {"fn": do_visualisation},
    "Test Bechdel" : {"fn": do_bechdel},
}

if selected_info in menu_nav_viz_dict.keys():
	menu_nav_viz_dict[selected_info]["fn"]()



			#menu_dict_nav = {
			#"Perso" : {"fn": show_perso},
			##"Visualisations" : {"fn": do_visualisation},
			##"Formulaire" : {"fn": NewFilm},
			#}
#
#
			#if nav_form in menu_dict_nav.keys():
			#	if selected == "Perso":
			#		show_perso()



# Streamit book properties
#tb.set_book_config(menu_title="bechdelAI",
#                   menu_icon="lightbulb",
#                   options=[
#                   		#"Home",
#                           "Datasets",
#                           "Formulaire : grille de visionnage",
#                           ],
#                   paths=[
#                   	  #"",
#                         "data4good_streamlit/data4good_dataset.py", # single file
#                         "data4good_streamlit/data4good_form.py",
#                         ],
#                   icons=[
#                   	  #"chart",
#                         "code",
#                         "robot",
#                         ],
#                   )


#st.help(pd.DataFrame)

# TEST

#option_names = ["a", "b", "c"]
#
#output_container = st.empty()
#
#next = st.button("Next/save")
#
#if next:
#    if st.session_state["radio_option"] == 'a':
#        st.session_state.radio_option = 'b'
#    elif st.session_state["radio_option"] == 'b':
#        st.session_state.radio_option = 'c'
#    else:
#        st.session_state.radio_option = 'a'
#
#option = st.sidebar.radio("Pick an option", option_names , key="radio_option")
#st.session_state
#
#if option == 'a':
#    output_container.write("You picked 'a' :smile:")
#elif option == 'b':
#    output_container.write("You picked 'b' :heart:")
#else:
#    output_container.write("You picked 'c' :rocket:")
#
#FIN DE TEST

#stb.set_chapter_config(path='data4good_streamlit', 
#	toc=False, button='top', button_previous='⬅️', 
#	button_next='➡️', button_refresh='🔄', 
#	on_load_header=None, on_load_footer=None, save_answers=False)