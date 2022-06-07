# -*- mode: ruby -*-
# vi: set ft=ruby :

# Specify minimum Vagrant version and Vagrant API version
Vagrant.require_version '>= 1.6.0'
VAGRANTFILE_API_VERSION = '2'

# Create and configure the VMs
Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

  # Always use Vagrant's default insecure key
  config.ssh.insert_key = false

  # Mount source code directory
  config.vm.synced_folder ".", "/usr/src/racker"

  config.vm.define "rackerhost-debian11" do |machine|

    # Don't check for box updates
    machine.vm.box_check_update = false

    # Specify the hostname of the VM
    machine.vm.hostname = "rackerhost-debian11"

    # Specify the Vagrant box to use
    machine.vm.box = "generic/debian11"
    #machine.vm.box = "debian/stretch64"
    #machine.vm.box = "ubuntu/bionic64"

    # Configure host specifications
    machine.vm.provider :virtualbox do |v|

      v.memory = 4096
      v.cpus = 4

      v.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
      v.customize ["modifyvm", :id, "--name", "rackerhost-debian11"]
      #v.customize ["modifyvm", :id, "--memory", 4096]

      # Turn on nested virtualization.
      v.customize ["modifyvm", :id, "--nested-hw-virt", "on"]

      # https://forums.virtualbox.org/viewtopic.php?f=1&t=59379
      v.customize ["modifyvm", :id, "--vtxux", "on"]
    end

    machine.vm.provision :shell, inline: <<-SHELL
        echo "Installing required packages"
        set -x
        sudo apt-get update
        sudo apt-get install --yes systemd-container skopeo umoci python3-pip python3-venv
    SHELL

    # Setup Racker sandbox
    machine.vm.provision :shell, privileged: true, inline: <<-SHELL
        SOURCE=/usr/src/racker
        TARGET=/opt/racker
        RACKER=/usr/local/bin/racker
        POSTROJ=/usr/local/bin/postroj

        echo "Installing package from ${SOURCE} to virtualenv at ${TARGET}"
        echo "Installing program to ${PROGRAM}"
        set -x
        whoami
        python3 -m venv ${TARGET}
        set +x
        source ${TARGET}/bin/activate
        set -x
        python -V
        pip install --editable=${SOURCE}[test]
        racker --version
        ln -sf ${TARGET}/bin/racker ${RACKER}
        ln -sf ${TARGET}/bin/postroj ${POSTROJ}
    SHELL

  end

end # Vagrant.configure
