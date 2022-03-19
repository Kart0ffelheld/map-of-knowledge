'''
Requires:
pip install wikipedia
OR
pip install git+https://github.com/lucasdnd/Wikipedia.git

This is backwards COMPATIBLE with versions 4.5.1_main.py to newest

Helpful:
https://stackabuse.com/getting-started-with-pythons-wikipedia-api/

Issues:
- Filter smartly
	- By links in summary => parse HTML 
	- Maybe with "Backlinks" or "links point to this site"
- Let user choose starting node if there is disambiguation -JUP-
- starting article not existent -JUP-
- Is "wikipedia-api" API faster? -NOP-
'''

import wikipedia as wiki

from bs4 import BeautifulSoup
import requests
import urllib.parse

def suggest_article(text):
	try:
		return wiki.search(text)
	except:
		return [] #When error is encountered, return nothing


class WikipediaArticle():
	"""
	-- An Wikipedia Article --
	USE LIKE DESCRIBED HERE:
	
	article = WikipediaArticle(article_name)

	article.get_wikipedia_object() 
	#This way access links, links_filtered e.g.
		article.page.links_filtered
	#and summary
		article.summary

	article.get_links_in_summary()
	#Very fast way to access important links and summary as html
		article.links_from_summary
		article.summary_html
	"""

	def __init__(self, page_name, language = "en", is_starting_article = False): 
		wiki.set_lang(language) 
		self.page_name = page_name

		self.language = language
		self.is_starting_article = is_starting_article

		#These will be set through 'get_wikipedia_object()'
		self.links_filtered = None
		self.summary = None
		self.page = type('', (), {})() #This somehow just creates an empty object
		self.page.links = None
		# Access links, references, content, title and url through self.page.links
		
		#These will be set through 'get_links_in_summary()'
		self.summary_html = None
		self.links_from_summary = None
		self.filtered_links_from_summary = None

		#Error thrown if article couldn't be found
		self.error = False

	def get_wikipedia_object(self):
		try:
			print("[*] TRYING (api): ", self.page_name)	
			self._set_page()

		except wiki.DisambiguationError as e:
				best_guess = e.options[1] # Take the first of the options
				print("[*] GUESSING: ", best_guess)
				self.page_name = best_guess

		except wiki.PageError as e:
			print("[!] ERROR! Page doesnt exist:", self.page_name)
			self.error = True
			return

	def _set_page(self): # Can be used directly if there is no disambiguation for sure
		self.page = wiki.page(self.page_name, auto_suggest = False, preload=False) 
		self.summary = wiki.summary(self.page_name, auto_suggest = False)
		# Auto suggestion causes weird errors. Like "Dog" turning to "Do" in the search

	def get_links_in_summary(self): # Via "requests" and HTML parsing
		print("[*] page_name: ", self.page_name)
		phrase_formatted = self.page_name.replace(" ", "_")
		print("[*] phrase_formatted: ", phrase_formatted)
		phrase_formatted = urllib.parse.quote(phrase_formatted)
		print("[*] phrase_formatted: ", phrase_formatted)

		self.url = "https://" + self.language + ".wikipedia.org/wiki/" + phrase_formatted
		print("[*] TRYING (html): ", self.url)	
		
		try:
			raw_html = requests.get(self.url)
		except Exception as e: 
			print("[!] ERROR! request error", e)
			return

		html = BeautifulSoup(raw_html.text, 'html.parser') 
		# This is the page in HTML in parseable format
		parent = html.find('div', class_ = "mw-parser-output")
		
		if parent == None: #Parent is None if the page isnt found
			self.error = True
			print("[!] ERROR! Page doesnt exist:", self.page_name)

		else:
			summary = []
			links_filtered = []
			
			reached_summary = False
			for child in parent.children:
				if child.name == "p" and child.text.strip() != "": #There can be empty <p> tags
					reached_summary = True
					summary.append(child)
			
				elif reached_summary == True: #Then the end of summary is reached
					break
			
			self.summary_html = ""

			for part in summary: #Extract links of painfully found <a> tags
				self.summary_html += str(part)

				links = part.find_all("a")
				for link in links:
					try:
						link_string = link["href"].replace("/wiki/", "")
						#This takes the 'href' attribute of the <p> and removes "/wiki/"
						#And sometimes it just doesnt work
					except KeyError as e:
						print("[!] ERROR: " + e)
					link_string = urllib.parse.unquote(link_string) 
					# This will replace %27 with ' and %E2%80%93 with - and so on

					if self._is_real_link(link_string) and link_string not in links_filtered:
						link_string = link_string.replace("_", " ") # _ represent Spaces in the URLs

						links_filtered.append(link_string)

			print("[+] success, links found: " + str(len(links_filtered)))
			self.links_from_summary = links_filtered

			self.summary_text = BeautifulSoup(self.summary_html, 'html.parser').get_text()
			
	def _is_real_link(self, link_string):
		if link_string[0:11] == "#cite_note-":
			return False

		if link_string[0:5] == "Help:":
			return False

		if link_string[0:5] == "File:":
			return False

		if link_string[0:2] == "//":
			return False

		if link_string[0:7] == "http://":
					return False

		if link_string[0:8] == "https://":
			return False

		return True			

	def filter(self, num): 
		# Filter links
		if self.page.links is not None:
			self.links_filtered = self.page.links[:num] # Get first ... links

		elif self.links_from_summary is not None:
			self.filtered_links_from_summary = self.links_from_summary[:num] # Get first ... links

		else:
			print("[*] Nothing to filter found")
		#self.links_filtered = numpy.array(self.page.links)[:num] 
		# Using numpy should be faster but isnt ... hmmm

	def toJSON(self):
		json = {
			'page_name': self.page_name,
			'language': self.language,

			#These will be set through 'get_links_in_summary()'
			'is_starting_article': self.is_starting_article,
			'summary_html': self.summary_html,
			'summary_text': self.summary_text,
			'links_from_summary': self.links_from_summary,
			'filtered_links_from_summary': self.filtered_links_from_summary

		}
		"""
			#These will be set through 'get_wikipedia_object()'
			'links_filtered': self.links_filtered,
			'summary': self.summary,
			'page': self.page,
			'page.links': self.page.links,
		"""

		return json

