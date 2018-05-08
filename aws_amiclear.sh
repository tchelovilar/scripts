#!/bin/bash

CMD=$1

# Padrao das variaveis
OUTPUT=text
OPT_LIMPAR_INATIVAS=0

# Verificar se o jq está instalado
jq --version > /dev/null 2>&1
if [ $? -gt 0 ]  ; then
  echo "Instale o jq para usar esse script (apt install jq ou yum install jq)"
  exit 1
fi

#
function listar {
  # Verificar ID da Conta
  accID=$(aws sts get-caller-identity | jq -r .Account)
  #
  lauchConfList=$(aws autoscaling describe-launch-configurations | jq -r '.LaunchConfigurations[] | { "ImageId":  .ImageId , "LC": .LaunchConfigurationName } | tostring')
  count=0
  while read img ; do
    imgId=$(jq -r .ImageId <<< $img)
    imgName=$(jq -r .Name <<< $img)
    imgSnap=$(jq -r '.Snapshots | tostring' <<< $img)
    # Lista de instancias que utilizam a AMI
    instances=$(aws ec2 describe-instances --filters '{ "Name": "image-id", "Values": ["'$imgId'"] }' | jq -r '.Reservations[] | { instances: [ { "InstanceId": .Instances[].InstanceId,"Tags": [ .Instances[].Tags ] } ] } | tostring')
    # Verificar Launch Configurations que utilizam a AMI
    lcList=$( grep $imgId <<< "$lauchConfList" )
    # Saida de texto
    if [ "$OUTPUT" == "text" ] ;  then
      echo -e "\n\e[32;1m## $imgName - $imgId ##\e[m"
      if [ -n "$instances" ] ; then
        echo "- Instancias"
        jq -r .instances[].InstanceId <<< "$instances"
      fi
      if [ -n "$lcList" ] ; then
        echo "- Autoscaling LaunchConfigurations"
        jq -r .LC <<< "$lcList"
      fi
    else
      test $count -eq 0 && echo -n -e "Image ID, Image Name, Snapshots, Instancias, LaunchConfigurations \n"
      instances_comma=$(jq -r .instances[].InstanceId <<< "$instances" | tr "\n" " ")
      lc_space=$(jq -r .LC <<< "$lcList" | tr "\n" " ")
      snapshotsList=$(tr -d '"[]' <<< ${imgSnap} | tr , " ")
      echo -n -e "${imgId},${imgName},${snapshotsList},${instances_comma},${lc_space}\n"
    fi
    # Tratamento de remocao
    if [ $OPT_LIMPAR_INATIVAS -eq 1 ] && [ -z "${instances}${lcList}" ]; then
      echo -e "Deseja remover a imagem acima (y/n)?"
      read -n 1 resp < /dev/tty
      if [ "$resp" == "y" ]; then
        echo -e "\nRemovendo AMI $imgId..."
        aws ec2 deregister-image --image-id $imgId
        echo "Removendo Snapshots da AMI..."
        for snapID in $(jq -r .Snapshots[] <<< $img) ; do
          echo - $snapID
          aws ec2 delete-snapshot --snapshot-id $snapID
        done
      fi
    fi
    let count++
  done <<< "$(aws ec2 describe-images --owners $accID | jq -r '.Images[] | { "ImageId": .ImageId , "Name": .Name , "Snapshots": [ .BlockDeviceMappings[].Ebs.SnapshotId ] } | tostring')"
}

function ajuda {
  echo -e "### Opcoes disponiveis:\n"
  echo -e "\e[34;1mlista\e[m"
  echo -e "  Exibe a lista de AMIs e instancias  que as utilizam.\n"
  echo -e "\e[34;1mlista-csv\e[m"
  echo -e "  Exibe a lista de AMIs e instancias no formato csv\n"
  echo -e "\e[34;1mlimpar-inativas\e[m"
  echo -e "  Exibe as AMIs que não possuem nenhum uso com a opcao para remover."
  echo -e "  Confirmando a remocao para cada uma."
}


case $CMD in
  limpar-inativas )
    OPT_LIMPAR_INATIVAS=1
    listar
  ;;
  lista )
    OPT_LIMPAR_INATIVAS=0
    listar
  ;;
  lista-csv )
    OPT_LIMPAR_INATIVAS=0
    OUTPUT=csv
    listar
  ;;
  * )
    ajuda
  ;;
esac
