apt-get install network-manager -y
service NetworkManager restart
nmcli connection delete LTEConnection
nmcli connection add type gsm ifname usb0 con-name LTEConnection apn airtelnet.es
nmcli connection modify LTEConnection gsm.username vodafone
nmcli connection modify LTEConnection gsm.password vodafone
nmcli connection modify LTEConnection connection.autoconnect yes
nmcli connection up LTEConnection --ask
nmcli connection show
nmcli device status