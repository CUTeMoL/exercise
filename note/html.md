# html

## 一、标签

标签有单标签<label/>，也有双标签<label></label>

标签可以添加属性<label attr="value"></label>

| 位置        | 标签                                                         | 涵义                                                         |
| ----------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
|             | `<!-- HTML注释 -->`                                          | 插入注释                                                     |
|             | `<!DOCTYPE html>`                                            | 声明这个一个html格式的文本                                   |
|             | `<html lang="en"></html>`                                    | 声明语言为英语                                               |
| html        | `<head></head>`                                              | 格式内容定义                                                 |
| head        | `<title></title>`                                            | 定义标题的名称                                               |
| head        | `<meta charset="UTF-8">`                                     | 定义文本的编码                                               |
| head        | `<meta name="keywords" content="关键字"/>`                   | 定义页面的关键字                                             |
| head        | `<meta name="Description" content="简介"/>`                  | 简介                                                         |
| head        | `<link type="text/css" rel="stylesheet" href="./my.css"/>`   | 引用/导入css文件                                             |
| head        | `<style type="text/css">label {}</style>`                    | 定义渲染类型为CSS层叠样式表,中间定义显示效果                 |
| html        | `<body></body>`                                              | 主题内容                                                     |
| body        | `<h1></h1>`                                                  | 标题,一共6级                                                 |
| body        | `<hr/>`                                                      | 水平分割线                                                   |
| body        | `<br/>`                                                      | 换行                                                         |
| body        | `<p></p>`                                                    | 段落                                                         |
| body        | `<button></button>`                                          | 按钮                                                         |
| body        | `<script type="text/javascript"></script>`                   | javascript脚本                                               |
| body        | `<a href="http://www.baidu.com" target="_blank" >link</a>`   | 超链接(另外可选则加#跳转锚点)<br/>target可以指定打开链接的方式<br/>`_blank`打开新窗口,`_parent`父窗口,`_self`本窗口(默认),`_top`顶级窗口,`framename`窗口名, |
|             | `<a id="锚点"></a>`                                          | 锚点,使用时为`#锚点id`                                       |
|             |                                                              |                                                              |
| body        | `<i></i>`                                                    | 斜体                                                         |
| body        | `<em></em>`                                                  | 强调斜体                                                     |
| body        | `<b></b>`                                                    | 加粗                                                         |
| body        | `<strong></strong>`                                          | 强调加粗                                                     |
| body        | `<cite></cite>`                                              | 作品的标题(引用)                                             |
| body        | `<sub></sub>`                                                | 下标                                                         |
| body        | `<sup></sup>`                                                | 上标                                                         |
| body        | `<del></del>`                                                | 删除线                                                       |
| body        | `<u></u>`                                                    | 下划线                                                       |
| body        | `<ul type="circle"></ul>`                                    | 无序列表,type指定列表项前缀                                  |
| body        | `<ol type="1"></ol>`                                         | 有序列表,type指定列表项前缀                                  |
| ul/ol       | `<li></li>`                                                  | 列表项                                                       |
| body        | `<dl></dl>`                                                  | 自定义列表(含有缩进)                                         |
| dl          | `<dt></dt>`                                                  | 自定义列表头                                                 |
| dl          | `<dd></dd>`                                                  | 自定义列表内容                                               |
| body        | `<div></div>`                                                | 常用于组合块级元素，以便通过CSS来对这些元素进行格式化，可以理解为高度0,宽度拉满的块 |
| body        | `<span></span>`                                              | 常用于包含的文本，您可以使用CSS对他定义演示，或者javascript对它尽行操作 |
| body        | `<img src="./images/1.jpg" alt="图片名称" width="200" border="1" />` | 图片标签<br/>src图片路径<br/>alt图片名称(加载失败时提示)<br/>width图片宽度,height指定高度(通常指定宽度即可,会自动等比例缩放)<br/>title鼠标停留时显示的名称<br/>border边框 |
| body        | `<table border="" width="" cellspacing="" cellpadding=""></table>` | 表格标签<br/>border边框<br/>width宽度<br/>cellspacing单元格间距<br/>cellpadding字与边框的距离<br/> |
| table       | `<caption></caption>`                                        | 表格标题                                                     |
| thead/tbody | `<tr></tr>`                                                  | 行标签                                                       |
| tr          | `<th></th>`                                                  | 列头标签(对比td加粗)                                         |
| tr          | `<td rowspan="2" align="center" valign="top"></td>`          | 列标签<br/>rowspan跨行,上覆盖下<br/>colspan跨列,左覆盖右<br/>align文本左右对齐方式显示<br/>valign文本上下对齐方式显示 |
| table       | `<thead></thead>`                                            | 表头                                                         |
| table       | `<tbody></tbody>`                                            | 表体                                                         |
| table       | `<tfoot></tfoot>`                                            | 表尾                                                         |
| body        | `<form action="h2.html" method="get"></form>`                | 表单标签<br/>action跳转页面<br/>method获取方式               |
| form        | `<input type="text" name="uname"></input>`                   | 输入表单项<br/>type为输入框类型<br/>text明文输入<br/>password密文输入<br/>submit提交框,此时可以再定义value=""对提交框进行定义<br/>radio单选,checked可以默认选中<br/>checkbox多选,checked可以默认选中<br/>search 指定为可输入下拉选择框,需要再用list定义链接的datalist的id<br/>reset重置按钮<br/>name表单命名，提交时表单项变成参数 |
| form        | `<select name="下拉选择" id=""></select>`                    | 下拉选择表单项                                               |
| select      | `<option value="" selected></option>`                        | 定义下拉的选项<br/>selected为默认值                          |
| form        | `<textarea rows="10" cols="100" name="contents"></textarea>` | 多行文本输入区域                                             |
| form        | `<fieldset></fieldset>`                                      | 元素可将表单内的相关元素分组                                 |
| form        | `<legend></legend>`                                          | 标签为`<fieldset>`、`<figure>`以及`<details>`元素定义标题    |
| form        | `<datalist id="namelist" ></datalist>`                       | 标签定义可选数据的列表,类似下拉框,但是可以搜索               |
| form        | `<optgroup><optgroup>`                                       | 标签定义选项组（即可以先分组再从组中挑选）                   |
| optgroup    | `<option value="">`                                          | 可以插入到datalist/optgroup的选项                            |
| body        | `<iframe src="a.html" name="aiframe" frameborder="1"  width="80%" height="500">` | 页面内嵌入一个子页面                                         |
| body        | `<audio src="" controls></audio>`                            | 音频标签<br/>controls用户控制                                |
| audio       | `<source src="" type="audio/mpeg">`                          | 如果audio没定义src可以用source定义                           |
| body        | `<video src="" controls="controls" width="400" height="300" poster=""></video>` | 视频标签<br/>poster可以定义封面                              |
|             |                                                              |                                                              |
|             |                                                              |                                                              |
|             |                                                              |                                                              |

## 二、CSS层叠样式表

样式定义如何显示控制HTML元素,从而实现梅花HTML网页,多个样式定义可层叠为一,后者可以覆盖前者的样式

### 1.格式:

```css
/*注释内容*/
selector {propery: value; property: value}
/* selector可以是标签 */
/* selector可以是*,代表所有标签 */
```

### 2.引用方式:

(1)外部样式表

```html
<head>
    <link type="text/css" rel="stylesheet" href="./my.css"/>
    <!-- 导入同级目录下的css文件 -->
</head>
```

(2)内部样式表

```html
<style>
	selector {propery:value;property:value}
    <!-- 内部定义 -->
</style>
```

(3)内联样式

```html
<label style="propery:value"></label>
<!-- 内联样式 -->
```

优先级:内联>(内部样式表or外部样式表)

内部样式表、外部样式表为后覆盖前

### 3.常用选择器

(1)HTML标签

(2)class

定义class

```html
<label class="className1 className2">
</label>
```

渲染class

```css
/* 所有标签中含className */
.className{propery:value}
/* html标签中含className */
html.className{propery:value}
```

(3)id

定义id

```html
<label id="idName">
</label>
```

渲染id

```
/* 所有标签中含idName */
#idName{propery:value}
```

优先级[ID]>[CLASS]>[HTML标签]

(4)关联选择器

```css
/* label1标签中的label2标签(递归) */
label1 label2{propery:value}
/* label1标签中的label2标签(不递归) */
label1 > label2{propery:value}
/* label1标签后的紧邻的label2标签(仅一个) */
label1+label2{propery:value}
/* label1标签后的label2标签(所有) */
label1~label2{propery:value}
```

(5)选择器组

```css
/* label1,label2标签都 */
label1,label2{propery:value}
```

(6)伪类选择器

```css
/* 未访问 */
a:link{propery:value}
/* 已访问 */
a:visited{propery:value}
/* 鼠标在链接上 */
a:hover{propery:value}
/* 激活链接 */
a:active{propery:value}
```

4.常用属性

尺寸:"%"百分比、"px"像素、"em"当前字体的尺寸

颜色color:"red"英文单词、"#rrggbb"十六进制数、"rgb(x,x,x)"RGB数值

| 类型 | 属性                  | 说明                                                         |
| ---- | --------------------- | ------------------------------------------------------------ |
| 字体 | `font-size`           | 字体大小,单位参照尺寸                                        |
| 字体 | `font-family`         | 字体                                                         |
| 字体 | `font-weight`         | 加粗,默认400,通常加粗700                                     |
| 字体 | `font-style`          | `normal`正常,`italic`斜体,`oblique`倾斜字体                  |
| 文本 | `text-indent`         | 首行缩进                                                     |
| 文本 | `text-overflow`       | 溢出是否省略                                                 |
| 文本 | `text-align`          | 文本位置`left`,`center`,`right`                              |
| 文本 | `text-decoration`     | 字体划线,`none`,`underline`,`line-through`                   |
| 文本 | `text-shadow`         | 文本文字阴影                                                 |
| 文本 | `vertical-align`      | 文本的垂直对齐方式                                           |
| 文本 | `letter-spacing`      | 文字或字母间距                                               |
| 文本 | `line-height`         | 行高                                                         |
| 文本 | `color`               | 字体颜色                                                     |
| 文本 | `white-space:nowrap`  | 强制显示在同一行                                             |
| 背景 | `background-color`    | 背景颜色                                                     |
| 背景 | `background-image`    | 背景图片<br/>url(路径)指定图片地址<br/>repeating-linear-gradient(to right,red,black)渐变色 |
| 背景 | `background-repeat`   | 重复方式`no-repeat`不平铺,`repeat`全平铺,`repeat-x`X轴平铺,`repeat-y`y轴平铺 |
| 背景 | `background-position` | 定位 x轴 y轴                                                 |
| 背景 | `background-size`     | 背景大小                                                     |
|      |                       |                                                              |
|      |                       |                                                              |
|      |                       |                                                              |
|      |                       |                                                              |
|      |                       |                                                              |
|      |                       |                                                              |
|      |                       |                                                              |
|      |                       |                                                              |
|      |                       |                                                              |
|      |                       |                                                              |
|      |                       |                                                              |
|      |                       |                                                              |
|      |                       |                                                              |
|      |                       |                                                              |
|      |                       |                                                              |
|      |                       |                                                              |
|      |                       |                                                              |
|      |                       |                                                              |
|      |                       |                                                              |
|      |                       |                                                              |
|      |                       |                                                              |
|      |                       |                                                              |
|      |                       |                                                              |
|      |                       |                                                              |
|      |                       |                                                              |
|      |                       |                                                              |
|      |                       |                                                              |
|      |                       |                                                              |
|      |                       |                                                              |
|      |                       |                                                              |



## 三、JavaScript

函数采用小驼峰命名法

```javascript
function funcName() {
    window.alert("警告");
}
```

