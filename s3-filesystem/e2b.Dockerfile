# You can use most Debian-based base images
FROM ubuntu:22.04

# Install dependencies and customize sandbox
RUN apt update && apt -y install sudo
RUN sudo apt -y install s3fs

# sudo apt -y install kmod