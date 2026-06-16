
rem >>>3) Instalando o Pacote FastAPI...Aguarde!
   pip install fastapi
rem  >>> Instalando o Pacote Uvicorn...Aguarde! 
   pip install "uvicorn[standard]"



rem >>>4) Instalando o pacote do Postgre....Aguarde!

 pip install psycopg2-binary

rem >>>5) Instalando o pacote de validacao do emaiç....Aguarde!

pip install email-validator

rem >>>6) Colocando em Execução a API....

  uvicorn main:app --host 0.0.0.0 --port 8000 
  

 
