build: compile clean-all
	
compile:	
	python setup.py bdist_wheel

clean-all:
	rm -rf ./build ./*.egg-info