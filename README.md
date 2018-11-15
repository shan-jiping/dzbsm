# dzbsm
yum -y install epel-release
yum -y install python-pip mariadb-server mariadb-devel python-devel gcc gcc-c++ redis
systemctl start redis
systemctl enable redis
systemctl start mariadb
systemctl enable mariadb
mysql_secure_installation
create database dzbsm;
grant all on dzbsm.* to dzbsm@'%' identified by 'dzbsm_pass';
git clone https://github.com/shan-jiping/dzbsm.git
cd dzbsm
pip install -r req
mkdir logs

