#!/usr/bin/python
# -*- coding: <utf-8> -*-
import mail
import sys


## Argumentos passados
if len(sys.argv) >= 3:
  destinatario=sys.argv[1]
  assunto=sys.argv[2]
  mensagem=sys.argv[3]
else:
    print "Erro: Informe os parametros."
    sys.exit(1)


#con = MySQLdb.connect('dbmy0049.whservidor.com', 'marogo', 'y7R7WhsRQeE', charset="utf8") # conecta no servidor
#con.select_db('marogo') # seleciona o banco de dados
#db = con.cursor() # ee preciso ter um cursor para se trabalhar
#db.execute("SELECT emid, dest, assunto, mensagem FROM email WHERE status = ''") # faz alguma query sql
#rs = db.fetchone() # pega uma linha;
#rs = db.fetchall() # pega todas as linhas;
#rs = db.dictfetchall # pega todas as linhas, cada linha tem um dicionario com os nomes dos campos
#print(rs[0]) # imprime o valor da primeira coluna

# Configuracoes do objeto mail
#arqConf="/home/marogo/scripts/etc/emailpy.conf"
m=mail.mail()
#m.arqConf=arqConf
m.portaSmtp=465
m.conexao="ssl"

m.envia(destinatario,assunto,mensagem)
print m.erro
#for linha in rs:
#  status=m.envia(linha[1],linha[2],linha[3])
#  if status:
#    sql=("UPDATE email SET status='enviado' WHERE emid = %s " % linha[0])
#    db.execute(sql)
#    #print "Email para "+linha[1]+" enviado."
#  else:
#    sql=("UPDATE email SET status='erro' WHERE emid = %s " % linha[0])
#    db.execute(sql)
#    #print m.erro
#
#sys.exit(0)

