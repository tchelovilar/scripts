#!/usr/bin/env  python

#
#

#
import boto3
from datetime import datetime, timedelta
import os

#
ec2 = boto3.client('ec2')


#
def backupEBS(ebsFilters=[],snapshotDaysExpirate=2):
  dateNow=datetime.now().strftime("%Y-%m-%d-%H%M")
  dateNowUnix=datetime.now().strftime("%s")
  ebsList=ec2.describe_volumes(Filters=ebsFilters)
  for volume in ebsList["Volumes"]:
    ebsName=""
    for tag in volume["Tags"]:
      if tag["Key"] == "Name":
        ebsName=tag["Value"]
    snapName="bkp-"+ebsName+"-"+volume["VolumeId"]+"_"+dateNow
    snapDescription="InstanceID: "+volume["Attachments"][0]["InstanceId"]+" VolumeID: "+volume["VolumeId"]
    snapTags=[{'Key': 'Name', 'Value': snapName},{'Key':'backupDateUnix','Value': dateNowUnix}]
    ec2.create_snapshot(VolumeId=volume["VolumeId"], Description=snapDescription, TagSpecifications=[{'ResourceType': 'snapshot' ,'Tags': snapTags}])
    #
    removeOldSnapshots(volume["VolumeId"],snapshotDaysExpirate)


#
def removeOldSnapshots(volumeId,snapshotDaysExpirate=2):
  dateExpireSnap=(datetime.now() - timedelta(days=snapshotDaysExpirate,minutes=60)).strftime("%s")
  filter=[{'Name':'tag-key','Values': ['backupDateUnix']},{'Name':'volume-id','Values':[volumeId]}]
  snapList=ec2.describe_snapshots(Filters=filter)
  for snap in snapList["Snapshots"]:
    snapId=snap['SnapshotId']
    snapDate="0"
    for tag in snap['Tags']:
      if tag['Key'] == 'backupDateUnix':
        snapDate=tag['Value']
    # dateExpireSnap=1525716789
    if snapDate != "0" and int(dateExpireSnap) >= int(snapDate):
      ec2.delete_snapshot(SnapshotId=snapId)


def lambda_handler(event, context):
  SNAPSHOT_DAYS_EXPIRATE=2
  if 'SNAPSHOT_DAYS_EXPIRATE' in os.environ:
    SNAPSHOT_DAYS_EXPIRATE=os.environ['SNAPSHOT_DAYS_EXPIRATE']
  Filter=[{'Name':'tag:k8s.io/role/master', 'Values': ['1']}]
  backupEBS(ebsFilters=Filter,snapshotDaysExpirate=SNAPSHOT_DAYS_EXPIRATE)
  return "Ok"

#lambda_handler(1, 2)
# Filter=[{'Name':'tag:k8s.io/role/master', 'Values': ['1']}]
# backupEBS(ebsFilters=Filter)
