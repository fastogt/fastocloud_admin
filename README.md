# fastocloud_admin
Admin panel for ![FastoCloud](https://github.com/fastogt/fastocloud) IPTV part

### Our IPTV workflow:
![](https://fastocloud.com/static/images/iptv_workflow.png)

### Dashboard page:
![](https://fastocloud.com/static/images/dashboard.png)

#### Note: Every channel take about 1% CPU.

### Requirements
<ul>
<li>MongoDB server</li>
</ul>

### Build
Steps:
apt-get install python3 python3-setuptools git pip3 mongodb
git clone https://github.com/fastogt/fastocloud_admin
cd fastocloud_admin
git submodule update --init --recursive
`pip3 install -r requirements.txt`
./server.py &
Create user: ./scripts/create_provider.py --email=youremail@yourdomain --password=yourpassword
browser to http://<server IP>:8080
user: youremail@yourdomain
password: yourpassword

### Docker
[Docker](https://hub.docker.com/r/fastogt/fastocloud_admin)

### Test server
[FastoCloud](https://fastocloud.com)
