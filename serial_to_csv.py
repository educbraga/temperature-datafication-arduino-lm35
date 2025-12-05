#!/usr/bin/env python3
"""
serial_to_csv.py
Lê linhas do serial e grava 1 leitura por linha no CSV no formato:
Timestamp,Temperatura_C
2025-11-24 14:03:10,27.1
"""

import serial
import csv
import argparse
import re
from datetime import datetime
import os
import sys
import time

regex_temp = re.compile(r"([-+]?\d*\.\d+|\d+)")

def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def ensure_header(path):
    if not os.path.exists(path):
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Timestamp", "Temperatura_C"])

def main(port, baud, out_file, sample_rate):
    try:
        ser = serial.Serial(port, baud, timeout=1)
    except Exception as e:
        print("Erro abrindo porta serial:", e)
        sys.exit(1)

    print(f"Lendo dados de {port} @ {baud} baud. Salvando em {out_file} ... (CTRL+C para sair)")

    ensure_header(out_file)

    try:
        with open(out_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            last_write = 0.0
            while True:
                try:
                    raw = ser.readline()
                except Exception as e:
                    print("Erro durante leitura serial:", e)
                    break

                if not raw:
                    # sem dados no timeout
                    continue

                try:
                    line = raw.decode("utf-8", errors="ignore").strip()
                except Exception:
                    line = raw.decode("latin1", errors="ignore").strip()

                if not line:
                    continue

                # extrai número da temperatura
                m = regex_temp.search(line)
                if not m:
                    # não encontrou número, pula
                    continue

                try:
                    temp = float(m.group(1))
                except Exception:
                    continue

                # controle simples de taxa: grava no mínimo a cada sample_rate segundos
                now_ts = time.time()
                if sample_rate is None or (now_ts - last_write) >= sample_rate:
                    writer.writerow([now_str(), f"{temp:.2f}"])
                    f.flush()
                    last_write = now_ts
                    # log pequeno no stdout
                    print(f"{now_str()}, {temp:.2f}")

    except KeyboardInterrupt:
        print("\nEncerrando (KeyboardInterrupt).")
    finally:
        try:
            ser.close()
        except:
            pass

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Ler porta serial e salvar leituras em CSV (1 leitura por linha)")
    p.add_argument("--port", "-p", default="/dev/cu.usbserial-AH03BBS7", help="porta serial (ex: /dev/cu.usbserial-XXXX)")
    p.add_argument("--baud", "-b", type=int, default=9600, help="baud rate")
    p.add_argument("--out", "-o", default="dados.csv", help="arquivo CSV de saída")
    p.add_argument("--sample-rate", "-r", type=float, default=None,
                   help="opcional: mínimo de segundos entre gravações (ex: 1.0 grava no máximo 1 por segundo). Default = nenhuma limitação")
    args = p.parse_args()
    main(args.port, args.baud, args.out, args.sample_rate)