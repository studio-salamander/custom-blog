# Custom-blog
Example of web application (custom blog), created by using Python 3.6 + Flask microframework + sqlite
定制博客，Web应用示例，基于Python3.6 + Flask微框架 + sqlite 创建
# Installation
Install the requirements package:
安装需要的软件包：

    pip install -r requirements.txt

The sqlite database must be created before the application can run, and the db_create.py script takes care of that.
运行应用之前必须先创建sqlite数据库，db_create.py脚本负责这一部分。

    python db_create.py

# Running
To run the application in the development web server just execute run.py (debug=True) or runp.py (debug=False) with the Python interpreter from the flask virtual environment.
要运行一个用于开发的Web服务器，只要执行run.py(debug=True)就可以了 或者 runp.py(debug=False)采用的是flask虚拟环境的python解释器。

    python run.py
