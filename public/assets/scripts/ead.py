import os
import json
import shutil

import requests

# the base URL of your ArchivesSpace installation
baseURL = 'http://localhost:8089'
# the id of your repository
repository = '3'
# the username to authenticate with
user = 'natanvtumane'
# the password for the username above
password = 'admina_Natan!'

# authenticates the session
auth = requests.post(baseURL + '/users/' + user + '/login?password=' + password).json()
session = auth["session"]
# if auth.status_code == 200:
# print "Authenticated!"
headers = {'X-ArchivesSpace-Session': session}

# number components and include DAOs
export_options = '?numbered_cs=true&?include_daos=true&?include_unpublished=false'

# Gets the IDs of all resources in the repository
resourceIds = requests.get(baseURL + '/repositories/' + repository + '/resources?all_ids=true', headers=headers)

# Sets the location where the EAD XMLs should be saved
eadxml_path = '/var/archivesspace/eadxml/'
if os.path.exists(eadxml_path):
    shutil.rmtree(eadxml_path)  # Deletes all old files (including folder)
if not os.path.exists(eadxml_path):
    os.mkdir(eadxml_path)

# Exports EAD for all resources in repositories/2 where finding_aid_status = "published"
for id in resourceIds.json():
    resource = (requests.get(baseURL + '/repositories/' + repository + '/resources/' + str(id), headers=headers)).json()
    resourceID = resource["id_0"]
    eadID = resource.get("ead_id")
    published = resource["publish"]
    if eadID and published:
        ead = requests.get(
            baseURL + '/repositories/' + repository + '/resource_descriptions/' + str(id) + '.xml' + export_options,
            headers=headers).text
        f = open(eadxml_path + eadID.replace('/', '-') + '.xml', 'w')
        f.write(ead.encode('utf-8'))
        f.close()

# Output path for compressed file (leave the extension off)
output_path = '/var/archivesspace/plugins/ou_branding/frontend/assets/eadxml/eadxml'

if os.path.exists(output_path):
    shutil.rmtree(output_path)  # Deletes all old files (including folder)
if not os.path.exists(output_path):
    os.mkdir(output_path)

# Directory to be zipped
source_path = eadxml_path

# Compresses the source directory as a .zip file and saves it to the output path
shutil.make_archive(output_path, 'zip', source_path)
