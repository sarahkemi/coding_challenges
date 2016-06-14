from bs4 import BeautifulSoup
import pycurl
from io import BytesIO
import csv
import re

all_posts = [] #list to keep track of all posts to avoid duplicates due to quotes

def grab_page(url):
	print("Downloading page..")
	buffer = BytesIO()
	c = pycurl.Curl()
	c.setopt(c.URL, url)
	c.setopt(c.WRITEDATA, buffer)
	c.perform()
	c.close()

	body = buffer.getvalue()
	print("Page downloaded")
	return body



def grab_links(root_url,parameter):
	html = grab_page(root_url + parameter)
	root = BeautifulSoup(html,'html.parser')

	#search for the thread navigation links
	links = []

	for link in root.find_all('a'):
		href = str(link.get('href'))
		if href.startswith(parameter) and re.compile("^-?[0-9]+$").match(link.get_text()): #check if the link is a navigation link and if the link leads to a numbered page
			links.append(href)

	#remove duplicates
	output = []

	for link in links:
		if link not in output:
			output.append(link)

	return output


def grab_posts(html):

	data = BeautifulSoup(html,'html.parser')

	#strip the page of all names, dates, body
	names = data.find_all("span", "name")
	dates = data.find_all(string=re.compile("^Posted"))
	body = []
	for td in data.findAll("td", attrs={"colspan": 2}):
		if str(td).find('class="postbody"') > 0:
			body.append(td)

	posts = []

	for post in body:
		post_text = post.get_text().encode('unicode-escape').decode('ascii')
		posts.append(post_text)

	#append each post as a line to the file		
	for n in range(len(posts)):

		output = []

		#get post id
		output.append(names[n].a['name'])
		#get poster's name
		output.append(str(names[n].b.string))
		#get post date and time
		output.append(str(dates[n].string[8:]))
		#get post body
		output.append(posts[n]) 

		#write each post to csv
		with open('forum.csv', 'a', newline='') as fp:
			write = csv.writer(fp, delimiter=';')
			write.writerows([output])



#let's get all these posts!!

root_forum = 'http://www.oldclassiccar.co.uk/forum/phpbb/phpBB2/'
first_page = 'viewtopic.php?t=12591'
forum_pages = grab_links(root_forum,first_page)

first = grab_page(root_forum + first_page)
grab_posts(first)

for page in forum_pages:
	page_html = grab_page(root_forum + page)
	grab_posts(page_html)

print("All done!")






