#!/bin/bash
XSOCK=/tmp/.X11-unix
XAUTH=$(mktemp)
trap "rm $XAUTH" EXIT

xauth nlist $DISPLAY | sed -e 's/^..../ffff/' | xauth -f ${XAUTH} nmerge -

docker run -it --rm \
	--env="USER_UID=$(id -u)" \
	--env="USER_GID=$(id -g)" \
	--env="USER_NAME=$(id -un)" \
	--env="DISPLAY=$DISPLAY" \
  --env="XAUTHORITY=/tmp/xauth" \
  --volume=$XAUTH:/tmp/xauth:rw \
	--volume=${XSOCK}:${XSOCK} \
	--volume=$HOME:$HOME \
  opendihu-webapp:1.0
