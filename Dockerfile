FROM ubuntu:24.04

# Install essential packages
RUN apt-get update && \
  apt-get install -y --no-install-recommends \
  openssh-server \
  sudo \
  python3 \
  tzdata

# Create SSH runtime directory
RUN mkdir -p /var/run/sshd

# Create ansible user with passwordless sudo
RUN useradd -m -s /bin/bash ansible && \
  echo 'ansible:ansible' | chpasswd && \
  echo 'ansible ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers.d/010_ansible_nopasswd

# Pre-create .ssh dir with correct permissions (in image)
RUN mkdir -p /home/ansible/.ssh && \
  chown -R ansible:ansible /home/ansible/.ssh && \
  chmod 700 /home/ansible/.ssh

# Set permissions in entrypoint in case .ssh is a mounted volume
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose SSH port
EXPOSE 22

ENV TZ=Asia/Kolkata
# ENV TZ=America/New_York

# Start SSH server with entrypoint to fix ownership dynamically
ENTRYPOINT ["/entrypoint.sh"]
CMD ["/usr/sbin/sshd", "-D"]
