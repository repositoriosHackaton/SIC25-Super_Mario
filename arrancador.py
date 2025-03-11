import subprocess
import sys
import time
import os

def main():
    try:
        # incia el fastapi en el puerto 8000
        uvicorn_cmd = ["uvicorn", "fastapi_app:app", "--reload", "--port", "8000"]
        print("Iniciando FastAPI con uvicorn en http://127.0.0.1:8000")
        uvicorn_process = subprocess.Popen(uvicorn_cmd)

        # tiempo de espera para que uvicorn cargue completamten
        time.sleep(2)

        # arranca el servidor flask del archivo app.py en el puerto 5000
        flask_cmd = [sys.executable, "app.py"]
        print("Iniciando Flask en http://127.0.0.1:5000")
        flask_process = subprocess.Popen(flask_cmd)

        print("Servidores iniciados. Presiona CTRL+C para detenerlos.")
        # funcion para detener los servicios con ctrl+c
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nDeteniendo servidores...")
        uvicorn_process.terminate()
        flask_process.terminate()
        uvicorn_process.wait()
        flask_process.wait()
        print("Servidores detenidos.")
    except Exception as e:
        print(f"Error: {e}")
        uvicorn_process.terminate()
        flask_process.terminate()

if __name__ == '__main__':
    main()
