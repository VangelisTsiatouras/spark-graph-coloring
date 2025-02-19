# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure("2") do |config|
  # The most common configuration options are documented and commented below.
  # For a complete reference, please see the online documentation at
  # https://docs.vagrantup.com.

  # Every Vagrant development environment requires a box. You can search for
  # boxes at https://vagrantcloud.com/search.
  config.vm.box = "bento/ubuntu-18.04"

  # Disable automatic box update checking. If you disable this, then
  # boxes will only be checked for updates when the user runs
  # `vagrant box outdated`. This is not recommended.
  # config.vm.box_check_update = false

  # Create a forwarded port mapping which allows access to a specific port
  # within the machine from a port on the host machine. In the example below,
  # accessing "localhost:8080" will access port 80 on the guest machine.
  # NOTE: This will enable public access to the opened port
  # config.vm.network "forwarded_port", guest: 8888, host: 8888

  # Create a forwarded port mapping which allows access to a specific port
  # within the machine from a port on the host machine and only allow access
  # via 127.0.0.1 to disable public access
  # config.vm.network "forwarded_port", guest: 80, host: 8080, host_ip: "127.0.0.1"

  # Create a private network, which allows host-only access to the machine
  # using a specific IP.
  # config.vm.network "private_network", ip: "192.168.33.10"

  # Create a public network, which generally matched to bridged network.
  # Bridged networks make the machine appear as another physical device on
  # your network.
  # config.vm.network "public_network"

  # Share an additional folder to the guest VM. The first argument is
  # the path on the host to the actual folder. The second argument is
  # the path on the guest to mount the folder. And the optional third
  # argument is a set of non-required options.
  # config.vm.synced_folder "../data", "/vagrant_data"

  # Provider-specific configuration so you can fine-tune various
  # backing providers for Vagrant. These expose provider-specific options.
  # Example for VirtualBox:
  #
  config.vm.provider "virtualbox" do |vb|
  #   # Display the VirtualBox GUI when booting the machine
  #   vb.gui = true
  #
  #   # Customize the amount of memory on the VM:
    vb.memory = "2048"
  end
  #
  # View the documentation for the provider you are using for more
  # information on available options.

  # Enable provisioning with a shell script. Additional provisioners such as
  # Puppet, Chef, Ansible, Salt, and Docker are also available. Please see the
  # documentation for more information about their specific syntax and use.
  config.vm.provision "shell", inline: <<-SHELL
  apt-get update
  apt-get -y install libssl-dev openjdk-8-jdk python3-pip python3-numpy
  wget https://cmake.org/files/v3.20/cmake-3.20.0.tar.gz
  tar -xf cmake-3.20.0.tar.gz
  rm cmake-3.20.0.tar.gz
  cd ./cmake-3.20.0
  ./configure
  make
  sudo make install
  cd /home/vagrant
  wget https://ftp.cc.uoc.gr/mirrors/apache/spark/spark-2.4.7/spark-2.4.7-bin-hadoop2.7.tgz
  tar -zxvf spark-2.4.7-bin-hadoop2.7.tgz
  rm spark-2.4.7-bin-hadoop2.7.tgz
  sed -i 's/log4j.rootCategory=INFO, console/log4j.rootCategory=ERROR, console/g' ./spark-2.4.7-bin-hadoop2.7/conf/log4j.properties.template
  mv ./spark-2.4.7-bin-hadoop2.7/conf/log4j.properties.template ./spark-2.4.7-bin-hadoop2.7/conf/log4j.properties
  pip3 install python-igraph cairocffi pandas

  SHELL

  config.vm.provision "shell", inline: "> /etc/profile.d/env_vars.sh", run: "always"
  config.vm.provision "shell", inline: "echo \"export PYSPARK_PYTHON=/usr/bin/python3\" >> /etc/profile.d/env_vars.sh", run: "always"
  config.vm.provision "shell", inline: "echo \"export PYSPARK_DRIVER_PYTHON=/usr/bin/python3\" >> /etc/profile.d/env_vars.sh", run: "always"

end