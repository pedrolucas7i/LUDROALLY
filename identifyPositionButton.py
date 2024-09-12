import RPi.GPIO as GPIO
import subprocess
import time
import os

# Definição dos pinos GPIO para as linhas e colunas da matriz de botões (4x3)
ROW_PINS = [20, 5, 6, 19]   # Colunas (físicas), agora são linhas (lógicas)
COL_PINS = [26, 21, 16]  # Linhas (físicas), agora são colunas (lógicas)


# Configuração do modo de numeração dos pinos
GPIO.setmode(GPIO.BCM)

# Configuração das linhas como saída e das colunas como entrada com resistores pull-up
for row in ROW_PINS:
    GPIO.setup(row, GPIO.OUT, initial=GPIO.LOW)

for col in COL_PINS:
    GPIO.setup(col, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Função para escanear a matriz e identificar qual botão foi pressionado
# Função para escanear a matriz de botões
def scan_matrix():
    for row_index, row_pin in enumerate(ROW_PINS):
        GPIO.output(row_pin, GPIO.HIGH)  # Ativa a linha atual

        # Verifica o estado de cada coluna
        if GPIO.input(COL_PINS[0]) == 1:  # Coluna 0 pressionada
            GPIO.output(row_pin, GPIO.LOW)      # Desativa a linha antes de retornar
            return (row_index, 0)  # Retorna a linha e a coluna do botão pressionado

        if GPIO.input(COL_PINS[1]) == 1:  # Coluna 1 pressionada
            GPIO.output(row_pin, GPIO.LOW)      # Desativa a linha antes de retornar
            return (row_index, 1)  # Retorna a linha e a coluna do botão pressionado

        if GPIO.input(COL_PINS[2]) == 1:  # Coluna 2 pressionada
            GPIO.output(row_pin, GPIO.LOW)      # Desativa a linha antes de retornar
            return (row_index, 2)  # Retorna a linha e a coluna do botão pressionado

        GPIO.output(row_pin, GPIO.LOW)  # Desativa a linha após verificar

    return None  # Nenhum botão foi pressionado

try:
    while True:
        result = scan_matrix()
        if result:
            print(result)
        # Aguarda um curto período para ajustar a sensibilidade
        time.sleep(2)

except KeyboardInterrupt:
    # Limpa a configuração dos pinos GPIO ao encerrar o programa
    GPIO.cleanup()