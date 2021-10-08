
clean:
	rm rrey-ganeti-*.tar.gz
build: clean
	ansible-galaxy collection build

publish: build
	ansible-galaxy collection publish ./rrey-ganeti-*.tar.gz  --token $GALAXY_TOKEN
