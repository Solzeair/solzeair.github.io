---
title: "Qt"
date: 2025-06-18
draft: false
tags: ["Qt", "C++"]
categories: ["编程"]
---

# Qt

## 信号与槽
- connect
	- 使用规则
		- 一个信号可以连接多个槽函数，多个信号可以连接同一个槽函数
		- 一个信号可以连接另一个信号
		- 信号的参数不能少于槽的参数
		- 在使用信号与槽的类中,必须在类的定义中插入宏Q_OBJECT
		- 信号被发射时,与其关联的槽函数被立即运行。只有当信号关联的所有槽函数运行完毕后,才运行后面的代码
	- 形式
		- 旧语法省略：connect (sender, SIGNAL (signal () ), receiver, SLOT (slot() ) ) ;
		- connect (lineEdit, &QLineEdit: : textChanged, this, &Widget: :do_textChanged);
		- 有多个同名槽使用模板，信号自动匹配槽
			- connect (ui->checkBox, QOverload<bool>::of(&QCheckBox::clicked), this, qOverload<bool> (&Widget :: do_click) );

## 对象树

## QWidget
界面组件
- 按键类
	- QAbstractButton抽象类
		- QPushButton普通按钮
			- QCommandLinkButton单选互斥按钮
		- QToolButton工具按钮
		- QRadioButton单选按钮
		- QCheckBox复选框
	- QDialogButtonBox复合组件类（ok/cancel）
- 输入类
	- QComboBox下拉列表框
		- QFontComboBox自动系统字体下拉列表框
	- QLineLdit编辑框，输入单行文字
	- QFrame
		- QAbstractSeroliArea
			- QTextEdit输入多行富文本（HTML / 图文）
			- QPlainTextEdit输入多行纯文本
	- QAbstractSpinBox
		- QSpinBox输入整数
		- QDoubleSpinBox输入浮点数的
		- QDateTimeEdit编辑日期时间
			- QDateEdit编辑日期
			- QTimeEdit编辑时间
	- QAbstractSlider
		- QDial模拟表盘
		- QScrollBar拖动卷滚条显示部分区域
			- Horizontal Scroll Bar
			- Vertical Scroll Bar
		- QSlider拖动滑块设置输入的值
			- Horizontal Slider
			- Vertical Slider
	- QKeySequenceEdit按键序列编辑器，获取用户设置的快捷键序列
- 显示类
	- QFrame
		- QLabel显示文字、图片
		- QAbstractScrollArea
			- QTextEdit
				- QTextBrowser显示只读富文本
			- QGraphics View图形视图组件
		- QLCDNumber模仿LCD显示效果的数值显示组件，可显示整数和浮点数
	- QCalendarWidget显示日历，选择一个日期可以作为输入组件
	- QProgressBar表示某个操作的进度，百分数表示，水平和竖直
	- QOpenGLWidget显示OpenGL图形
	- QQuickWidget自动加载QML文件并显示
	- Line分隔线
		- Horizontal Line
		- Vertical Line
- 容器类
	- QWidget界面组件，可以作为容器组件
	- QGroupBox分组框，具有标题和边框
	- QFrame
		- 框架组件，定义了边框形状、边框阴影、边框线宽等属性
		- QAbstractScroll Area
			- QScrollArea具有卷滚条的容器，可实现显示范围移动
			- QMdiArea管理多文档窗口
		- QToolBox垂直方向的多页容器,每个页面有标签栏,每个页面就是一个QWidget组件
		- QStackedWidget类似于QTabWidget的多页组件,但是没有标签栏,只有两个按钮,用于在页面之间切换
	- QTabWidget带标签栏的多页组件，每个页面就是一个QWidget组件
	- QDockWidget可以在QMainWindow 窗口的上、下、左、右区域停靠的组件，也可以浮动在窗口上方
- QspacerItem弹簧
	- Horizontal Spacer
	- Vertical Spacer
- QAbstractItem View
(Item Views and Item Widgets)
	- QListView
		- QUndoView
		- QListWidget
	- QTree View
		- QTreeWidget
	- QTable View
		- QTableWidget
	- QColumn View
