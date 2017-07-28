# -*- coding: utf-8 -*-
"""
Created on Sun Jul 23 11:03:51 2017

@author: Quantum Liu
"""

import re,os,traceback
import requests
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from multiprocessing import Pool,cpu_count,freeze_support


def validatetitle(title):
    '''
    transform a string to a validate filename
    将字符串转化为合法文件名
    '''
    rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/\:*?"<>|'
    new_title = re.sub(rstr, "", title).replace(' ','')
    return new_title


class Chapter():
    def __init__(self,comic_title,comic_dir,chapter_title,chapter_url):
        self.comic_title,self.comic_dir,self.chapter_title,self.chapter_url=comic_title,comic_dir,chapter_title,chapter_url
        self.chapter_dir=os.path.join(self.comic_dir,validatetitle(self.chapter_title))
        if not os.path.exists(self.chapter_dir):
            os.mkdir(self.chapter_dir)
        self.pages=[]

    def get_pages(self):
        '''
        Get all pages' urls using selenium an phantomJS
        '''
        r_slt=r'onchange="select_page\(\)">([\s\S]*?)</select>'
        r_p=r'<option value="(.*?)".*?>第(\d*?)页<'
        try:
            dcap = dict(DesiredCapabilities.PHANTOMJS)
            # 不载入图片，爬页面速度会快很多
            dcap["phantomjs.page.settings.loadImages"] = False
            driver = webdriver.PhantomJS(desired_capabilities=dcap)
            driver.get(self.chapter_url)
            text=driver.page_source
            st=re.findall(r_slt,text)[0]
            self.pages = [(int(p[-1]),p[0]) for p in re.findall(r_p,st)]
        except Exception:
            traceback.print_exc()
            self.pages = []
        finally:
            driver.quit()
            print('Got {l} pages in chapter {ch}'.format(l=len(self.pages),ch=self.chapter_title))
            return self.pages
    
    def download_page(self,page):
        '''
        Download a page and save it in a local file
        '''
        headers={'use-agent':"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36",'referer':self.chapter_url}
        n=page[0]
        url=page[-1]
        if not os.path.exists(self.chapter_dir):
            os.mkdir(self.chapter_dir)
        path=os.path.join(self.chapter_dir,str(n)+'.'+url.split('.')[-1])
        try:
            print('Downloading page {n} into file {f}'.format(n=n,f=path))
            res=requests.get(url,headers=headers)
            data=res.content
            with open(path,'wb') as f:
                f.write(data)
        except Exception:
            e=traceback.format_exc()
            print('Got eorr when downloading picture\n'+e)
            return 0
        else:
            return 1
    
    def download_chapter_s(self):
        '''
        Download all pages of the chapter not using multiprocessing
        '''
        freeze_support()
        results=[]
        if not self.pages:
            print('No page')
            return None
        print('Downloading chapter {c}'.format(c=self.chapter_title))
        results=[self.download_page(page) for page in self.pages]
        num=sum(results)
        print('Downloaded {} pages'.format(num))
    def download_chapter_m(self):
        '''
        Download all pages of the chapter using multiprocessing
        '''
        results=[]
        if not self.pages:
            print('No page')
            return None
        freeze_support()
        mp=Pool(min(8,max(cpu_count(),4)))
        for page in self.pages:
            results.append(mp.apply_async(self.download_page,(page,)))
        mp.close()
        mp.join()
        num=sum([result.get() for result in results])
        print('Downloaded {} pages'.format(num))


class Comic():
    '''
    An abstraction of comic
    '''
    def __init__(self,comic_url,comic_title=None,comic_dir=None):
        self.comic_url=comic_url
        n_comic_title,self.des,self.cover,self.chapter_infos=self.get_info()
        self.chapter_num=len(self.chapter_infos)
        self.comic_title=(comic_title if comic_title else n_comic_title)
        self.comic_dir=os.path.abspath((validatetitle(comic_dir) if comic_dir else validatetitle(self.comic_title)))
        if not os.path.exists(self.comic_dir):
            os.mkdir(self.comic_dir)
        print('There are {n} chapters in comic {c}'.format(n=self.chapter_num,c=self.comic_title))
        self.chapters={info[0]:Chapter(self.comic_title, self.comic_dir, *info) for info in self.chapter_infos}
        self.pages=[]
    def get_info(self):
        '''
        Get informations of the comic
        return:
            comic title,description,cover url,chapters' urls
        '''
        headers={'use-agent':"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"}
        root='http://manhua.dmzj.com'
        r_title=r'<span class="anim_title_text"><a href=".*?"><h1>(.*?)</h1></a></span>'
        r_des=r'<meta name=\'description\' content=".*?(介绍.*?)"/>'
        r_cover=r'src="(.*?)" id="cover_pic"/></a>'
        r_cb=r'<div class="cartoon_online_border" >([\s\S]*?)<div class="clearfix"></div>'
        r_cs=r'<li><a title="(.*?)" href="(.*?)" >.*?</a>'
        try:
            text=requests.get(self.comic_url,headers=headers).text
        except ConnectionError:
            traceback.print_exc()
            raise ConnectionError
        title=re.findall(r_title,text)[0]
        cb=re.findall(r_cb,text)[0]
        chapter_urls=[(c[0],root+c[1]+'#@page=1') for c in re.findall(r_cs,cb)]
        cover_url=re.findall(r_cover,text)[0]
        des=re.findall(r_des,text)
        return title,des,cover_url,chapter_urls
    
    def update(self):
        n_chapter_infos=self.get_info()
        num=0
        for info in n_chapter_infos:
            if not info in self.chapter_infos:
                num+=1
                self.chapters[info[0]]=Chapter(self.comic_title, self.comic_dir, *info)
        if num:
            self.chapter_infos=n_chapter_infos
            print('Got {n} new chapters:\n{chs}'.format(n=num,chs='\n'.join([info[0] for info in self.chapter_infos])))
        else:
            print('No new chapter found')
    def print_chapters(self):
        text='There are {n} chapters in comic {c}:\n{chs}'.format(n=self.chapter_num,c=self.comic_title,chs='\n'.join([info[0] for info in self.chapter_infos]))
        print(text)
        return text

    def download_chapter(self,key,m=True):
        '''
        Download a chapter by chapter title
        key:title
        m:multiprocessing or not
        '''
        if not key in self.chapters:
            print('No such chapter {key}\nThere are chapters:\n{chs}'.format(key=key,chs='\n'.join(self.chapters.keys())))
            return None
        if not self.chapters[key].pages:
            self.pages+=self.chapters[key].get_pages()
        (self.chapters[key].download_chapter_m() if m else self.chapters[key].download_chapter_s())

    def download_all_chapters_s(self,m=False):
        print('Downloading all chapters of comic {title} into dir {d}'.format(title=self.comic_title,d=self.comic_dir))
        [self.download_chapter(key=title,m=m) for title in self.chapters.keys()]

    def download_all_chapters_m(self):
        freeze_support()
        mp=Pool(min(8,max(cpu_count(),4)))
        for key in self.chapters.keys():
            mp.apply_async(self.download_chapter,(key,False))
        mp.close()
        mp.join()
