#!/usr/local/bin/python
import os
import re
import smtplib, base64


class mail:
  arqConf="/usr/local/etc/email.conf"
  portaSmtp="587"
  conexao="ssl"
  remetente=""
  erro=""
  def encode_plain(self,user, password):
    return base64.b64encode("\0%s\0%s" % (user, password))
  
  def checaVar(self):
    if not os.path.isfile(self.arqConf):
	self.erro='Arquivo de configuracao inexistente. Por padrao o arquivo deve ficar na localizacao:\n'+self.arqConf
	return False
    else:
	arq=open(self.arqConf,'r')
	for linha in arq:
	    conf=linha.split("=")
	    if len(conf) > 1:
		valor=re.sub('\\n$', "", conf[1])
		if conf[0] == "servidor":
		    self.servidor=valor
		elif conf[0] == "usuario":
		    self.usuario=valor
		elif conf[0] == "senha":
		    self.senha=valor
		elif conf[0] == "remetente":
		    self.remetente=valor
    if (self.remetente == ""):
      self.erro="Remetente inexistente"
      return False
    
  def envia(self,destinatario,assunto,menssagem):
    a=self.checaVar()
    if (a == False):
      return False
    msg = ("From: %s\r\nTo: %s\r\nSubject: %s\r\nContent-Type: text/plain; charset=UTF-8; format=flowed\r\n\r\n" % (self.remetente, destinatario, assunto) )
    msg=msg + menssagem
    try:
      if (self.conexao == "ssl"):
        #server.set_debuglevel(1)
        server = smtplib.SMTP_SSL(self.servidor,self.portaSmtp)
        #sys.exit(1)
        #server.helo()
        #server.docmd("AUTH", "PLAIN " + self.encode_plain(self.usuario, self.senha))
        server.login(self.usuario,self.senha)
      elif (self.conexao == "startls"):
        server = smtplib.SMTP(self.servidor,self.portaSmtp)
        server.starttls()
        server.login(self.usuario,self.senha)
      else:
        server = smtplib.SMTP(self.servidor,self.portaSmtp)
        server.login(self.usuario,self.senha)
    except:
      self.erro="Erro: Falha na conexao com o Servidor: "+self.servidor+" Porta: "+str(self.portaSmtp)
      #self.erro="Erro: Falha na conexao com o Servidor: "+self.servidor
      return False
    #server.set_debuglevel(1)
    server.sendmail(self.remetente, destinatario, msg)
    server.quit()
    return True
