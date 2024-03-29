# -*- coding: utf-8 -*-
from app import db
from models import Post
import requests
from bs4 import BeautifulSoup
import re
from pushover import Pushover

class Spider:
	board_base_url = 'http://www.ppomppu.co.kr/zboard/'
	board_index_url = 'http://www.ppomppu.co.kr/zboard/zboard.php?id=phone'
	keywords = ['Band', 'band', '밴드']

	def main(self):
		for link in reversed(self.getPostLinks(self.board_index_url)):
			try:
				post = self.postExtractor(link)

				if db.session.query(Post.id).filter(Post.title==post['title'], Post.content==post['content']).count() > 0:
					print 'Skip: ' + post['link']
				else:
					print 'Add: ' + post['link']
					self.addPost(post)
			except Exception as e:
				print 'Exception: ' + str(e)

	def addPost(self, post):
		self.keywordChecker(post)
		db.session.add(Post(**post))
		db.session.commit()

	def keywordChecker(self, post):
		hasKeyword = False

		for keyword in self.keywords:
			if unicode(keyword, 'utf-8') in post['content']:
				hasKeyword = True
				break

		if hasKeyword:
			push = Pushover()
			push.sendNotification(title=post['title'], message=post['content'], url=post['link'])

	def getPostLinks(self, url):
		links = []
		r = requests.get(url);
		s = BeautifulSoup(unicode(r.content, 'cp949').encode('utf-8'))
		rows = s.find_all('tr', class_=re.compile("list[0-1]"));
	
		for row in rows:
			link = row.find('font', class_='list_title').parent['href']
			links.append(link)

		return links

	def postExtractor(self, url):
		url = self.board_base_url + url
		post = dict()
		r = requests.get(url);
		s = BeautifulSoup(unicode(r.content, 'cp949').encode('utf-8'))

		post['link'] = url
		post['title'] = s.find('font', class_='view_title2').get_text()
		post['content'] = unicode()

		for tag in s.find_all('table', class_='pic_bg'):
			text = tag.get_text().strip()
			if text:
				post['content'] += text

		return post

if __name__ == "__main__":
	spider = Spider()
	spider.main()

