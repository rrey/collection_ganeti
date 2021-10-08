
clean:
	rm rrey-ganeti-*.tar.gz
build: clean
	ansible-galaxy collection build

publish: build
	ansible-galaxy collection publish ./rrey-ganeti-*.tar.gz  --token 3a732db34a159b73863a7a81f657c44df0b18a98
