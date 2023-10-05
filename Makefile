SHELL := /bin/bash

.PHONY : clean build package

clean:
	rm -f functions/*-pkg.py
	rm -f *-build.yaml
	rm -f *-pkg.yaml
	rm main.yaml

build:
	python3 ./build/config_function.py
	python3 ./build/conformance_pack.py
	python3 ./build/stackset.py
	python3 ./build/template.py

package:
	rain pkg stackset-build.yaml --output stackset-pkg.yaml
	rain pkg template-build.yaml --output main.yaml
