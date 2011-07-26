all:
	pyrcc4 -py3 -o hypernucleus/view/icons.py hypernucleus/view/icons.qrc
clean:
	rm -rf ~/.config/hypernucleus
