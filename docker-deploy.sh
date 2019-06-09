#!/bin/bash

version=`python -c "import ostiarius; print(ostiarius.__version__)"`

echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin registry.entrydsm.hs.kr

docker build -t registry.entrydsm.hs.kr/ostiarius:${version} .

docker tag registry.entrydsm.hs.kr/ostiarius:${version} registry.entrydsm.hs.kr/ostiarius:latest

docker push registry.entrydsm.hs.kr/ostiarius:${version}
docker push registry.entrydsm.hs.kr/ostiarius:latest

exit