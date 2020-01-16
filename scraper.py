import requests     
from bs4 import BeautifulSoup
import platform, os
import time
import threading
import codecs


# Limpar o terminal dependendo do sistema operativo.

def clear():

    if platform.system() == "Windows":
        os.system('cls')
    elif platform.system() == "Linux":
        os.system('clear')

clear()

# Dados do ficheiro links.txt.


def getLinks():
    components = []
    links = []
    try: 
        with codecs.open('links.txt', 'r', 'utf-8') as file:
            line = file.readline()
            while line:
                arr = line.split()
                links.append(arr[0])
                components.append(arr[1])
                line = file.readline()
    except Exception as e:
        print('Erro no ficheiro links.txt. Algo está em falta.')
        raise e
    
    return dict(zip( components , links ))



data = getLinks()

# ---------------------------- LOADING ANIMATION ----------------------------

complete = False
message = 'Starting Requests'

def animation():
	animation = "|/-\\"
	idx = 0
	while not complete:        
	    print(f'{message} {animation[idx % len(animation)]}', end= '\r')
	    idx += 1
	    time.sleep(0.2)
	    

animation_func = threading.Thread(target=animation)
animation_func.start()

# ---------------------------------------------------------------------------

# BS4 

def bs4(html):

    soup = BeautifulSoup(html.content, 'html.parser')
    disp = soup.find('span', {'class': 'icon icon-checkmark'}) != None 
    preco = soup.find('span', {'class': 'price'}).get_text()
    nome = soup.find('span', {'class': 'base'}).get_text()
    desconto = soup.find('div', {'class': 'value--price--label-discount'})
    imagem = soup.find('img', {'class': 'gallery-placeholder__image'})['src']

    return {'nome': nome, 'disponibilidade': disp, 'preco': preco, 'desconto': desconto.get_text().replace('\n', '').replace(' ', '') if desconto else 'None', 'imagem' : imagem}
    




# Request

resultado = {}

try:
    for cmp, link in data.items():
    
        message = f'Requesting {cmp} '
        clear()
        response = requests.get(data[cmp])

        if response.status_code > 210:
            print(f'Request com status_code: {response.status_code}\n')

            if response.status_code >= 400:
                complete = True
                animation_func.join()
                print(f'Erro ao fazer request:\n\n\tComponente: {cmp}\n\tLink: {link}\n\tStatus Code: {response.status_code}\n')
                exit()

        else: 
            resultado[cmp] = bs4(response)
        
        
            
            

except Exception as e:
    complete = True
    animation_func.join()
    raise

finally:
    complete = True
    animation_func.join()


def result2HTML(result):
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

            </tr>
        </thead>
        <tbody>\n'''

    with codecs.open('ProdutosView.html', 'w', 'utf-8') as site:
        site.write(header + '\n')
        for cmp, desc in result.items():
            site.write('\t<tr class="table-primary">\n')
            site.write(f'\t\t<td>{cmp}</td>\n')
            for key, info in desc.items():
                if key == 'disponibilidade':
                    site.write('\t\t<td class=\"text-holder\">' + '<i class=\'fas fa-check\'></i>' if info else '<i class=\'fas fa-times\'></i>' + '</td>\n')
                elif key == 'imagem':
                    site.write(f'\t\t<td class=\"img-holder\"><img src=\"{info}\"></img></td>\n')
                else:
                    site.write(f'\t\t<td class=\"text-holder\">{info}</td>\n')
            site.write('\t</tr>\n')
        site.write('    </tbody>\n    </table>\n</div>\n</body>')

        
result2HTML(resultado)
os.system('ProdutosView.html')