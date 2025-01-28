import schedule
import subprocess
import time
from log import logger

# Função para executar os scripts
def executar():
    print("Executando agenda.py...")
    print("  Executando growatt_automacao.py...")
    
    try:
        logger.info("Executando growatt_automacao.py...")
        subprocess.run(["python", "growatt_automacao.py", "--sem-gui"], check=True)
        # subprocess.run(["python", "hello.py"], check=True)
        logger.info("Execução finalizada com sucesso.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Erro ao executar growatt_automacao.py: {e}")


    # print("  Executando gitrun.py...")
    # logger.info("Executando gitrun.py...")
    # subprocess.run(["python", "gitrun.py", "-m", "Data update using git"], check=True)
    # logger.info("Execução finalizada.")

    print("Finalizando execução da agenda.py")


if __name__ == "__main__":
    logger.info("Iniciando agendamento...")
    # agendamentos =  ["12:14", "12:15"]  # 
    agendamentos =  ["17:00", "19:00" ,"22:00"] 
    for i, a in enumerate(agendamentos):
        text = f"{i+1}° agendamento para {a}"
        print(text)
        logger.info(text)
        # Agendar as tarefas
        schedule.every().day.at(a).do(executar)

    # Loop para manter o agendador rodando
    while True:
        schedule.run_pending()  # Executa tarefas agendadas
        time.sleep(10)  # Pausa para evitar alto consumo de CPU
    
    logger.info("Agendamento finalizado.")
