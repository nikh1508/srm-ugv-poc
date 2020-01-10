# SRM UGV

	 .d8888b.    8888888b.    888b     d888            888     888    .d8888b.   888     888
	d88P  Y88b   888   Y88b   8888b   d8888            888     888   d88P  Y88b  888     888
	Y88b.        888    888   88888b.d88888            888     888   888    888  888     888
	 "Y888b.     888   d88P   888Y88888P888            888     888   888         Y88b   d88P
	    "Y88b.   8888888P"    888 Y888P 888   888888   888     888   888  88888   Y88b d88P
	      "888   888 T88b     888  Y8P  888            888     888   888    888    Y88o88P
	Y88b  d88P   888  T88b    888   "   888            Y88b. .d88P   Y88b  d88P     Y888P
	 "Y8888P"    888   T88b   888       888             "Y88888P"     "Y8888P88      Y8P



## Repository Info

---

This project follows monorepo approach and thus all independent codebases are maintained in this repo itself. Role of each codebase in this monorepo : 

| Directory       | Role                                                         |
| :-------------- | ------------------------------------------------------------ |
| motion-control  | controlling motors and other electronics \| MCU              |
| motion-planning | main control algorithm and motion planning \| SBC            |
| server          | hadling api requests and hosting client-side web page \| SBC |

