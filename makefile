build: compile clean-all
	
compile:	
	python3 setup.py bdist_wheel

clean-all:
	rm -rf ./build ./*.egg-info