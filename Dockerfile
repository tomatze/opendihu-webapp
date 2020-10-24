FROM ubuntu:20.04
ADD src /
RUN apt-get update; \
    apt-get install -y python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-gtksource-4; \
    apt-get clean -y
CMD [ "python3", "gui.py" ]
