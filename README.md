
1. Primero necesitamos crear un entorno virtual con virtualenv

    virtualenv .venv

2. Debemos activar el entorno virtual usando lo siguiente en la terminal

    .\.venv\Scripts\activate

3. Una vez el entorno activado... Ahora debemos instalar las librerias de python del archivo requeriments.txt

    pip install -r requirements.txt

4. Luego de hecho eso arrancamos los servicios de flask app.py y uvicorn con un solo archivo arracador

    python .\arrancador.py

5. En el navegador ingresamos lo siguiente para acceder al sitio web

    http://127.0.0.1:5000/

6. Se debe crear un nueva cuenta en la pagina, cuidado que el campo del correo electronico es sensible a las mayusculas

7. Y ya dentro puedes solicitar un acta de bautiso como prueba con esta cedula que ya esta registrada "20862342" sin comillas, ni espacios ni puntos
o tambien con esta otra cedula "14555555"

8. Para detener el servicio se debe seleccionar la terminal y presionar ctrl+c dos veces

9. Apartado del admin "admin@test.com" y la contraseña "Admin123$"

9. Y listo :)
