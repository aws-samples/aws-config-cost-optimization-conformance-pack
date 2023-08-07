SHELL := /bin/bash

.PHONY : clean build package

clean:
	rm -f functions/*-pkg.py
	rm -f *-build.yaml
	rm -f *-pkg.yaml

build:
	python3 ./build/config_function.py
	python3 ./build/conformance_pack.py
	python3 ./build/template.py

package:
	rain pkg stackset.yaml --output stackset-pkg.yaml
	rain pkg template-build.yaml --output main.yaml
