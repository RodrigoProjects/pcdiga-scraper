import requests     
from bs4 import BeautifulSoup
import platform, os
import time
import codecs
from exceptions import BadInit, NoData


class PCdiga:

    compToLinks = {}
    data = {}

    def __init__(self, file_name):
        components = []
        links = []
        try: 
            with codecs.open(file_name, 'r', 'utf-8') as file:
                line = file.readline()
                while line:
                    arr = line.split()
                    links.append(arr[0])
                    components.append(arr[1])
                    line = file.readline()
        except Exception as e:
            raise e
        
        self.compToLinks = dict(zip( components , links ))
        if not self.compToLinks:
            raise BadInit('Ficheiro vazio')

    def __str__(self):
        string = ''

        if not self.data:
            raise NoData('Request não efetuado.')
        
        for key, val in self.data.items():
            string += f'{key}: {val}'
        
        return string
    
    def __bs4(self, html):

        soup = BeautifulSoup(html.content, 'html.parser')
        disp = soup.find('span', {'class': 'icon icon-checkmark'}) != None 
        preco = soup.find('span', {'class': 'price'}).get_text()
        nome = soup.find('span', {'class': 'base'}).get_text()
        desconto = soup.find('div', {'class': 'value--price--label-discount'})
        imagem = soup.find('img', {'class': 'gallery-placeholder__image'})['src']

        return {'nome': nome, 'disponibilidade': disp, 'preco': preco, 'desconto': desconto.get_text().replace('\n', '').replace(' ', '') if desconto else 'None', 'imagem' : imagem}
    
    def request(self):
        if not self.compToLinks:
            raise BadInit

        try:
            for cmp, link in self.compToLinks.items():

                response = requests.get(link)

                if response.status_code > 210:
                    print(f'Request com status_code: {response.status_code}\n')

                    if response.status_code >= 400:
                        print(f'Erro ao fazer request:\n\n\tComponente: {cmp}\n\tLink: {link}\n\tStatus Code: {response.status_code}\n')
                        exit()

                else: 
                    self.data[cmp] = self.__bs4(response)
                
        except Exception as e:           
            raise e
    
    def result2HTML(self):

        if not self.data:
            raise NoData
        
        header = '''<!doctype html>

<html lang="pt">
<head>
    <meta charset="utf-8">

    <title>Produtos</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css" integrity="sha384-Vkoo8x4CGsO3+Hhxv8T/Q5PaXtkKtu6ug5TOeNV6gBiFeWPGFN9MuhOf23Q9Ifjh" crossorigin="anonymous">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.11.2/css/all.min.css">
    <link rel="stylesheet" href="style.css">

</head>
<body>
<div class="table-area">
    <table class="table table-striped table-bordered table-hover table-light">
        <thead class="thead-dark">
            <tr>
                <th id="empty" class="col">#</th>
                <th class="col-3">Nome</th>
                <th class="col">Disponibilidade</th>
                <th class="col">Preço</th>
                <th class="col">Desconto</th> 
                <th class="col">Imagem</th>
                <th class="col">Ações</th>

            </tr>
        </thead>
        <tbody>\n'''

        links = list(self.compToLinks.values())[::-1]

        with codecs.open('ProdutosView.html', 'w', 'utf-8') as site:
            site.write(header + '\n')
            for cmp, desc in self.data.items():
                site.write('\t<tr class="table-primary">\n')
                site.write(f'\t\t<td>{cmp}</td>\n')
                for key, info in desc.items():
                    if key == 'disponibilidade':
                        site.write('\t\t<td class=\"text-holder\">' + '<i class=\'fas fa-check\'></i>' if info else '<i class=\'fas fa-times\'></i>' + '</td>\n')
                    elif key == 'imagem':
                        site.write(f'\t\t<td class=\"img-holder\"><img src=\"{info}\"></img></td>\n')
                    else:
                        site.write(f'\t\t<td class=\"text-holder\">{info}</td>\n')
                site.write('\t\t<td class=\"button-visit\"><button type="button" onclick="location.href=\'' + links.pop() + '\'" class="btn btn-outline-info">Visitar</button></th>')
                site.write('\t</tr>\n')
            site.write('    </tbody>\n    </table>\n</div>\n</body>')
        
        os.system('ProdutosView.html')

    def result2Discord(self):
        if not self.data:
            raise NoData

        links = list(self.compToLinks.values())[::-1]

        for cmp, desc in self.data.items():
            yield (f'> **{cmp}** - ***{desc["nome"]}***\n {links.pop()}')
    
        

