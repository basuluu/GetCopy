import requests
import re
from bs4 import BeautifulSoup
import os
import zipfile
import shutil
from selenium.webdriver import FirefoxOptions
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import re
import time


class CopySite:
    words_in_ban = ['base64', 'data:image/svg+xml']
    file_names = []

    #file: django.models
    def __init__(self, url: str, download_method: str, file):
        self.file = file
        self.url = url
        self.method = download_method
        self.base_path = "download/archiv" + str(hash(url + download_method))
        self.path_to_save = self.base_path + '/' + url.split("//")[-1].split("/")[0]
        if download_method == 'simple':
            content = self.get_page_with_request()
        else:
            content = self.get_page_with_selenium()
        self.soup = BeautifulSoup(content, features="html.parser")
        self._create_path()
        self._set_url_main()

    def get_page_with_request(self) -> str:
        r = requests.get(self.url)
        r.encoding = 'Windows-1251' if 'Windows-1251' in r.text else 'utf-8'
        return r.text

    def get_page_with_selenium(self) -> str:
        opts = FirefoxOptions()
        opts.add_argument("--headless")
        driver = webdriver.Firefox(firefox_options=opts)
        try:
            driver.get(self.url)
            time.sleep(8)
            for x in range(25):
                driver.execute_script("scrollBy(0,+400);")
                time.sleep(0.1)
            html = driver.page_source
            encoding = 'Windows-1251' if 'Windows-1251' in html else 'utf-8'
            html = html.encode(encoding)
        except Exception as e:
            print(e)
        finally:
            driver.close()
        return html

    def _create_path(self) -> None:
        if not os.path.exists(self.path_to_save):
            os.makedirs(self.path_to_save)

    def _set_url_main(self) -> None:
        url_parts = self.url.split('/')
        self.url_main = url_parts[0] + '//' + url_parts[2]

    def _rename_file(self, file_name: str) -> str:
        i = 0
        for name in self.file_names:
            if file_name in name:
                i += 1
        return str(i) + '_' + file_name

    def clear_meta_verification(self) -> None:
        while True:
            try:
                for meta_with_name in self.soup.find_all('meta', {"name": True}):
                    if 'verification' in meta_with_name['name']:
                        meta_with_name['name'] = ''
                        try:
                            meta_with_name['content'] = ''
                        except:
                            pass
                break
            except:
                pass

    def get_page_links(self) -> set:
        links = set()
        for anchor in self.soup.findAll('a', href=True):
            try:
                if len(anchor['href']) == 1:
                    links.add(self.url)
                elif self.url in anchor['href']:
                    links.add(anchor['href'])
                    anchor['href'] = '/'
                elif anchor['href'].startswith('/'):
                    link = self.url + anchor['href']
                    links.add(link)
                    anchor['href'] = '/'
                if self.url_main in anchor['href']:
                    anchor['href'] = '/'
            except:
                continue
        return links

    def create_links_txt(self) -> None:
        links = self.get_page_links()
        with open(self.path_to_save + '/' + 'links.txt', 'w', encoding='utf-8') as f:
            [f.write(x + '\n') for x in links]

    def check_path(self, path: str) -> bool:
        for word in self.words_in_ban:
            if word in path:
                return False
        return True

    def get_clear_file_name(self, path: str) -> str:
        file_name = path.split('/')[-1]
        file_name = file_name.split('?')[0]
        return file_name

    def download_file(self, link: str, file_name: str) -> None:
        
        if not file_name:
            return

        try:
            with open(self.path_to_save + '/' + file_name, 'wb') as f:
                ufr = requests.get(link)
                content = ufr.content

                if '.css' in file_name or '.js' in file_name:
                    content = content.decode("utf-8")
                    if '.css' in file_name:
                        content = self.download_import(link, content)
                    content = self.download_css_image(link, content)
                    content = content.encode('utf-8')
                f.write(content)
        except:
            pass

    def get_info_from_path(self, file_path: str, relative_link='') -> tuple:
        file_path = file_path.replace(' ', '')
        file_name = self.get_clear_file_name(file_path)
        if file_name in self.file_names:
            file_name = self._rename_file(file_name)
        self.file_names.append(file_name)

        if file_path.startswith('//'):
            link = 'http:' + file_path
        elif file_path.startswith('http'):
            link = file_path
        elif '..' in file_path:
            link = self.change_relative_path(relative_link, file_path)
        elif file_path.startswith('/'):
            link = self.url_main + file_path
        elif (len(relative_link) - len(self.url)) > 4:
            relative_path = relative_link[len(self.url):]
            dirs_to_file = list([value for value in relative_path.split('/') if value])
            dirs_to_file.pop()
            link = self.url + '/'.join(map(str, dirs_to_file)) + '/' + file_path
        elif len(file_path) > 3:
            link = self.url_main + '/' + file_path
        else:
            return ("", "")
        
        return (link, file_name)

    def download_css_image(self, link_to_css='', content='') -> str:
        if not content:
            link_to_css = self.url
            content = str(self.soup)

        if self.url_main not in link_to_css:
            return content
        
        img_files_list = re.findall(r'url\(.*?\)', content)
        for img in img_files_list:

            img_path = img.replace('"', '').replace("'", '')[4:-1]

            if not self.check_path(img_path):
                continue

            link, image_name = self.get_info_from_path(img_path, link_to_css)

            if not link:
                continue

            self.download_file(link, image_name)

            content = content.replace(img, """url(%s)""" % image_name)

        if link_to_css == self.url:
            self.soup = BeautifulSoup(content, features="html.parser")

        return content

    def download_js_image(self, link_to_js='', content='') -> str:
        if not content:
            link_to_css = self.url
            content = str(self.soup)
        
        if self.url_main not in link_to_css:
            return content
        
        img_files_list = re.findall(r'\.src=.+ ', content) + re.findall(r'\.src=.[\S]{0,}>', content)

        for img in img_files_list:
            img_path = img[6:]
            img_path = img_path.replace('"', '').replace("'", '').replace(' ', '').replace('>', '')
            
            if not self.check_path(img_path):
                continue

            link, image_name = self.get_info_from_path(img_path, link_to_css)

            if not link:
                continue

            self.download_file(link, image_name)

            content = content.replace(img_path, image_name)

        if link_to_css == self.url:
            self.soup = BeautifulSoup(content, features="html.parser")

        return content
        
    def download_import(self, link_to_file: str, content: str) -> str:
        css_imports = re.findall(r'import url\(.*?\)', content)
        for css_import in css_imports:

            if not self.check_path(css_import):
                continue

            css_path = css_import[11:-1].replace('"', '').replace("'", '').replace('../', '')

            if not self.check_path(css_path):
                continue

            link, import_name = self.get_info_from_path(css_path, link_to_file)

            if not link:
                continue

            try:
                download_file(link, import_name)
            except:
                continue
            content = '@import "%s"; \n' % file_name + content
        return content

    def change_relative_path(self, link_to_main_file: str, download_path: str) -> str:
        path_to_css = link_to_main_file[len(self.url_main):]
        dirs_to_css = list([value for value in path_to_css.split('/') if value])
        try:
            dirs_to_css.pop()
            if download_path[0] != '/':
                download_path = '/' + download_path
        except:
            pass
        while True:
            try:
                if download_path.startswith('/..'):
                    download_path = download_path[3:]
                    dirs_to_css.pop()
                else:
                    return self.url + '/'.join(map(str, dirs_to_css)) + download_path
            except Exception as e:
                print(e)

    def download_part(self, tag: str, attrs: dict, arg: str) -> None:
        for item in self.soup.find_all(tag, attrs=attrs):
            if not self.check_path(item[arg]):
                continue

            item_path = item[arg]

            link, file_name = self.get_info_from_path(item_path)
            if not link:
                continue

            if arg == 'data-src':
                item['data-src'] = file_name
                item['src'] = file_name
                item['pc-adapt'] = file_name
                item['original-src'] = file_name
            else:
                item[arg] = file_name

            # try:
            self.download_file(link, file_name)
            # except:
            #    continue

    def change_iframe_src(self) -> None:
        for iframe in self.soup.find_all('iframe', src=True):
            if iframe['src'].startswith('//'):
                iframe['src'] = 'http:' + iframe['src']

    def save_page(self) -> None:
        with open(self.path_to_save + '/' + 'index.html', 'w', encoding='utf-8') as f:
            f.write(str(self.soup))

    def delete_base_link(self) -> None:
        try:
            base = self.soup.find('base')
            base.decompose()
        except:
            pass
        
    def add_water_point(self) -> None:
        html = """
            var html = '<div style="height: 20px; text-align:center">';
            html += '<a href="https://getcopy.site/" style="color: black; width: 100%;">';
            html += 'getcopy.site - копирование сайтов</a></div>'
            document.body.innerHTML += html
        """
        new_script_tag = self.soup.new_tag("script", attrs={"type": "text/javascript"})
        new_script_tag.append(html)
        self.soup.append(new_script_tag)
        
    def make_zip(self) -> None:
        zip_path = self._zip_directory()
        self.file.file = zip_path
        self.file.ready = True
        self.file.save()
        shutil.rmtree(self.base_path + '/')

    def _zip_directory(self) -> str:
        zipf_name = self.base_path + '.zip'
        zipf = zipfile.ZipFile(zipf_name, 'w', zipfile.ZIP_DEFLATED)
        start_path = os.path.abspath(os.curdir)
        os.chdir(self.base_path)
        for root, dirs, files in os.walk('.'):
            for file in files:
                zipf.write(os.path.join(root, file))
        os.chdir(start_path)
        zipf.close()
        return zipf_name
    
#file: django.models
def main(url: str, download_method: str, file):
    
    copy_site = CopySite(url, download_method, file)
    
    copy_site.download_part('img', {'src': True}, 'src')
    copy_site.download_part('img', {'data-src': True}, 'data-src')
    copy_site.download_part('script', {'src': True}, 'src')
    copy_site.download_part('link', {'href': True}, 'href')

    copy_site.download_css_image()
    copy_site.download_js_image()
    
    copy_site.create_links_txt()
    copy_site.change_iframe_src()
    copy_site.clear_meta_verification()
    copy_site.delete_base_link()
    copy_site.add_water_point()
    
    copy_site.save_page()
    copy_site.make_zip()
    
