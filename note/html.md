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
| head        | `<link type="text/css" rel="stylesheet" href="**.css"/>`     | 导入css文件                                                  |
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
|             |                                                              |                                                              |
|             |                                                              |                                                              |
|             |                                                              |                                                              |
|             |                                                              |                                                              |
|             |                                                              |                                                              |
|             |                                                              |                                                              |
|             |                                                              |                                                              |
|             |                                                              |                                                              |
|             |                                                              |                                                              |
|             |                                                              |                                                              |
|             |                                                              |                                                              |
|             |                                                              |                                                              |
|             |                                                              |                                                              |
|             |                                                              |                                                              |
|             |                                                              |                                                              |

## 二、标签属性

可以通过`class=""`来给标签添加属性

## 三、javascript

函数采用小驼峰命名法

```javascript
function funcName() {
    window.alert("警告");
}
```

