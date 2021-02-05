#!make

init:
	pip3 install -r requirements.txt

config:
	sed -i 's|ExecStart=.*|ExecStart=python ${PWD}/apodwallpaper.py|g' apodwallpaper.service

.ONESHELL:
setup:
	sudo cp apodwallpaper.service /etc/systemd/user/
	sudo chmod 644 /etc/systemd/user/apodwallpaper.service
	systemctl --user daemon-reload
	systemctl --user enable apodwallpaper.service

run:
	python apodwallpaper.py

.PHONY: init, config, setup, run
