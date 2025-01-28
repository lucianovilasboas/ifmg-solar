import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
from datetime import datetime
from log import logger  

# Classe que vai lidar com os eventos
class MonitorArquivo(FileSystemEventHandler):

    # construtor
    def __init__(self, caminho='./dados/input'):
        super().__init__()
        self.pasta_input = caminho


    def on_created(self, event):
        # Verifica se o arquivo foi criado e não é um diretório
        if not event.is_directory:
            logger.info("Arquivo adicionado: %s", event.src_path)
            
            # Conta o número de arquivos na pasta dados/input
            total_arquivos = len([f for f in os.listdir(self.pasta_input) if os.path.isfile(os.path.join(self.pasta_input, f))])
            
            # Verifica se existem 3 arquivos na pasta
            if total_arquivos == 3:
                print(f"-> Existem 3 arquivos na pasta {self.pasta_input}. Executando o script.")
                logger.info("Existem 3 arquivos na pasta %s. Executando o script.", self.pasta_input)
                # Executa o comando se houver 3 arquivos na pasta
                subprocess.run(["python", "processa.py"], shell=True)


                # Obtendo o horário atual para a mensagem de commit
                horario_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                mensagem_commit = f"Commit via gitrun.py em {horario_atual}"
                git_cmd = ["python", "gitrun.py", "-m", mensagem_commit] 
                # Executa o comando para comitar os arquivos no repositório
                subprocess.run(git_cmd, shell=True) 

            else:
                print(f"-> Existem {total_arquivos} arquivos na pasta {self.pasta_input}. Aguardando mais arquivos.")
                logger.info("Existem %s arquivos na pasta %s. Aguardando mais arquivos.", total_arquivos, self.pasta_input)

# Função para iniciar a observação
def monitorar_pasta(caminho):
    event_handler = MonitorArquivo(caminho)
    observer = Observer()
    observer.schedule(event_handler, caminho, recursive=False)
    observer.start()
    print(f"=> Monitorando a pasta: {caminho}")
    logger.info("Monitorando a pasta: %s", caminho)

    try:
        while True:
            time.sleep(1)  # Espera enquanto monitora os eventos
    except KeyboardInterrupt as k:
        logger.error(f"Monitoramento interrompido. {k}")
        observer.stop()

    observer.join()

# Caminho da pasta a ser monitorada
pasta_para_monitorar = "./dados/input"

# Iniciar monitoramento
monitorar_pasta(pasta_para_monitorar)
