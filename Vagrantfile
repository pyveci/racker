# -*- mode: ruby -*-
# vi: set ft=ruby :

# Specify minimum Vagrant version and Vagrant API version
Vagrant.require_version '>= 1.6.0'
VAGRANTFILE_API_VERSION = '2'

# Create and configure the VMs
Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

  # Always use Vagrant's default insecure key
  config.ssh.insert_key = false

  config.vm.define "postroj-debian11" do |machine|

    # Don't check for box updates
    machine.vm.box_check_update = false

    # Specify the hostname of the VM
    machine.vm.hostname = "postroj-debian11"

    # Specify the Vagrant box to use
    machine.vm.box = "generic/debian11"
    #machine.vm.box = "debian/stretch64"
    #machine.vm.box = "ubuntu/bionic64"

    # Configure host specifications
    machine.vm.provider :virtualbox do |v|

      v.memory = 2048
      v.cpus = 2

      v.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
      #v.customize ["modifyvm", :id, "--memory", 1024]
      v.customize ["modifyvm", :id, "--name", "postroj-debian11"]
    end

    # Install required packages
    machine.vm.provision :shell, inline: <<-SHELL
        sudo apt-get update
        sudo apt-get install --yes systemd-container skopeo umoci python3-pip python3-venv
    SHELL

  end

  # Mount source code directory
  config.vm.synced_folder ".", "/usr/src/postroj"

end # Vagrant.configure
