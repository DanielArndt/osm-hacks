install_fzf() {
	git clone --depth 1 https://github.com/junegunn/fzf.git ~/.fzf
	~/.fzf/install
	export FZF_CTRL_T_OPTS="--preview='less {}'"
	echo "export FZF_CTRL_T_OPTS=\"--preview='less {}'\"" >> ~/.bashrc
}

install_rg() {
	curl -LO https://github.com/BurntSushi/ripgrep/releases/download/13.0.0/ripgrep_13.0.0_amd64.deb
	sudo dpkg -i ripgrep_13.0.0_amd64.deb
}

install_fzf
install_rg
